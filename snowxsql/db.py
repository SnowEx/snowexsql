from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_session(db_str):
    '''
    Returns a session object
    '''
    # Start the Database
    engine = create_engine(db_str, echo=False)

    # create a Session
    Session = sessionmaker(bind=engine)
    return Session()
