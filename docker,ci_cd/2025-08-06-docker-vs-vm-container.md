---
title: "Docker란? Docker vs VM & 이미지 vs 컨테이너"
date: 2025-08-06
categories:
  - docker
tags:
  - docker
  - vm
  - image
  - container
  - interview
---

# Docker란? Docker vs VM & 이미지 vs 컨테이너

## 0. Docker란 무엇인가?
- Docker는 애플리케이션과 실행 환경을 컨테이너(Container) 형태로 패키징하여 
어디서든 동일한 환경에서 실행할 수 있도록 해주는 가상화 플랫폼입니다.

- **핵심 장점**
1. **환경 일관성 보장** (로컬, 스테이징, 운영 환경 동일화)
2. **배포 효율화** (컨테이너 단위로 이동/재배포/롤백이 용이)
3. **경량화** (VM 대비 리소스를 적게 사용, 시작 속도 빠름)

- **활용 예시:**
	- FastAPI/Django 서버 배포
	- Redis, PostgreSQL, RabbitMQ 같은 미들웨어 실행
	- CI/CD 테스트 환경 자동 구성

---

## 1. VM과 컨테이너의 차이

### 1-1. 구조적 차이점
- 정리: 
| 항목 | VM (Virtual Machine) | Docker (Container) |
|------|---------------------|-------------------|
| **구조** | Hypervisor + Guest OS + App | Host OS + Container Runtime + App |
| **부팅 속도** | 수십 초~수 분 | 수 초 이내 |
| **리소스 사용** | 무겁고 고정 | 경량, 동적 사용 가능 |
| **환경 격리** | 완전한 OS 단위 | 프로세스 단위 격리 (Namespace) |
| **이식성** | 제한적 | 높음 (이미지 기반 배포) |

Q. Docker와 VM의 차이점은?

"VM과 Docker의 차이를 설명해보겠습니다.

먼저 **VM(Virtual Machine)**은 물리 서버 위에 **하이퍼바이저(Hypervisor)**를 두고,
그 위에 각각의 게스트 OS와 애플리케이션을 설치하는 구조입니다.

예를 들어 하나의 서버에서 3개의 VM을 띄운다고 하면,
우분투, 윈도우, 센토스를 각각 설치하고 그 위에서 앱을 실행하게 됩니다.
그래서 부팅 속도가 느리고, 메모리/CPU를 많이 차지하게 돼요.

반면에 Docker 컨테이너는 호스트 OS의 커널을 그대로 공유합니다.
하이퍼바이저를 거치지 않고, **컨테이너 런타임(Docker Engine)**이
프로세스 단위로 애플리케이션을 격리해서 실행해요.

덕분에 수 초 안에 컨테이너가 바로 뜨고,
필요한 만큼만 리소스를 쓰기 때문에 굉장히 경량화되어 있습니다.

정리하면,
	•	VM은 하드웨어 가상화 → 각 VM마다 OS 필요 → 무겁고 느림
	•	Docker 컨테이너는 OS 커널 공유 → 프로세스 단위 격리 → 가볍고 빠름

그래서 최근에는 대부분의 서비스가 VM보다 컨테이너 기반 배포를 표준으로 쓰고 있습니다."

꼬리 질문 1: 컨테이너가 어떻게 격리되나요?

“리눅스 커널의 Namespace를 이용해 프로세스, 네트워크, 파일시스템을 분리하고,
cgroups로 CPU/메모리 같은 리소스 사용량을 제한합니다.”

꼬리 질문 2: 맥에서 Docker는 어떻게 실행되나요?

“맥은 리눅스 커널이 없기 때문에,
Docker Desktop이 내부적으로 경량 리눅스 VM을 띄우고
그 안에서 Docker Daemon이 컨테이너를 실행합니다.”


---

#### 커널이 뭔데?
- 운영체제(OS)의 핵심 부분으로 CPU, 메모리, 디스크, 네트워크 같으 하드웨어 자원 관리를 담당한다.
- 우리가 실행하는 모든 프로그램은 결국 커널을 통해 하드웨어에 접근합니다. 
- VM과 컨테이터의 차이를 


### 1-2. 핵심 차이점

**가장 큰 차이점:**
- **VM**: Hypervisor를 통해 하드웨어를 가상화하여 각각의 독립적인 OS 환경 제공
- **컨테이너**: Host OS 커널을 공유하여 프로세스 수준의 격리 제공

**컨테이너가 OS에 상관없이 실행 가능한 이유:**
- **Host OS 커널 공유 + Namespace + cgroups**

### 1-3. Docker 격리 원리 상세

#### 1-3-1. Namespace (네임스페이스)

**Namespace**는 Linux 커널의 기능으로, 프로세스들이 서로 다른 리소스 뷰를 가지도록 해줍니다.

