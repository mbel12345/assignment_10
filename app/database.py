from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.config import settings

def get_engine(database_url: str = settings.DATABASE_URL):

    '''
    Create and return an SQLAlchemy engine.
    '''

    try:
        engine = create_engine(database_url, echo=True)
        return engine
    except SQLAlchemyError as e:
        print(f'Error creating engine: {e}')
        raise

def get_sessionmaker(engine):

    '''
    Create and return a sessionmaker
    '''

    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

# Initialize engine and SessionLocal
engine = get_engine()
SessionLocal = get_sessionmaker(engine)

def get_db():

    '''
    Dependency that provides a database session.

    Useful for being injected via FastAPI's dependency injection system (Depends).
    Provides a database session that routes can use.
    '''

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
