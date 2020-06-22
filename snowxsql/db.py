from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData

def get_db(db_str):
    '''
    Returns a session object
    '''
    # create a Session
    engine = create_engine(db_str, echo=False)

    Session = sessionmaker(bind=engine)
    session = Session()
    metadata = MetaData(engine)
    # metadata.reflect(engine)
    session = Session(expire_on_commit=False)

    return engine, metadata, session