**주요 Namespace 종류:**
- **PID Namespace**: 프로세스 ID 격리 (각 컨테이너는 독립적인 PID 공간)
- **Network Namespace**: 네트워크 인터페이스, 라우팅 테이블 격리
- **Mount Namespace**: 파일시스템 마운트 포인트 격리
- **UTS Namespace**: 호스트명과 도메인명 격리
- **IPC Namespace**: 프로세스 간 통신 격리
- **User Namespace**: 사용자 ID와 그룹 ID 격리

#### 1-3-2. cgroups (Control Groups)

**cgroups**는 프로세스 그룹의 리소스 사용량을 제한하고 격리하는 기능입니다.

**주요 제어 항목:**
- **CPU**: CPU 사용량 제한 및 할당
- **Memory**: 메모리 사용량 제한
- **I/O**: 디스크 I/O 대역폭 제한
- **Network**: 네트워크 대역폭 제한

#### 1-3-3. 격리 원리 작동 방식

```bash
# 컨테이너 내부에서 보는 프로세스 (PID 1부터 시작)
docker run -it ubuntu ps aux

# 호스트에서 보는 프로세스 (실제 PID)
ps aux | grep docker
```

### 1-4. Docker 보안 고려사항

#### 1-4-1. Host 커널 공유로 인한 보안 이슈

**잠재적 보안 위험:**
1. **커널 취약점 공유**: Host OS 커널 취약점이 모든 컨테이너에 영향
2. **권한 상승**: 컨테이너 내부에서 Host 시스템에 접근 가능성
3. **리소스 고갈**: 악의적 컨테이너가 Host 리소스 고갈 공격

**보안 대책:**
1. **최신 커널 사용**: 정기적인 보안 패치 적용
2. **컨테이너 권한 제한**: `--privileged` 플래그 사용 금지
3. **리소스 제한**: cgroups를 통한 엄격한 리소스 제한
4. **이미지 스캔**: 정기적인 보안 취약점 스캔

#### 1-4-2. 보안 강화 방법

```bash
# 권한 제한된 컨테이너 실행
docker run --user 1000:1000 -it ubuntu bash

# 리소스 제한
docker run --memory=512m --cpus=1.0 -it ubuntu bash

# 읽기 전용 파일시스템
docker run --read-only -it ubuntu bash

# 보안 옵션 추가
docker run --security-opt=no-new-privileges -it ubuntu bash
```

## 2. Docker Engine 구조

### 2-1. Docker 구조 (Engine / Daemon / Client)
- Docker는 다음 3가지 컴포넌트로 구성됩니다:
    1.	Docker Engine
        - 컨테이너를 실행·관리하는 전체 플랫폼
    2.	Docker Daemon (dockerd)
        - 백그라운드에서 컨테이너/이미지 관리
        - 컨테이너 생성, 실행, 중지 요청을 실제로 처리
    3.	Docker Client (CLI)
        - 사용자가 docker run, docker ps 등 명령어 입력
        - → Daemon에 API 요청을 보내서 실제 작업 수행
    ```
    [CLI] docker run
        ↓  REST API
    [Daemon] 컨테이너 생성/관리
        ↓
    [Engine] Linux Namespace + cgroups 활용해 컨테이너 실행

    ※ 맥/윈도우의 경우 Docker Desktop 내부에서 리눅스 VM을 띄우고, 그 위에서 Docker Engine이 실행됨   
    (리눅스 커널 필요하기 때문)
    ```

### 2-2. Docker 작동 원리 (핵심 요약)
- 도커의 가장 핵심적인 기술은 컨테이너다. 

#### 2-2-1. 핵심 기술

1. **Namespace**
   - 프로세스, 네트워크, 파일 시스템을 컨테이너 단위로 격리

2. **cgroups (Control Groups)**
   - CPU, 메모리 등 리소스 사용량 제한 및 관리

3. **Layered Image**
   - 여러 레이어를 조합해 컨테이너 생성
   - 이미지 재사용으로 빌드·배포 속도 최적화

## 3. 이미지와 컨테이너의 차이

### 1) 정의

- **이미지 (Image)**: 컨테이너 실행을 위한 불변(immutable) 템플릿
  - 여러 레이어의 스냅샷으로 구성
- **컨테이너 (Container)**: 이미지를 기반으로 실행 중인 인스턴스
  - 상태 변화 가능(로그, 데이터) → 삭제 시 초기화

### 2) 비유

- **이미지 = 클래스(Class)**
- **컨테이너 = 객체(Instance)**

### 3) 면접 질문 예시

**Q: "이미지와 컨테이너의 차이를 설명해보세요."**

**Q: "컨테이너를 삭제하면 데이터는 어떻게 되나요?"** (→ 볼륨 필요성 꼬리 질문)

