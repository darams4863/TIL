---
title: "Dockerfile 작성법 & 이미지 최적화 기법"
date: 2025-08-07
categories:
  - docker
tags:
  - dockerfile
  - entrypoint
  - cmd
  - multistage
  - image-optimization
  - interview
---

# Dockerfile 작성법 & 이미지 최적화 기법

## 1. Dockerfile 
### 1-1. Dockerfile이란?
- **Dockerfile**은 Docker 이미지를 빌드하기 위한 텍스트 파일입니다. 애플리케이션과 실행 환경을 정의하는 "레시피"라고 생각하면 됩니다.

#### 1-1-1. 왜 Dockerfile이 필요한가? 
- ❌ 기존 방식: 이미지 수동 생성
	- 예전에는 컨테이너 안에 들어가서 직접 Python 설치, 의존성 설치, 환경변수 설정 등을 일일이 명령어로 실행함
	- 문제: 일관성 없음, 반복 불가, 자동화 불가능

- ✅ Dockerfile 등장: 선언형으로 “환경을 코드화”
	- 이제는 Dockerfile만 있으면 docker build 명령어로 항상 같은 환경의 이미지를 만들 수 있음
	- “코드를 기준으로 동일한 환경을 언제 어디서나 만들 수 있다” → 환경 일관성 보장
	- 자동화가 가능해짐 → CI/CD 연동에 필수

#### 1-1-2. Dockerfile의 주요 역할
| 역할 | 설명 |
|------|------|
| 이미지 자동 생성 | 동일한 Docker 이미지를 반복 생성할 수 있도록 함 |
| 환경 코드화 | OS, 라이브러리, 의존성, 실행 명령 등을 모두 코드로 명시 |
| 이식성 향상 | 누구든지 Dockerfile만 있으면 똑같은 환경을 로컬/서버에 구축 가능 |
| CI/CD 연동 기반 | 빌드/테스트/배포 자동화를 위한 핵심 기반 |
| 협업 및 버전 관리 | 실행 환경을 Git 등으로 관리 가능 → 팀원 간 환경 차이 제거 |


### 1-2. Dockerfile 기본 문법
#### 1-2-1. 꼭 알아야 할 기본 문법

<pre><code class="language-dockerfile">
# 1. 베이스 이미지 지정 (필수)
FROM python:3.11-slim

# 2. 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# 3. 호스트 → 컨테이너로 파일 복사
COPY requirements.txt .

# 4. 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 애플리케이션 소스 복사
COPY . .

# 6. 환경 변수 설정
ENV PYTHONUNBUFFERED=1

# 7. 컨테이너가 실행될 때 실행할 명령
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
</code></pre>

#### 1-2-2. 각 지시어 상세 설명

- **FROM**
  - 컨테이너 기반 이미지(base image)를 지정하는 명령어

<pre><code class="language-dockerfile">
# 공식 이미지 사용 (권장)
FROM python:3.9-slim
FROM nginx:alpine
FROM postgres:13

# 베이스 이미지 선택 기준
# - 공식 이미지 우선 사용
# - 태그 명시 (latest 대신 구체적 버전)
# - 경량 이미지 선택 (alpine, slim)
</code></pre>


- **WORKDIR**

<pre><code class="language-dockerfile">
# 작업 디렉토리 설정
WORKDIR /app

# 장점:
# - 절대 경로 사용으로 명확성 확보
# - RUN, COPY, CMD 명령어의 기본 경로 설정
# - 컨테이너 내부 구조 일관성 유지
</code></pre>

- **COPY vs ADD**

<pre><code class="language-dockerfile">
# COPY: 파일/디렉토리 복사 (권장)
COPY requirements.txt .
COPY . .

# ADD: 추가 기능 (압축 해제, URL 다운로드)
ADD archive.tar.gz /app/
ADD https://example.com/file.txt /app/

# 권장사항: 단순 복사는 COPY 사용
</code></pre>

- **RUN**
  - 도커파일로부터 도커 이미지를 빌드하는 순간 실행되는 명령어 

<pre><code class="language-dockerfile">
# 명령어 실행 (이미지 빌드 시점)
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y package-name

