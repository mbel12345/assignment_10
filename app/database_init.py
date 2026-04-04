from app.base import Base

def init_db(engine):

    Base.metadata.create_all(bind=engine)

def drop_db(engine):

    Base.metadata.drop_all(bind=engine)

if __name__ == '__main__':

    init_db() # pragma: no cover
