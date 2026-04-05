import logging
import pytest
import requests
import subprocess
import time

from contextlib import contextmanager
from faker import Faker
from playwright.sync_api import Browser, sync_playwright
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Dict, Generator, List

from app.base import Base
from app.config import settings
from app.database import get_engine, get_sessionmaker
from app.database_init import drop_db, init_db
from app.models.user import User

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration

fake = Faker()
Faker.seed(12345)

logger.info(f'Using database URL: {settings.DATABASE_URL}')

# Create DB engine and sessionmaker
test_engine = get_engine(database_url=settings.DATABASE_URL)
TestingSessionLocal = get_sessionmaker(engine=test_engine)

def create_fake_user() -> Dict[str, str]:

    # Create a dictionary of fake user data for testing.

    return {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.unique.email(),
        'username': fake.unique.user_name(),
        'password': fake.password(length=12),
    }

@contextmanager
def managed_db_session():

    # Context manager that automatically handles rollback and cleanup.

    session = TestingSessionLocal()
    try:
        yield session
    except SQLAlchemyError as e:
        logger.error(f'Database error: {str(e)}')
        session.rollback()
        raise
    finally:
        session.close()

@pytest.fixture(scope='session', autouse=True)
def setup_test_database(request):

    '''
    Initialize the test database once per session:
      - Drop all existing tables
      - Create all tables
      - Optinally initialize the database with seed data.
    After tests, drop all tables unless --preserve-db is set
    '''

    logger.info('Setting up test database...')

    drop_db(test_engine)
    logger.info('Dropped all existing tables.')

    init_db(test_engine)
    logger.info('Created all tables based on models.')

    yield

    preserve_db = request.config.getoption('--preserve-db')
    if preserve_db:
        logger.info('Skipping drop_db due to --preserve-db flag.')
    else:
        logger.info('Cleaning up test database...')
        drop_db(test_engine)
        logger.info('Dropped test database tables.')

@pytest.fixture
def db_session(request) -> Generator[Session, None, None]:

    # Provide a test database, which by default has its tables truncated after each test, unless --preserve-db is passed.

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        logger.info('db_session teardown: about to truncate tables.')
        preserve_db = request.config.getoption('--preserve-db')
        if preserve_db:
            logger.info('Skipping table truncation due to --preserve-db flag.')
        else:
            logger.info('Truncating all tables now.')
            for table in reversed(Base.metadata.sorted_tables):
                logger.info(f'Truncating table: {table}')
                session.execute(table.delete())
            session.commit()
            logger.info('db_session teardown: done.')
        session.close()

@pytest.fixture
def fake_user_data() -> Dict[str, str]:

    # Return a dictionary of fake user data

    return create_fake_user()

@pytest.fixture
def test_user(db_session: Session) -> User:

    # Create and return a test user

    user_data = create_fake_user()
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    logger.info(f'Created test user with ID: {user.id}')
    return user

@pytest.fixture
def seed_users(db_session: Session, request) -> List[User]:

    # Create multiple test users in the database

    try:
        num_users = request.param
    except AttributeError:
        num_users = 5

    users = []
    for _ in range(num_users):
        user_data = create_fake_user()
        user = User(**user_data)
        users.append(user)
        db_session.add(user)

    db_session.commit()
    logger.info(f'Seeded {len(users)} users into the test database')
    return users

'''
FastAPI fixtures
'''

class ServerStartupError(Exception):

    # Raised when the test server fails to start properly

    pass

def wait_for_server(url: str, timeout: int = 30) -> bool:

    # Wait for server to be ready, and raise an error if this never happens

    start_time = time.time()
    while (time.time() - start_time) < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    return False

@pytest.fixture(scope='session')
def fastapi_server():

    # Start and manage a FastAPI test server for integration tests

    server_url = 'http://127.0.0.1:8000/'
    logger.info('Starting test server...')

    try:
        process = subprocess.Popen(
            ['python', 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if not wait_for_server(server_url, timeout=30):
            raise ServerStartupError('Failed to start test server')

        logger.info('Test server started successfully.')
        yield

    except Exception as e:

        logger.error(f'Server error: {str(e)}')
        raise

    finally:

        logger.info('Terminating test server...')
        process.terminate()
        try:
            process.wait(timeout=5)
            logger.info('Test server terminated gracefully.')
        except subprocess.TimeoutExpired:
            logger.warning('Test server did not terminate in time; killing it.')
            process.kill()

@pytest.fixture(scope='session')
def browser_context():

    # Provide a Playwright browswer context for UI tests.

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage'],
        )
        logger.info('Pllaywright browser launched.')
        try:
            yield browser
        finally:
            logger.info('Closing Playwright browser.')
            browser.close()

@pytest.fixture
def page(browser_context: Browser):

    # Return a new browser page for each test

    context = browser_context.new_context(
        viewport={'width': 1920, 'height': 1080},
        ignore_https_errors=True,
    )
    page = context.new_page()
    logger.info('Created new browser page.')
    try:
        yield page
    finally:
        logger.info('Closing browser page and context.')
        page.close()
        context.close()

'''
Pytest options
'''

def pytest_addoption(parser):

    '''
    Add command line options
    --preserve-db
    '''

    parser.addoption(
        '--preserve-db',
        action='store_true',
        default=False,
        help='Keep test database after tests, and skip table truncation.',
    )
