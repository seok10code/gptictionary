from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
user = os.getenv('USERNAME')  # 'root'는 기본값
passwd = os.getenv('PASSWORD')  # 기본 비밀번호
host = os.getenv('HOST')  # 기본 호스트
port = os.getenv('PORT')  # 기본 포트
db = os.getenv('DATABASE')  # 기본 데이터베이스 이름

# Synchronous SQLAlchemy engine URL
DB_URL = f'mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset=utf8mb4&collation=utf8mb4_general_ci'

# Create synchronous engine
engine = create_engine(DB_URL, echo=True)

# Create sessionmaker factory using the synchronous engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()
