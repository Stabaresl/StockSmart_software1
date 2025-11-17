# src/config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///stocksmart.db")