from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = BASE_DIR / ".env"

# Load environment variables
load_dotenv()
user = os.getenv('DB_USERNAME')  # 'root'는 기본값
passwd = os.getenv('DB_PASSWORD')  # 기본 비밀번호
host = os.getenv('DB_HOST')  # 기본 호스트
port = os.getenv('DB_PORT')  # 기본 포트
db = os.getenv('DB_DATABASE')  # 기본 데이터베이스 이름

# Synchronous SQLAlchemy engine URL
DATABASE_URL = f'mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset=utf8mb4&collation=utf8mb4_general_ci'

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


