import psycopg2

from app.base import Base

def init_db(engine):

    Base.metadata.create_all(bind=engine)

def drop_db(engine):

    try:
        Base.metadata.drop_all(bind=engine)
    except psycopg2.OperationalError as e:
        print(f'Warning: {str(e)}')

if __name__ == '__main__':

    init_db() # pragma: no cover
