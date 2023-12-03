
# import psycopg2
from .models import Orders, create_tables
from .db_loader import engine, Base, db_session

class DatabaseManager(object):
    engine = None
    Base = None
    db_session = None
    
    def __init__(self) -> None:
        self.Base = Base
        self.engine = engine
        self.db_session = db_session

    def createTables(self):
        create_tables()

    def delete_orders(self):
        self.db_session.query(Orders).delete()
        self.db_session.commit()
    

if __name__ == "__main__":
    db = DatabaseManager()
    db.create_order()
