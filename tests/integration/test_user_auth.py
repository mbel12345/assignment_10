import pytest

from app.models.user import User

def test_password_hashing(fake_user_data):

    # Test that login check can work

    original_password = 'TestPass123' # Known password
    hashed = User.hash_password(original_password)

    user = User(
        first_name = fake_user_data['first_name'],
        last_name=fake_user_data['last_name'],
        email=fake_user_data['email'],
        username=fake_user_data['username'],
        password_hash=hashed,
    )
    assert user.verify_password(original_password) is True
    assert user.verify_password('WrongPass123') is False
    assert hashed != original_password

def test_user_registration(db_session, fake_user_data):

    # Test user registration process

    fake_user_data['password'] = 'TestPass123'

    user = User.register(db_session, fake_user_data)
    db_session.commit()

    assert user.first_name == fake_user_data['first_name']
    assert user.last_name == fake_user_data['last_name']
    assert user.email == fake_user_data['email']
    assert user.username == fake_user_data['username']
    assert user.is_active is True
    assert user.is_verified is False
    assert user.verify_password('TestPass123') is True

def test_duplicate_user_registration(db_session):

    # Test registration with duplicate email/username

    # User 1
    user1_data = {
        'first_name': 'Test',
        'last_name': 'User1',
        'email': 'unique.test@example.com',
        'username': 'uniqueuser1',
        'password': 'TestPass123',
    }

    # User 2
    user2_data = {
        'first_name': 'Test',
        'last_name': 'User2',
        'email': 'unique.test@example.com',
        'username': 'uniqueuser2',
        'password': 'TestPass123',
    }

    # Register first user
    first_user = User.register(db_session, user1_data)
    db_session.commit()
    db_session.refresh(first_user)

    # Try to register second user (duplicate email)
    with pytest.raises(ValueError, match='Username or email already exists'):
        User.register(db_session, user2_data)

def test_user_authentication(db_session, fake_user_data):

    # Test user authentication and token generation

    fake_user_data['password'] = 'TestPass123'
    User.register(db_session, fake_user_data)
    db_session.commit()

    # Test successful authentication
    auth_result = User.authenticate(
        db_session,
        fake_user_data['username'],
        'TestPass123',
    )

    assert auth_result is not None
    assert 'access_token' in auth_result
    assert 'token_type' in auth_result
    assert auth_result['token_type'] == 'bearer'
    assert 'user' in auth_result

def test_user_last_login_update(db_session, fake_user_data):

    # Test that last_login is updated on authentication

    fake_user_data['password'] = 'TestPass123'
    user = User.register(db_session, fake_user_data)
    db_session.commit()

    assert user.last_login is None
    User.authenticate(db_session, fake_user_data['username'], 'TestPass123')
    db_session.refresh(user)
    assert user.last_login is not None

def test_unique_email_username(db_session):

    # Test uniqueness constraints for email and username

    # User 1
    user1_data = {
        'first_name': 'Test',
        'last_name': 'User1',
        'email': 'unique_test@example.com',
        'username': 'uniqueuser',
        'password': 'TestPass123',
    }

    # Register first user
    User.register(db_session, user1_data)
    db_session.commit()

    # Try to create user with the same email
    user2_data = {
        'first_name': 'Test',
        'last_name': 'User2',
        'email': 'unique_test@example.com',
        'username': 'differentuser',
        'password': 'TestPass123',
    }

    with pytest.raises(ValueError, match='Username or email already exists'):
        User.register(db_session, user2_data)

def test_short_password_registration(db_session):

    # Test that registration fails for a short password

    test_data = {
        'first_name': 'Password',
        'last_name': 'Test',
        'email': 'short.pass@exmaple.com',
        'username': 'shortpass',
        'password': 'Shor5',
    }

    with pytest.raises(ValueError, match='Password must be at least 6 characters long'):
        User.register(db_session, test_data)

def test_invalid_token():

    # Test that invalid tokens are rejected

    invalid_token = 'invalid.token.string'
    result = User.verify_token(invalid_token)
    assert result is None

def test_token_creation_and_verification(db_session, fake_user_data):

    # Test token creation and verification

    fake_user_data['password'] = 'TestPass123'
    user = User.register(db_session, fake_user_data)
    db_session.commit()

    # Create token
    token = User.create_access_token({'sub': str(user.id)})

    # Verify token
    decoded_user_id = User.verify_token(token)
    assert decoded_user_id == user.id

def test_authenticate_with_email(db_session, fake_user_data):

    # Test authentication using email

    fake_user_data['password'] = 'TestPass123'
    User.register(db_session, fake_user_data)
    db_session.commit()

    auth_result = User.authenticate(
        db_session,
        fake_user_data['email'],
        'TestPass123',
    )

    assert auth_result is not None
    assert 'access_token' in auth_result

def test_usre_model_representation(test_user):

    # Test the str representation of User model

    expected = f'<User(name={test_user.first_name} {test_user.last_name}, email={test_user.email})>'
    assert str(test_user) == expected

def test_missing_password_registration(db_session):

    # Test that registration fails when no password is given

    test_data = {
        'first_name': 'NoPassword',
        'last_name': 'Test',
        'email': 'no.password@example.com',
        'username': 'nopassworduser',
        # Password is missing
    }

    with pytest.raises(ValueError, match='Password must be at least 6 characters long'):
        User.register(db_session, test_data)
