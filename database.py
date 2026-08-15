import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Agar DATABASE_URL environment variable set hai (Render PostgreSQL), wahi use karo
# Warna local testing ke liye SQLite use karo
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./placement.db")

# Render ka URL "postgres://" se start hota hai, lekin naye SQLAlchemy ko "postgresql://" chahiye
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# connect_args sirf SQLite ke liye chahiye, PostgreSQL ke liye nahi
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()