import logging
import pytest

from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from unittest.mock import patch

from app.models.user import User
from tests.conftest import create_fake_user
from tests.conftest import managed_db_session

# Set up logging
logger = logging.getLogger(__name__)

def test_database_connection(db_session):

    # Check that a database connection can be made.

    result = db_session.execute(text('SELECT 1'))
    assert result.scalar() == 1
    logger.info('Database connection test passed')

def test_managed_session():

    # Test the managed_db_session context manager.

    with managed_db_session() as session:

        session.execute(text('SELECT 1'))
        try:
            session.execute(text('SELECT * FROM nonexistent_table'))
        except Exception as e:
            assert 'nonexistent_table' in str(e)

def test_session_handling(db_session):

    # Test partial commits

    initial_count = db_session.query(User).count()
    logger.info(f'Initial user count before test_session_handling: {initial_count}')
    assert initial_count == 0, f'Expected 0 users before test, found {initial_count}'

    user1 = User(
        first_name='Test',
        last_name='User',
        email='test1@example.com',
        username='testuser1',
        password='password123',
    )
    db_session.add(user1)
    db_session.commit()
    logger.info(f'Added user1: {user1.email}')

    current_count = db_session.query(User).count()
    logger.info(f'User count after adding user1: {current_count}')
    assert current_count == 1, f'Expected 1 user after adding user1, found {current_count}'

    # Try creating a user with an already-used email
    try:
        user2 = User(
            first_name='Test',
            last_name='User',
            email='test1@example.com',
            username='testuser2',
            password='password456',
        )
        db_session.add(user2)
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
        logger.info('IntegrityError caught and rolled back for user2.')

    found_user1 = db_session.query(User).filter_by(email='test1@example.com').first()
    assert found_user1 is not None, 'User1 should still exist after rollback'
    assert found_user1.username == 'testuser1'
    logger.info(f'Found user1 after rollback: {found_user1.email}')

    # Add another user
    user3 = User(
        first_name='Test',
        last_name='User',
        email='test3@example.com',
        username='testuser3',
        password='password789',
    )
    db_session.add(user3)
    db_session.commit()
    logger.info(f'Added user3: {user3.email}')

    users = db_session.query(User).order_by(User.email).all()
    current_count = len(users)
    emails = {user.email for user in users}
    logger.info(f'Final user count: {current_count}, Emails: {emails}')

    assert current_count == 2, f'Should have exactly user1 and user3, found {current_count}'
    assert 'test1@example.com' in emails, 'User1 must remain'
    assert 'test3@example.com' in emails, 'User3 must exist'

def test_create_user_with_faker(db_session):

    # Create a User using Faker-generated data and verify it was saved

    user_data = create_fake_user()
    logger.info(f'Creating user with data: {user_data}')

    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.email == user_data['email']
    logger.info(f'Successfully created user with ID: {user.id}')

def test_create_multiple_users(db_session):

    # Create users in a loop and verify they are all saved

    users = []
    for _ in range(3):
        user_data = create_fake_user()
        user = User(**user_data)
        users.append(user)
        db_session.add(user)

    db_session.commit()
    assert len(users) == 3
    logger.info(f'Successfully created {len(users)} users')

def test_query_methods(db_session, seed_users):

    '''
    Demonstrate various various query methods
    - Counting users
    - Filterin by email
    - Ordering by email
    '''

    user_count = db_session.query(User).count()
    assert user_count >= len(seed_users), 'The user table should have at least the seeded users'

    first_user = seed_users[0]
    found = db_session.query(User).filter_by(email=first_user.email).first()
    assert found is not None, 'Should ifnd the seeded user by email'

    users_by_email = db_session.query(User).order_by(User.email).all()
    assert len(users_by_email) >= len(seed_users), 'Query should return at least the seeded users'

def test_transaction_rollback(db_session):

    # Demonstrate how a partial transaction fails and triggers rollback.

    initial_count = db_session.query(User).count()

    try:
        user_data = create_fake_user()
        user = User(**user_data)
        db_session.add(user)
        db_session.execute(text('SELECT * FROM nonexistent_table'))
        db_session.commit()
    except Exception:
        db_session.rollback()

    final_count = db_session.query(User).count()
    assert final_count == initial_count, 'The new user should not have been committed'

