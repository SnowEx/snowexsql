from sqlalchemy import orm

# Global variable to manage sessions to the database
SESSION = orm.scoped_session(orm.sessionmaker())
