from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.get_model import Base

DATABASE_URL = "sqlite:///./test.db"

engine =create_engine(DATABASE_URL,connect_args={"check_same_thread":False})


session = sessionmaker(autoflush=False,bind=engine)

def db_connect():
    db = session()
    try: 
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)
