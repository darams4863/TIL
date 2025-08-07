---
title: "Dockerfile 완전 가이드 & 이미지/컨테이너 이해"
date: 2025-08-07
categories:
  - docker
tags:
  - dockerfile
  - entrypoint
  - cmd
  - multistage
  - image
  - container
  - interview
---


## 4. 이미지와 컨테이너의 차이
### 4-1. 정의
- **이미지 (Image)**: 컨테이너 실행을 위한 불변(immutable) 템플릿
  - 여러 레이어의 스냅샷으로 구성
- **컨테이너 (Container)**: 이미지를 기반으로 실행 중인 인스턴스
  - 상태 변화 가능(로그, 데이터) → 삭제 시 초기화

### 비유

- **이미지 = 클래스(Class)**
- **컨테이너 = 객체(Instance)**

### 4-3. 면접 질문 예시
- **Q: "이미지와 컨테이너의 차이를 설명해보세요."**
  ```text 
  간단히 말해 이미지가 앱의 설치 파일이라면,
  컨테이너는 그 이미지를 실행한 인스턴스입니다.

  이미지는 애플리케이션을 실행하는 데 필요한 모든 환경—코드, 라이브러리, 설정 등을 포함한 정적인 패키지입니다.
  이 이미지를 기반으로 docker run 같은 명령을 실행하면
  운영체제 커널 위에서 독립적인 프로세스인 컨테이너가 생성됩니다.

  이미지는 변하지 않고, 컨테이너는 그 이미지로부터 만들어져 실행 상태로 동작하면서 입출력, 로그, 상태 등을 가지게 돼요.
  ``` 
- **Q. 그럼 컨테이너를 만들면 이미지가 수정되나요?** 
  ```text 
  아니요. 이미지는 그대로 남고, 컨테이너는 그걸 복사해서 실행한 ‘실행 인스턴스’일 뿐입니다. 
  컨테이너에서 어떤 파일을 바꾸거나 로그가 쌓여도 이미지는 불변이라 이미지에는 영향이 가지 않습니다.
  ```
- **Q. 컨테이너가 종료되면 데이터는 어떻게 되나요?** (→ 볼륨 필요성 꼬리 질문)
  ```text 
  기본적으로 컨테이너는 휘발성이라 종료되면 내부 데이터는 사라집니다.
  그래서 데이터를 영속화하려면 볼륨(Volume) 기능을 써서 호스트 디렉토리나 외부 스토리지와 연결해줘야 해요.
  ```
  (cf. 볼륨 기능은 추후 다룰 예정)





# Dockerfile 완전 이해하기 & 컨테이너 운영

## 1. Dockerfile 완전 이해하기

### 1-1. Dockerfile이란?

**Dockerfile**은 Docker 이미지를 빌드하기 위한 텍스트 파일입니다. 애플리케이션과 실행 환경을 정의하는 "레시피"라고 생각하면 됩니다.

#### 1-1-1. Dockerfile의 역할
- **이미지 빌드 자동화**: 수동 설치 과정을 자동화
- **환경 일관성**: 모든 환경에서 동일한 이미지 생성
- **버전 관리**: 코드와 함께 환경 설정도 버전 관리
- **재현 가능성**: 언제든지 동일한 환경 재생성 가능

### 1-2. Dockerfile 기본 문법

#### 1-2-1. 핵심 지시어 (Directives)

```dockerfile
# 기본 이미지 지정
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 파일 복사
COPY requirements.txt .
COPY . .

# 명령어 실행
RUN pip install -r requirements.txt

# 포트 노출
EXPOSE 8000

# 컨테이너 실행 명령
CMD ["python", "app.py"]
```

#### 1-2-2. 각 지시어 상세 설명

**FROM**
```dockerfile
# 공식 이미지 사용 (권장)
FROM python:3.9-slim
FROM nginx:alpine
FROM postgres:13

# 베이스 이미지 선택 기준
# - 공식 이미지 우선 사용
# - 태그 명시 (latest 대신 구체적 버전)
# - 경량 이미지 선택 (alpine, slim)
```

**WORKDIR**
```dockerfile
# 작업 디렉토리 설정
WORKDIR /app

# 장점:
# - 절대 경로 사용으로 명확성 확보
# - RUN, COPY, CMD 명령어의 기본 경로 설정
# - 컨테이너 내부 구조 일관성 유지
```

**COPY vs ADD**
```dockerfile
# COPY: 파일/디렉토리 복사 (권장)
COPY requirements.txt .
COPY . .

# ADD: 추가 기능 (압축 해제, URL 다운로드)
ADD archive.tar.gz /app/
ADD https://example.com/file.txt /app/

# 권장사항: 단순 복사는 COPY 사용
```

**RUN**
```dockerfile
# 명령어 실행 (이미지 빌드 시점)
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y package-name

# 최적화 팁:
# - 여러 RUN 명령어를 하나로 합치기
# - 캐시 레이어 최소화
# - 불필요한 파일 정리
```

**EXPOSE**
```dockerfile
# 포트 노출 (문서화 목적)
EXPOSE 8000
EXPOSE 80 443

# 주의: 실제 포트 바인딩은 docker run -p 옵션으로
```

### 1-3. ENTRYPOINT vs CMD

#### 1-3-1. 기본 개념

**ENTRYPOINT**
- 컨테이너가 시작될 때 **항상 실행**되는 명령어
- 컨테이너의 **주요 실행 파일**을 지정
- `docker run` 시 추가 인자가 ENTRYPOINT에 전달됨

