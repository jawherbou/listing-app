from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

Base = declarative_base()
engine = None
SessionLocal = None

def get_engine():
    global engine
    if engine is None:
        db_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/database")
        engine = create_engine(db_url, pool_pre_ping=True)
    return engine

def get_session():
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return SessionLocal()

def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()
