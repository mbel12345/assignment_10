import logging

from sqlalchemy import text

# Set up logging
logger = logging.getLogger(__name__)

def test_database_connection(db_session):

    '''
    Check that a database connection can be made.
    '''

    result = db_session.execute(text('SELECT 1'))
    assert result.scalar() == 1
    logger.info('Database connection test passed')
