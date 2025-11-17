# src/database/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config  # ABSOLUTA
from database.models import Base  # ABSOLUTA

engine = create_engine(Config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()