from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()
DB_PASSWORD= os.getenv("our_password") 
USERNAME=os.getenv("our_user")
HOST=os.getenv("our_host")
PORT=int(os.getenv("our_port"))
DB=os.getenv("our_database")

# DATABASE_URL = f"mysql+pymysql://{USERNAME}:{DB_PASSWORD}@{HOST}:{PORT}/{DB}"
DATABASE_URL=os.getenv("DATABASE_URL")
SQLALCHEMY_DATABASE_URL = DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base = declarative_base()
