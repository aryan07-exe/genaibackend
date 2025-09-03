from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
load_dotenv()


DB_USER = "aryan"
DB_PASSWORD = "Sahu@123"
DB_NAME = "genaichat"
DB_HOST = "34.68.1.193"

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://aryan:Sahu&123@34.68.1.193:5432/genaichat"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
