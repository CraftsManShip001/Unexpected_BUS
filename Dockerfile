# Python 3.11 슬림 이미지 사용
FROM python:3.11-slim-buster

# 앱 실행에 필요한 UID 및 GID 설정 (기본값: 1000)
ARG UID=1000
ARG GID=1000

# 비특권 사용자를 생성
RUN groupadd -g "${GID}" appgroup && \
    useradd --create-home --no-log-init -u "${UID}" -g "${GID}" appuser

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 파이썬 패키지 관리자 업그레이드
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 비특권 사용자로 실행
USER appuser:appgroup

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 컨테이너 포트 노출
EXPOSE 8000

# 컨테이너 실행 명령
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