**CMD**
- 컨테이너가 시작될 때 **기본값**으로 실행되는 명령어
- `docker run` 시 다른 명령어로 **덮어쓸 수 있음**
- ENTRYPOINT가 없으면 CMD가 실행됨

#### 1-3-2. 사용 패턴 비교

```dockerfile
# 패턴 1: CMD만 사용
FROM python:3.9-slim
CMD ["python", "app.py"]

# 실행: docker run myapp
# 결과: python app.py 실행

# 실행: docker run myapp python test.py
# 결과: python test.py 실행 (CMD 덮어씀)
```

```dockerfile
# 패턴 2: ENTRYPOINT만 사용
FROM python:3.9-slim
ENTRYPOINT ["python"]

# 실행: docker run myapp app.py
# 결과: python app.py 실행

# 실행: docker run myapp test.py
# 결과: python test.py 실행
```

```dockerfile
# 패턴 3: ENTRYPOINT + CMD 조합 (권장)
FROM python:3.9-slim
ENTRYPOINT ["python"]
CMD ["app.py"]

# 실행: docker run myapp
# 결과: python app.py 실행

# 실행: docker run myapp test.py
# 결과: python test.py 실행
```

#### 1-3-3. 실무 활용 예시

**웹 서버 (Nginx)**
```dockerfile
FROM nginx:alpine
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
```

**데이터베이스 (PostgreSQL)**
```dockerfile
FROM postgres:13
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["postgres"]
```

**애플리케이션 (Python)**
```dockerfile
FROM python:3.9-slim
ENTRYPOINT ["python"]
CMD ["app.py"]
```

### 1-4. 멀티스테이지 빌드 (Multi-stage Build)

#### 1-4-1. 멀티스테이지 빌드란?

여러 단계의 빌드 과정을 하나의 Dockerfile에서 처리하여 **최종 이미지 크기를 최적화**하는 기법입니다.

#### 1-4-2. 기본 구조

```dockerfile
# 1단계: 빌드 환경
FROM node:16 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 2단계: 실행 환경
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### 1-4-3. Python 애플리케이션 예시

```dockerfile
# 1단계: 의존성 설치
FROM python:3.9-slim AS deps
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# 2단계: 애플리케이션 빌드
FROM python:3.9-slim AS build
WORKDIR /app
COPY --from=deps /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY . .
RUN python -m compileall .

# 3단계: 실행 환경
FROM python:3.9-slim AS runtime
WORKDIR /app
COPY --from=build /app /app
COPY --from=deps /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
EXPOSE 8000
CMD ["python", "app.py"]
```

#### 1-4-4. 멀티스테이지 빌드 장점

1. **이미지 크기 최적화**: 빌드 도구와 중간 파일 제거
2. **보안 강화**: 빌드 환경의 민감한 정보 제거
3. **빌드 속도 향상**: 레이어 캐시 활용
4. **환경 분리**: 빌드 환경과 실행 환경 분리

### 1-5. 이미지 최적화 기법

#### 1-5-1. .dockerignore 파일

```dockerignore
# Git 관련
.git
.gitignore

# 개발 환경
.env
.env.local
*.log

# 의존성
node_modules/
__pycache__/
*.pyc

# 문서
README.md
docs/

# 테스트
tests/
test_*
```

#### 1-5-2. 레이어 최적화

```dockerfile
# ❌ 비효율적
FROM python:3.9-slim
COPY . .
RUN pip install -r requirements.txt

# ✅ 효율적
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

#### 1-5-3. 불필요한 파일 제거

```dockerfile
# 패키지 매니저 캐시 정리
RUN apt-get update && apt-get install -y package-name \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python 캐시 정리
RUN pip install -r requirements.txt \
    && rm -rf ~/.cache/pip
```

## 2. 면접 포인트

### 2-1. 주요 질문 유형

- **"Dockerfile을 작성해본 적이 있나요?"**
- **"ENTRYPOINT와 CMD의 차이점은?"**
- **"멀티스테이지 빌드를 사용하는 이유는?"**
- **"이미지와 컨테이너의 차이점은?"**

### 2-2. Dockerfile 면접 질문 예시

#### Q1: "Dockerfile 최적화 방법을 설명해보세요."

**답변 포인트:**
- 레이어 최소화 (RUN 명령어 합치기)
- .dockerignore 파일 사용
- 멀티스테이지 빌드 활용
- 불필요한 파일 제거
- 베이스 이미지 최적화

#### Q2: "ENTRYPOINT와 CMD를 언제 사용하나요?"

**답변 포인트:**
- **ENTRYPOINT**: 컨테이너의 주요 실행 파일 지정
- **CMD**: 기본 실행 명령어 또는 ENTRYPOINT의 인자
- **조합 사용**: ENTRYPOINT + CMD로 유연성 확보
- **실무 예시**: nginx, postgres, python 애플리케이션

#### Q3: "멀티스테이지 빌드의 장점은?"

**답변 포인트:**
- 이미지 크기 최적화
- 보안 강화 (빌드 도구 제거)
- 빌드 속도 향상
- 환경 분리 (빌드/실행)

### 2-3. 실무 문제 해결

#### Q1: "이미지 크기가 너무 큰데 어떻게 줄이나요?"

**답변 포인트:**
- 멀티스테이지 빌드 사용
- .dockerignore 파일 활용
- 베이스 이미지 최적화
- 불필요한 파일 제거

---
<details>
<summary>cf. reference</summary>

- Docker 공식 문서
- Docker Best Practices
- 컨테이너 오케스트레이션 가이드
</details> 