from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

TESTING = os.getenv("TESTING", "0") == "1"

# Database URL (Update with your actual credentials)
DATABASE_URL = os.getenv("DATABASE_URL") if TESTING else "postgresql://myuser:mypassword@localhost:6666/mydatabase"

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()