# 최적화 팁:
# - 여러 RUN 명령어를 하나로 합치기
# - 캐시 레이어 최소화
# - 불필요한 파일 정리
</code></pre>

- **EXPOSE**

<pre><code class="language-dockerfile">
# 포트 노출 (문서화 목적)
EXPOSE 8000
EXPOSE 80 443

# 주의: 실제 포트 바인딩은 docker run -p 옵션으로
</code></pre>

### 1-3. ENTRYPOINT vs CMD
#### 1-3-1. 기본 개념
- **ENTRYPOINT**
  - 컨테이너가 시작될 때 **항상 실행**되는 명령어
  - 컨테이너의 **주요 실행 파일**을 지정
  - `docker run` 시 추가 인자가 ENTRYPOINT에 전달됨
- **CMD**
  - 컨테이너가 시작될 때 **기본값**으로 실행되는 명령어
  - `docker run` 시 다른 명령어로 **덮어쓸 수 있음**
  - ENTRYPOINT가 없으면 CMD가 실행됨

#### 1-3-2. 사용 패턴 비교

<pre><code class="language-dockerfile">
# 패턴 1: CMD만 사용
FROM python:3.9-slim
CMD ["main.py"]

# •	docker run myapp → main.py 실행됨
# •	docker run myapp test.py → test.py 실행됨 (CMD 덮어씀)

# 👉 CMD는 기본값일 뿐, 언제든지 덮어쓸 수 있어.
</code></pre>

<pre><code class="language-dockerfile">
# 패턴 2: ENTRYPOINT만 사용
FROM python:3.9-slim
ENTRYPOINT ["python"]

# •	docker run myapp main.py → python main.py 실행
# •	docker run myapp test.py → python test.py 실행

# 👉 ENTRYPOINT는 항상 실행되며, 뒤에 붙는 건 인자(argument)야.
</code></pre>

<pre><code class="language-dockerfile">
# 패턴 3: ENTRYPOINT + CMD 조합 (실무에서 가장 많이 씀)
FROM python:3.9-slim
ENTRYPOINT ["python"]
CMD ["main.py"]

# •	docker run myapp → python main.py 실행
# •	docker run myapp test.py → python test.py 실행

# 👉 기본은 main.py, 필요하면 실행파일만 바꿔치기 가능.
# 👉 ENTRYPOINT는 명령 고정, CMD는 인자 기본값
</code></pre>

### 1-4. 멀티스테이지 빌드 (Multi-stage Build)
- 하나의 Dockerfile 안에서 여러 개의 FROM을 사용해, 빌드 단계와 실행 단계를 분리하여, 최종 이미지 크기를 최적화 하는 기법
  - 예: 빌드 도구/컴파일러가 필요하지만 실행시에는 불필요한 파일이 이미지에 남는다 (e.g. node_modules) 
  이미지 용량이 커서 배포 속도를 느리게 하는데, 이를 최종 이미지 크기를 최적화 하는 기법인 `멀티스테이지 빌드` 로 개선할 수 있다 

#### 1-4-1. 왜 필요한가? 
-	일반적인 Dockerfile은 의존성 설치, 빌드, 실행이 한 이미지 안에서 모두 처리됨
-	이 경우 빌드 도구, 중간 산출물 등 실행 시 필요 없는 파일까지 포함되어 이미지가 무겁고 보안상 불필요한 정보가 남을 수 있음
-	→ 멀티스테이지 빌드는 이를 개선하여
    - 가볍고 빠른 배포가 가능한 이미지 생성
    - 보안 강화 및 관리 용이성 증가

#### 1-4-2. 예시

<pre><code class="language-dockerfile">
# 1단계: 빌드 환경
FROM node:16 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 2단계: 실행 환경 (불필요한 파일 없음)
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# 📌 핵심:
# • FROM으로 새로운 이미지 스테이지를 시작하고 (FROM을 한번 더 쓰면, 그 뒤는 완전히 새로운 컨테이너 환경이 됨)
# • AS builder로 이름 붙이고
# • COPY --from=builder로 빌드 산출물만 가져옴
</code></pre>

#### 1-4-3. 실제 프로젝트 애플리케이션 예시

