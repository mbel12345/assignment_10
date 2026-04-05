import pytest

from pydantic import ValidationError

from app.schemas.base import PasswordMixin, UserBase, UserCreate, UserLogin

def test_user_base_valid():

    # Test UserBase with valid data

    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'username': 'johndoe',
    }
    user = UserBase(**data)
    assert user.first_name == 'John'
    assert user.email == 'john.doe@example.com'

def test_user_base_invalid_email():

    # Test Userbase with invalid email

    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'invalid-email',
        'username': 'johndoe',
    }

    with pytest.raises(ValidationError):
        UserBase(**data)

def test_password_mixin_valid():

    # Test valid password

    data = {'password': 'SecurePass123'}
    password_mixin = PasswordMixin(**data)
    assert password_mixin.password == 'SecurePass123'

def test_password_minx_invalid_short_password():

    # Test that short password is rejected

    data = {'password': 'short'}
    with pytest.raises(ValidationError):
        PasswordMixin(**data)

def test_password_mixin_no_uppercase():

    # Test that password with no uppercase chars is rejected

    data = {'password': 'lowercase1'}
    with pytest.raises(ValidationError, match='Password must contain at least one uppercase letter'):
        PasswordMixin(**data)

def test_password_mixin_no_lowercase():

    # Test that password with no lowercase chars is rejected

    data = {'password':  'UPPERCASE1'}
    with pytest.raises(ValidationError, match='Password must contain at least one lowercase letter'):
        PasswordMixin(**data)

def test_password_mixin_no_digit():

    # Test that password with no digits is rejected

    data = {'password': 'NoDigits'}
    with pytest.raises(ValidationError, match='Password must contain at least one digit'):
        PasswordMixin(**data)

def test_user_create_valid():

    # Test UserCreate with valid data

    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'username': 'johndoe',
        'password': 'SecurePass123',
    }
    user_create = UserCreate(**data)
    assert user_create.username == 'johndoe'
    assert user_create.password == 'SecurePass123'

def test_user_login_invalid_username():

    # Test UserLogin with short username

    data = {
        'username': 'jd',
        'password': 'SecurePass123',
    }
    with pytest.raises(ValidationError):
        UserLogin(**data)

def test_user_create_invalid_password():

    # Test UserLogin with invalid password

    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'username': 'johndoe',
        'password': 'short',
    }
    with pytest.raises(ValidationError):
        UserCreate(**data)

def test_user_login_valid():

    # Test UserLogin with valid data

    data = {
        'username': 'johndoe',
        'password': 'SecurePass123',
    }
    user_login = UserLogin(**data)
    assert user_login.username == 'johndoe'

def test_empty_password():

    data = {'password': ''}
    with pytest.raises(ValidationError, match='Password is required'):
        PasswordMixin(**data)
