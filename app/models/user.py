import uuid

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy import Boolean, Column, DateTime, func, or_, String
from sqlalchemy.dialects.postgresql import UUID
from typing import Any, Dict, Optional

from app.base import Base
from app.config import settings
from app.schemas.base import UserCreate
from app.schemas.user import Token
from app.schemas.user import UserResponse

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class User(Base):

    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):

        return f'<User(name={self.first_name} {self.last_name}, email={self.email})>'

    @staticmethod
    def hash_password(password: str) -> str:

        # Hash password uing bcrypt

        return pwd_context.hash(password)

    def verify_password(self, plain_password: str) -> bool:

        # Verify a plain password against the hashed password

        return pwd_context.verify(plain_password, self.password_hash)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:

        # Create a JWT

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({'exp': expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[UUID]:

        # Verify and decode a JWT

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get('sub')
            return uuid.UUID(user_id) if user_id else None
        except (JWTError, ValueError):
            return None

    @classmethod
    def register(cls, db, user_data: Dict[str, Any]) -> "User":

        # Validate a new user and register it

        try:

            # Check password length
            password = user_data.get('password', '')
            if len(password) < 6:
                raise ValueError('Password must be at least 6 characters long')

            # Check if email/username already exists
            existing_user = db.query(cls).filter(
                or_(
                    cls.email == user_data.get('email'),
                    cls.username == user_data.get('username'),
                ),
            ).first()

            if existing_user:
                raise ValueError('Username or email already exists')

            # Validate the fields
            user_create = UserCreate.model_validate(user_data)

            # Instantiate the user
            new_user = cls(
                first_name=user_create.first_name,
                last_name=user_create.last_name,
                email=user_create.email,
                username=user_create.username,
                password_hash=cls.hash_password(user_create.password),
                is_active=True,
                is_verified=False,
            )
            db.add(new_user)
            db.flush()
            return new_user

        except ValidationError as e:

            raise ValueError(str(e))

        except ValueError as e:

            raise e

    @classmethod
    def authenticate(cls, db, username: str, password: str) -> Optional[Dict[str, Any]]:

        # Authenticate user and return token with the user data

        user = db.query(cls).filter(
            or_(
                cls.username == username,
                cls.email == username,
            )
        ).first()

        if not user or not user.verify_password(password):
            return None

        user.last_login = datetime.now(timezone.utc)
        db.commit()

        # Create token response
        user_response = UserResponse.model_validate(user)
        token_response = Token(
            access_token=cls.create_access_token({
                'sub': str(user.id),
            }),
            token_type='bearer',
            user=user_response,
        )

        return token_response.model_dump()
