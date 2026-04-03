import importlib
import pytest
import sys

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock, patch

DATABASE_MODULE = 'app.database'

@pytest.fixture
def mock_settings(monkeypatch):

    #Override settings.DATABASE_URL so that the changes take effect before app.database is loaded

    mock_url = 'postgresql://user:password@localhost:5432/test_db'
    mock_settings = MagicMock()
    mock_settings.DATABASE_URL = mock_url
    if DATABASE_MODULE in sys.modules:
        del sys.modules[DATABASE_MODULE]
    monkeypatch.setattr(f'{DATABASE_MODULE}.settings', mock_settings)
    return mock_settings

def reload_database_module():

    # Reload the database module after patches.

    if DATABASE_MODULE in sys.modules:
        del sys.modules[DATABASE_MODULE]
    return importlib.import_module(DATABASE_MODULE)

def test_base_declaration(mock_settings):

    # Test that Base is in instnace of declarative_base.

    database = reload_database_module()
    assert isinstance(database.Base, database.declarative_base().__class__)

def test_get_engine_success(mock_settings):

    # Test that get_engine returns a valid engine.

    database = reload_database_module()
    engine = database.get_engine()
    assert isinstance(engine, Engine)

def test_get_engine_failure(mock_settings):

    # Test that get_engine raises an error if the engine cannot be created.

    database = reload_database_module()
    with patch('app.database.create_engine', side_effect=SQLAlchemyError('Engine error')):
        with pytest.raises(SQLAlchemyError, match='Engine error'):
            database.get_engine()

def test_get_sessionmaker(mock_settings):

    # Test that get_sessionmaker returns a valid sessionmaker.

    database = reload_database_module()
    engine = database.get_engine()
    SessionLocal = database.get_sessionmaker(engine)
    assert isinstance(SessionLocal, sessionmaker)

def test_get_db(mock_settings):

    # Test that get_db method works and can do a query

    database = reload_database_module()
    db_gen = database.get_db()
    db = next(db_gen)
    result = db.execute(text('SELECT 1'))
    assert result.scalar() == 1
