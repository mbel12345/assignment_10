import logging
import pytest

from contextlib import contextmanager
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Dict, Generator

from app.base import Base
from app.config import settings
from app.database import get_engine, get_sessionmaker

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname) - %(message)s'
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

    '''
    Create a dictionary of fake user data for testing.
    '''

    return {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.unique.email(),
        'username': fake.unique.user_name(),
        'password': fake.password(length=12),
    }

@contextmanager
def managed_db_session():

    '''
    Context manager that automatically handles rollback and cleanup.
    '''

    session = TestingSessionLocal()
    try:
        yield session
    except SQLAlchemyError as e:
        logger.error(f'Database error: {str(e)}')
        session.rollback()
        raise
    finally:
        session.close()

@pytest.fixture
def db_session(request) -> Generator[Session, None, None]:

    '''
    Provide a test database, which by default has its tables truncated after each test, unless --preserve-db is passed.
    '''

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

def pytest_addoption(parser):

    '''
    Add command line options
    --preserver-db
    '''

    parser.addoption(
        '--preserve-db',
        action='store_true',
        default=False,
        help='Keep test database after tests, and skip table truncation.',
    )
