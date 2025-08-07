---
title: "Docker Healthcheck & 컨테이너 운영"
date: 2025-08-06
categories:
  - docker
tags:
  - healthcheck
  - container
  - monitoring
  - operations
---

- 추가할 내용: 
  - 컨테이너 디버깅 / 성능 최적화 / 보안 실무 적용 사례? 방법? 




# Docker Healthcheck & 컨테이너 운영

## 1. Healthcheck란?

**Healthcheck**는 컨테이너의 상태를 주기적으로 확인하여 **정상 동작 여부를 판단**하는 기능입니다.

### 1-1. Healthcheck의 필요성
- **자동 복구**: 비정상 컨테이너 자동 재시작
- **로드 밸런싱**: 정상 컨테이너만 트래픽 분산
- **모니터링**: 컨테이너 상태 실시간 확인
- **배포 안정성**: 롤링 업데이트 시 정상 동작 확인

## 2. Healthcheck 구현 방법

### 2-1. Dockerfile에서 정의

```dockerfile
# HTTP 엔드포인트 확인
FROM nginx:alpine
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# 프로세스 확인
FROM postgres:13
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD pg_isready -U postgres || exit 1

# 커스텀 스크립트
FROM python:3.9-slim
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python health_check.py || exit 1
```

### 2-2. docker run에서 정의

```bash
# HTTP 헬스체크
docker run -d \
  --health-cmd="curl -f http://localhost/ || exit 1" \
  --health-interval=30s \
  --health-timeout=3s \
  --health-retries=3 \
  nginx

# 프로세스 헬스체크
docker run -d \
  --health-cmd="pg_isready -U postgres" \
  --health-interval=30s \
  postgres:13
```

## 3. Healthcheck 옵션

### 3-1. 주요 옵션

```dockerfile
HEALTHCHECK [OPTIONS] CMD command

# 옵션 설명:
# --interval=DURATION: 헬스체크 간격 (기본: 30s)
# --timeout=DURATION: 헬스체크 타임아웃 (기본: 30s)
# --start-period=DURATION: 시작 대기 시간 (기본: 0s)
# --retries=N: 재시도 횟수 (기본: 3)
```

### 3-2. 상태 확인

```bash
# 컨테이너 상태 확인
docker ps

# 헬스체크 로그 확인
docker inspect --format='{{.State.Health.Status}}' container_name

# 상세 헬스체크 정보
docker inspect container_name | grep -A 10 Health
```

## 4. 실무 활용 예시

### 4-1. 웹 애플리케이션

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# 헬스체크 엔드포인트 추가
RUN echo 'from flask import Flask; app = Flask(__name__); @app.route("/health"); def health(): return "OK"' > health.py

EXPOSE 8000
CMD ["python", "app.py"]

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### 4-2. 데이터베이스

```dockerfile
FROM postgres:13
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD pg_isready -U postgres -d mydb || exit 1
```

### 4-3. Redis

```dockerfile
FROM redis:6-alpine
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD redis-cli ping || exit 1
```

## 5. 재시작 정책

### 5-1. 재시작 정책 설정

```bash
# no: 재시작하지 않음 (기본값)
docker run --restart=no nginx

# on-failure: 실패 시에만 재시작
docker run --restart=on-failure:3 nginx

# always: 항상 재시작
docker run --restart=always nginx

# unless-stopped: 명시적으로 중지하지 않는 한 재시작
docker run --restart=unless-stopped nginx
```

### 5-2. 재시작 정책과 Healthcheck 조합

```bash
# 헬스체크 실패 시 자동 재시작
docker run -d \
  --restart=on-failure:3 \
  --health-cmd="curl -f http://localhost/ || exit 1" \
  --health-interval=30s \
  nginx
```

## 6. 로그 관리

### 6-1. 로그 드라이버 설정

```bash
# JSON 파일 로그 (기본)
docker run --log-driver=json-file nginx

# 로그 크기 제한
docker run --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  nginx

# syslog로 전송
docker run --log-driver=syslog nginx
```

### 6-2. 로그 확인

```bash
# 컨테이너 로그 확인
docker logs container_name

# 실시간 로그 확인
docker logs -f container_name

# 특정 시간 이후 로그
docker logs --since="2023-01-01T00:00:00" container_name

# 마지막 N줄만 확인
docker logs --tail=100 container_name
```

## 7. 면접 포인트

### 7-1. 주요 질문 유형
- **"Healthcheck를 어떻게 구현하나요?"**
- **"컨테이너가 자주 죽는데 어떻게 해결하나요?"**
- **"재시작 정책을 어떻게 설정하나요?"**
- **"로그 관리는 어떻게 하시나요?"**

### 7-2. 답변 포인트

#### Q: "Healthcheck를 어떻게 구현하나요?"
**답변 포인트:**
- HTTP 엔드포인트 확인
- 프로세스 상태 확인
- 커스텀 스크립트 사용
- 적절한 간격과 재시도 설정

#### Q: "컨테이너가 자주 죽는데 어떻게 해결하나요?"
**답변 포인트:**
- Healthcheck 구현
- 재시작 정책 설정
- 로그 분석
- 리소스 제한 확인

---
<details>
<summary>cf. reference</summary>

- Docker 공식 문서
- Docker Best Practices
- 컨테이너 오케스트레이션 가이드
</details> 