def test_update_with_refresh(db_session, test_user):

    # Update user's email

    original_email = test_user.email
    original_update_time = test_user.updated_at

    new_email = f'new_{original_email}'
    test_user.email = new_email
    db_session.commit()
    db_session.refresh(test_user)

    assert test_user.email == new_email, 'Email should have been updated'
    assert test_user.updated_at > original_update_time, 'Updated time should be newer'
    logger.info(f'Successfully updated user {test_user.id}')

@pytest.mark.slow
def test_bulk_operation(db_session):

    # Test bulk inserting multiple users

    users_data = [create_fake_user() for _ in range(10)]
    users = [User(**data) for data in users_data]
    db_session.bulk_save_objects(users)
    db_session.commit()

    count = db_session.query(User).count()
    assert count >= 10, 'At least 10 users should now be in the database'
    logger.info(f'Successfully performed bulk operation with {len(users)} users')

def test_unique_email_constraint(db_session):

    # Create two users  with the same email and check that an IntegrityError is raised

    first_user_data = create_fake_user()
    first_user = User(**first_user_data)
    db_session.add(first_user)
    db_session.commit()

    second_user_data = create_fake_user()
    second_user_data['email'] = first_user_data['email']
    second_user = User(**second_user_data)
    db_session.add(second_user)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_unique_username_constraint(db_session):

    # Create two users with the same username and check that an IntegrityError is raised
    first_user_data = create_fake_user()
    first_user = User(**first_user_data)
    db_session.add(first_user)
    db_session.commit()

    second_user_data = create_fake_user()
    second_user_data['username'] = first_user_data['username']
    second_user = User(**second_user_data)
    db_session.add(second_user)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_user_persistence_after_constraint(db_session):

    '''
    - Create and commit a valid user
    - Attempt to create a user with the same email -> fails
    - Confirm the original user still exists
    '''

    initial_user_data = {
        'first_name': 'First',
        'last_name': 'User',
        'email': 'first@example.com',
        'username': 'firstuser',
        'password': 'password123',
    }
    initial_user = User(** initial_user_data)
    db_session.add(initial_user)
    db_session.commit()
    saved_id = initial_user.id

    try:
        duplicate_user = User(
            first_name='Second',
            last_name='User',
            email='first@example.com',
            username='seconduser',
            password='password456',
        )
        db_session.add(duplicate_user)
        db_session.commit()
        assert False, 'Should have raised IntegrityError'
    except IntegrityError:
        db_session.rollback()

    found_user = db_session.query(User).filter_by(id=saved_id).first()
    assert found_user is not None, 'Original user should exist'
    assert found_user.id == saved_id, 'Should have original user by ID'
    assert found_user.email == 'first@example.com', 'Email should be unchanged'
    assert found_user.username == 'firstuser', 'Username should be unchanged'

def test_error_handling():

    # Verify that a manual managed_db_session can capture and log SQL errors

    with pytest.raises(Exception) as e:
        with managed_db_session() as session:
            session.execute(text('INVALID SQL'))
    assert 'INVALID SQL' in str(e.value)

def test_hash_password():

    # Test password hashing

    hashed = User.hash_password('password')
    assert hashed != 'password'
    assert len(hashed) >= 30

def test_unknown_registration_error(db_session):

    # Force a Validation Error during registration

    user_data = {
        'first_name': 'First',
        'last_name': 'User',
        'email': 'first@example.com',
        'username': 'firstuser',
        'password': 'password123',
    }

    err = ValidationError.from_exception_data(
        'UserCreate',
        [
            {
                'loc': ('password',),
                'msg': 'force error',
                'type': 'value_error',
                'input': None,
                'ctx': {'error': ValueError('force error')},
            },
        ],
    )
    with patch('app.schemas.base.UserCreate.model_validate', side_effect=err):
        with pytest.raises(ValueError, match='force error'):
            User.register(db_session, user_data)

def test_authenticate_no_matching_user(db_session):

    # Test that authentication returns None if there is no matching user

    assert User.authenticate(db_session, 'fake_user_12345', 'password') is None
