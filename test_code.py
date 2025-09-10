from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.get_model import Base

# Example: postgres://username:password@localhost:5432/dbname

engine = create_engine(DATABASE_URL)

session = sessionmaker(autoflush=False, bind=engine)

def db_connect():
    db = session()
    try: 
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)
