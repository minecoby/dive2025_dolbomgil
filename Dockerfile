FROM python:3.10-slim

WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && \
    apt-get install -y \
    gcc \
    g++ \
    default-libmysqlclient-dev \
    pkg-config \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# pip 업그레이드
RUN pip install --upgrade pip setuptools wheel

# requirements.txt 복사 및 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Firebase 인증 파일 먼저 복사
COPY serviceAccountKey.json ./
# 애플리케이션 코드 복사
COPY app/ ./

# Python 경로 설정
ENV PYTHONPATH=/app

CMD ["python", "main.py"]
