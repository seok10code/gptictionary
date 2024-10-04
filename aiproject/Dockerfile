# Python 3.9을 베이스 이미지로 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /aiproject/gptbot

# requirements.txt 파일을 aiproject 디렉토리에서 복사
COPY ./requirements.txt /aiproject/requirements.txt

# requirements.txt 파일이 있는 aiproject 디렉토리로 이동하여 패키지 설치
RUN pip install --no-cache-dir -r /aiproject/requirements.txt

# 애플리케이션 소스 복사 (gptbot 디렉토리)
COPY ./gptbot /aiproject/gptbot

# python aiproject_mac.py 명령어로 AI 프로젝트 실행
CMD ["python", "aiproject_mac.py"]
