from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import psycopg2
load_dotenv()

# -----------------------------
# DATABASE URL
# -----------------------------
# Example: postgresql://username:password@host:port/database
DATABASE_URL = "postgresql://postgres:Aaryan07@db.wgyhqyufvnkmwfiocimk.supabase.co:5432/postgres"

# -----------------------------
# SQLAlchemy Engine
# -----------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args={},  # For PostgreSQL, no extra args needed
    echo=True  # Set True to see SQL logs, False in production
)

# -----------------------------
# Session Local
# -----------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -----------------------------
# Base class for models
# -----------------------------
Base = declarative_base()


# -----------------------------
# Dependency to get DB session
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
