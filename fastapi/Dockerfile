# Python 3.9을 베이스 이미지로 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /fastapi/

# 필수 시스템 패키지 설치 (mysqlclient를 위한 패키지 포함)
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 파일 복사
COPY ./app/requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 복사
COPY ./app /fastapi/app

# Uvicorn이 사용할 포트 노출
EXPOSE 8000

# Uvicorn 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
