---
title: "Docker Volume & Bind Mount 완전 가이드"
date: 2025-08-07
categories:
  - docker
tags:
  - volume
  - bind-mount
  - data-persistence
  - storage
---

# Docker Volume & Bind Mount 완전 가이드

## 1. 데이터 영속성의 필요성

### 1-1. 컨테이너의 특성
- **임시성**: 컨테이너 삭제 시 데이터 손실
- **격리성**: 컨테이너 간 데이터 공유 불가
- **재시작**: 컨테이너 재시작 시 데이터 초기화

### 1-2. 데이터 영속성이 필요한 경우
- **데이터베이스**: PostgreSQL, MySQL, Redis
- **로그 파일**: 애플리케이션 로그, 시스템 로그
- **설정 파일**: 환경별 설정, 인증서
- **업로드 파일**: 사용자 업로드, 임시 파일

## 2. Volume vs Bind Mount

### 2-1. Volume (볼륨)

**특징:**
- Docker가 관리하는 데이터 저장소
- 컨테이너와 독립적으로 존재
- 여러 컨테이너에서 공유 가능
- 백업, 마이그레이션 용이

**사용법:**
```bash
# 볼륨 생성
docker volume create my-volume

# 컨테이너에 볼륨 마운트
docker run -v my-volume:/app/data nginx

# 익명 볼륨
docker run -v /app/data nginx
```

**Dockerfile에서 사용:**
```dockerfile
FROM postgres:13
VOLUME ["/var/lib/postgresql/data"]
```

### 2-2. Bind Mount (바인드 마운트)

**특징:**
- 호스트의 특정 경로를 컨테이너에 직접 마운트
- 호스트와 컨테이너 간 실시간 동기화
- 개발 환경에서 코드 변경사항 즉시 반영
- 절대 경로 사용

**사용법:**
```bash
# 호스트 경로를 컨테이너에 마운트
docker run -v /host/path:/container/path nginx

# 현재 디렉토리 마운트 (개발용)
docker run -v $(pwd):/app nginx
```

### 2-3. 비교표

| 구분 | Volume | Bind Mount |
|------|--------|------------|
| **관리 주체** | Docker | 사용자 |
| **위치** | Docker 영역 | 호스트 파일시스템 |
| **이식성** | 높음 | 낮음 |
| **성능** | 좋음 | 매우 좋음 |
| **사용 사례** | 프로덕션 | 개발 환경 |

## 3. 실무 활용 예시

### 3-1. 데이터베이스 볼륨 관리

```bash
# PostgreSQL 볼륨 생성
docker volume create postgres-data

# 컨테이너 실행
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=password \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:13
```

### 3-2. 개발 환경 설정

```bash
# 소스 코드 바인드 마운트
docker run -d \
  --name myapp \
  -v $(pwd):/app \
  -p 8000:8000 \
  python:3.9
```

### 3-3. 로그 수집

```bash
# 로그 디렉토리 볼륨
docker run -d \
  --name nginx \
  -v nginx-logs:/var/log/nginx \
  nginx:alpine
```

### 3-4. 설정 파일 관리

```bash
# 설정 파일 바인드 마운트
docker run -d \
  --name nginx \
  -v /etc/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
  nginx:alpine
```

## 4. 볼륨 관리 명령어

### 4-1. 볼륨 생성 및 관리

```bash
# 볼륨 생성
docker volume create my-volume

# 볼륨 목록 확인
docker volume ls

# 볼륨 상세 정보
docker volume inspect my-volume

# 볼륨 삭제
docker volume rm my-volume

# 사용하지 않는 볼륨 삭제
docker volume prune
```

### 4-2. 볼륨 백업 및 복원

```bash
# 볼륨 백업
docker run --rm -v my-volume:/data -v $(pwd):/backup alpine tar czf /backup/my-volume-backup.tar.gz -C /data .

# 볼륨 복원
docker run --rm -v my-volume:/data -v $(pwd):/backup alpine tar xzf /backup/my-volume-backup.tar.gz -C /data
```

## 5. 고급 활용

### 5-1. 읽기 전용 마운트

```bash
# 읽기 전용 바인드 마운트
docker run -v /host/config:/container/config:ro nginx

# 읽기 전용 볼륨
docker run -v my-volume:/data:ro nginx
```

### 5-2. 여러 볼륨 마운트

```bash
# 여러 볼륨 동시 마운트
docker run -d \
  --name myapp \
  -v app-data:/app/data \
  -v app-logs:/app/logs \
  -v app-config:/app/config \
  myapp:latest
```

### 5-3. tmpfs 마운트 (메모리 기반)

```bash
# 임시 파일시스템 (메모리 기반)
docker run --tmpfs /tmp nginx
```

## 6. Docker Compose에서의 활용

### 6-1. 볼륨 정의

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:13
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: password

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - nginx-logs:/var/log/nginx

volumes:
  postgres-data:
  nginx-logs:
```

### 6-2. 바인드 마운트

```yaml
version: '3.8'
services:
  app:
    image: myapp:latest
    volumes:
      - ./src:/app/src
      - ./config:/app/config:ro
    ports:
      - "8000:8000"
```

## 7. 면접 포인트

### 7-1. 주요 질문 유형
- **"Volume과 Bind Mount의 차이점은?"**
- **"언제 Volume을 사용하고 언제 Bind Mount를 사용하나요?"**
- **"데이터 영속성을 어떻게 보장하나요?"**
- **"볼륨 백업은 어떻게 하나요?"**

### 7-2. 답변 포인트

#### Q: "Volume과 Bind Mount를 언제 사용하나요?"
**답변 포인트:**
- **Volume**: 프로덕션 환경, 데이터베이스, 로그
- **Bind Mount**: 개발 환경, 설정 파일, 코드 변경사항
- **성능 고려**: Bind Mount가 더 빠름
- **이식성 고려**: Volume이 더 이식성 높음

#### Q: "데이터 영속성을 어떻게 보장하나요?"
**답변 포인트:**
- 적절한 볼륨 마운트 설정
- 정기적인 백업 전략
- 읽기 전용 마운트로 보안 강화
- 여러 볼륨으로 데이터 분리

---
<details>
<summary>cf. reference</summary>

- Docker 공식 문서
- Docker Best Practices
- 컨테이너 오케스트레이션 가이드
</details> 