## 4. 컨테이너의 장점/단점

### 1) 장점

- **빠른 배포/시작**: 수초 내에 배포 및 시작 가능
- **일관된 환경**: 로컬, 스테이징, 프로덕션 등 각 단계에서 동일한 환경 보장
- **가볍고 높은 확장성**: 마이크로서비스 아키텍처에 적합

### 2) 단점

- **커널 공유로 인한 보안 취약점 가능성**: Host OS 커널을 공유하므로 잠재적 보안 위험
- **상태 유지 서비스(DB 등)는 볼륨 관리 필요**: 데이터베이스 등 상태 유지 서비스는 신중한 볼륨 관리 필요
- **완전한 OS 격리가 필요한 경우 VM이 더 적합**: 완전한 운영체제 격리가 엄격한 요구사항인 경우 VM이 더 적합

## 5. Docker Hub와 이미지 관리

### 5-1. Docker Hub란?

**Docker Hub**는 Docker 이미지를 공유하고 배포하는 **클라우드 기반 레지스트리 서비스**입니다. 쉽게 말해서 "Docker 이미지의 GitHub"라고 생각하면 됩니다.

#### 5-1-1. Docker Hub의 구성

1. **공식 이미지 (Official Images)**
   - Docker Inc.에서 제공하는 검증된 이미지들
   - 예: `nginx`, `postgres`, `redis`, `python`, `node`, `mysql` 등
   - 보안과 품질이 보장됨

2. **개인/팀 이미지**
   - 사용자가 직접 빌드하고 공유하는 이미지들
   - 예: `mycompany/myapp:latest`, `username/myproject:v1.0`

3. **Private Repository**
   - 비공개 이미지 저장소
   - 팀 내부에서만 사용하는 이미지 관리

### 5-2. Docker Hub 사용 방법

#### 5-2-1. 기본 사용법

```bash
# 1. Docker Hub 로그인
docker login

# 2. 이미지 다운로드 (pull)
docker pull nginx:latest
docker pull postgres:13

# 3. 이미지 검색
docker search python
docker search redis

# 4. 내 이미지를 Docker Hub에 업로드
docker tag myapp:latest myusername/myapp:latest
docker push myusername/myapp:latest
```

#### 5-2-2. 이미지 태그 관리
- Docker 이미지 태그는 같은 이미지의 다른 버전을 구분하기 위한 라벨이다. 
쉽게 말해서 "이미지의 이름표"라고 생각하면 된다.
- 활용: 
    - **이미지 버전 관리**: `v1.0`, `v1.1`, `latest` 등으로 버전 관리
    - **환경별 이미지**: `dev`, `staging`, `prod` 태그로 환경 구분  
    - **보안 이미지**: 공식 이미지 기반으로 보안 패치 적용

```bash
# 이미지에 태그 지정
docker tag myapp:latest myusername/myapp:v1.0
docker tag myapp:latest myusername/myapp:latest

# 특정 태그의 이미지 다운로드
docker pull myusername/myapp:v1.0
```

### 5-3. 주요 Docker Hub 명령어

| 명령어 | 설명 | 사용 예시 |
|--------|------|-----------|
| `docker pull <image>` | Docker Hub에서 이미지 다운로드 | `docker pull nginx:latest` |
| `docker push <image>` | 로컬 이미지를 Docker Hub에 업로드 | `docker push myusername/myapp:latest` |
| `docker login` | Docker Hub 계정 로그인 | `docker login` |
| `docker search <keyword>` | Docker Hub에서 이미지 검색 | `docker search python` |
| `docker tag <source> <target>` | 이미지에 태그 지정 | `docker tag myapp:latest myusername/myapp:v1.0` |

### 5-4. 실무에서 Docker Hub 활용

#### 5-4-1. 개발 환경 구성

```bash
# 개발에 필요한 기본 이미지들
docker pull python:3.9
docker pull postgres:13
docker pull redis:6
docker pull nginx:alpine
```

#### 5-4-2. CI/CD 파이프라인에서 활용

```yaml
# GitHub Actions 예시
- name: Build and push Docker image
  run: |
    docker build -t myusername/myapp:${{ github.sha }} .
    docker push myusername/myapp:${{ github.sha }}
```

<!-- #### 5-4-3. 팀 협업에서 활용

- **이미지 버전 관리**: `v1.0`, `v1.1`, `latest` 등으로 버전 관리
- **환경별 이미지**: `dev`, `staging`, `prod` 태그로 환경 구분
- **보안 이미지**: 공식 이미지 기반으로 보안 패치 적용 -->

### 5-5. Docker Hub 보안 고려사항