<pre><code class="language-dockerfile">
# ✅ 1단계: 의존성 설치 전용 빌더
FROM python:3.11-slim AS deps

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# requirements만 먼저 복사해서 캐시 활용
COPY requirements.txt .

# 패키지 설치 (캐시 최적화 + 용량 감소)
RUN pip install --no-cache-dir -r requirements.txt

---

# ✅ 2단계: 애플리케이션 빌드 스테이지
FROM python:3.11-slim AS builder

WORKDIR /app

# 의존성 레이어 복사
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# 애플리케이션 코드 복사
COPY . .

# 선택: pyc 파일로 컴파일 (속도 향상 목적)
# 현재 디렉토리(.)에 있는 모든 Python 소스파일(.py)를 .pyc(바이트코드)파일로 컴파일 하는 명령어 
RUN python -m compileall . 

---

# ✅ 3단계: 실행 전용 스테이지 (최종 이미지)
FROM python:3.11-slim AS runtime

WORKDIR /app

# 빌드된 코드와 패키지 복사
COPY --from=builder /app /app
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# 헬스 체크 포트 노출
EXPOSE 8000

# FastAPI 실행 (예: main.py → app 인스턴스)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
</code></pre>

#### 1-4-4. 멀티스테이지 빌드의 핵심 구성요소
1.	**FROM 여러 번 사용**
  -	각 스테이지별 독립된 환경 생성
  -	AS builder, AS deps 등으로 이름 부여
2.	**COPY –from=…**
  -	특정 스테이지에서 산출물만 추출
  -	실행 이미지엔 꼭 필요한 파일만 포함
3.	**RUN / CMD / ENV는 최종 스테이지에서만 최소화 사용**

#### 1-4-4. 멀티스테이지 빌드 장점
1. 이미지 용량 감소 → 배포 속도 향상
2. 보안 강화 → 빌드 시 사용한 임시 파일, 자격 증명 제거
3. 환경 분리 → 빌드 환경과 실행 환경의 충돌 방지
4. 캐시 활용 → 변경 없는 스테이지는 재사용 가능


### 1-5. 이미지 최적화 기법
- 멀티스테이지 빌드 기법 이외에도 다른 기법들로 이미지를 최적화 해서 빌드 속도는 빠르고, 이미지 크기는 작고, 배포는 안전하게 할 수 있다 
- 아래와 같이: 
  1. `.dockerignore` 파일  
  2. 레이어 최적화 
  3. 불필요한 파일 제거 

#### 1-5-1. .dockerignore 파일
- .git, .env, README.md. /test 폴더 등 -> 컨테이너 안에 필요없는 파일들을 Dockerfile이 복사하지 않게 설정하는 파일이다 -> 이미지가 더 작아지고 빌드 속도도 빨라짐 

```bash
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
- 도커 빌드는 각 명령어 (RUN, COPY, ADD, ENV, CMD 등)는 하나의 레이어가 된다 
- 처음부터 `COPY . .` 를 사용하면 소스 코드가 조금이라도 바뀌면 매번 `pip install`이 다시 실행되어 캐시를 못씀.
하지만 `COPY requirements.txt .` 부터 쓰면 해당 파일이 바뀌지 않으면 pip install은 캐시를 사용하게 된다. 

<pre><code class="language-dockerfile">
# ❌ 비효율적
FROM python:3.9-slim
COPY . .
RUN pip install -r requirements.txt

# ✅ 효율적
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
</code></pre>

#### 1-5-3. 불필요한 파일 제거
- 컨테이너 안에 임시 파일이나 패키지 매니저(APT) 캐시가 남으면 이미지 용량이 커진다. 
  - apt-get clean, rm -rf /var/lib/apt/lists/* 와 같은 명령어로 `APT 캐시 제거` 
  - rm -rf ~/.cache/pip -> pip 설치 후 캐시 제거 
  
<pre><code class="language-dockerfile">
# 패키지 매니저 캐시 정리
RUN apt-get update && apt-get install -y package-name \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python 캐시 정리
RUN pip install -r requirements.txt \
    && rm -rf ~/.cache/pip
</code></pre>


---
<details>
<summary>cf. reference</summary>

- 
</details> 