1. **이미지 스캔**: Docker Hub는 자동으로 보안 취약점 스캔
2. **Private Repository**: 민감한 이미지는 private으로 관리
3. **이미지 서명**: 이미지 무결성 검증
4. **접근 제어**: 팀 멤버별 권한 관리

### 5-3. 자주 물어보는 수준의 기본 명령어

| 명령어 | 설명 |
|--------|------|
| `docker run <image>` | 이미지 기반 컨테이너 실행 |
| `docker ps -a` | 실행 중/종료된 컨테이너 목록 확인 |
| `docker stop <id>` | 컨테이너 정지 |
| `docker rm <id>` | 정지된 컨테이너 삭제 |
| `docker logs <id>` | 컨테이너 로그 확인 |
| `docker exec -it <id> sh` | 컨테이너 내부 접속 |
| `docker images` | 로컬 이미지 목록 확인 |
| `docker rmi <image>` | 이미지 삭제 |

## 6. 면접 포인트

### 6-1. 주요 질문 유형

- **"Docker와 VM의 차이점은 무엇인가요?"**
- **"Docker 컨테이너가 격리된 환경처럼 보이는 원리는 무엇인가요?"**
  - 핵심: **Namespace + cgroups**
- **"Docker Engine의 구성 요소를 설명해보세요."**
  - 핵심: **Docker Daemon + Docker CLI + Docker API**
- **"Docker Hub는 무엇이고, 어떻게 사용하나요?"**
  - 핵심: **이미지 레지스트리, pull/push, 공식 이미지 활용**
- **"Docker Hub에서 어떤 이미지를 주로 사용하나요?"**
  - 핵심: **공식 이미지 활용, 보안 고려사항**
- **"팀에서 이미지를 어떻게 관리하나요?"**
  - 핵심: **버전 관리, 태그 전략, CI/CD 연동**
- **"Docker를 사용하면 배포에서 어떤 장점이 있나요?"**

### 6-2. Docker Hub 면접 질문 예시

#### Q1: "Docker Hub에서 이미지를 선택할 때 어떤 기준으로 선택하나요?"

**답변 포인트:**
- 공식 이미지 우선 사용 (보안, 안정성)
- 다운로드 수, 별점, 최근 업데이트 확인
- 이미지 크기와 보안 취약점 스캔 결과 확인

#### Q2: "팀에서 이미지 버전을 어떻게 관리하나요?"

**답변 포인트:**
- 시맨틱 버저닝 사용 (`v1.0.0`, `v1.1.0`)
- 환경별 태그 관리 (`dev`, `staging`, `prod`)
- `latest` 태그는 개발용으로만 사용

#### Q3: "Docker Hub의 보안을 어떻게 고려하나요?"

**답변 포인트:**
- 공식 이미지 사용
- 정기적인 보안 스캔
- Private repository 활용
- 이미지 서명 검증

### 6-3. Docker 격리 및 보안 면접 질문 예시

#### Q1: "Docker는 왜 격리된 환경처럼 보이나요?"

**답변 포인트:**
- **Namespace**: 프로세스, 네트워크, 파일시스템을 컨테이너별로 격리
- **cgroups**: 리소스 사용량을 제한하고 관리
- **예시**: 컨테이너 내부에서는 PID 1부터 시작하는 독립적인 프로세스 공간

#### Q2: "Host 커널 공유로 인한 보안 이슈 가능성은 없나요?"

**답변 포인트:**
- **잠재적 위험**: 커널 취약점 공유, 권한 상승 가능성
- **대책**: 최신 커널 사용, 권한 제한, 리소스 제한
- **실무 적용**: `--user`, `--memory`, `--read-only` 옵션 활용

#### Q3: "컨테이너 보안을 어떻게 강화하나요?"

**답변 포인트:**
- **권한 제한**: `--user` 옵션으로 root 권한 방지
- **리소스 제한**: cgroups를 통한 메모리, CPU 제한
- **파일시스템 보호**: `--read-only` 옵션 사용
- **보안 스캔**: 정기적인 이미지 보안 취약점 검사


---
<details>
<summary>cf. reference</summary>

- https://wonos.tistory.com/entry/%EB%8F%84%EC%BB%A4-%EB%A9%B4%EC%A0%91-%EC%A7%88%EB%AC%B8-20%EC%84%A0-%EC%A0%95%EB%A6%AC-%EC%8B%A4%EB%AC%B4-%EA%B0%9C%EB%B0%9C%EC%9E%90%EB%9D%BC%EB%A9%B4-%EA%BC%AD-%EC%95%8C%EC%95%84%EC%95%BC-%ED%95%A0-%ED%95%B5%EC%8B%AC-%EA%B0%9C%EB%85%90
- https://github.com/CHEE-UP/TECH-INTERVIEW
- https://yubeen-ha.tistory.com/176
- 
</details> 