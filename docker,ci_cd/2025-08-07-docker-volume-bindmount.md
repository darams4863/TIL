---
title: "Docker Volume & Bind Mount"
date: 2025-08-07
categories:
  - docker
tags:
  - volume
  - bind-mount
  - data-persistence
  - storage
---

# Docker Volume & Bind Mount
- 컨테이너는 기본적으로 휘발성이다. 종료되면 내부 데이터는 사라짐.
- 로그, DB, 설정 파일 등은 외부 저장소에 따로 보존 필요
- 그래서 사용하는 것이: Volume, Bind Mount, 그리고 tmpfs

## 1. Volume vs Bind Mount
### Volume 
- 개념:
  - 도커가 직접 관리하는 저장소 디렉토리 
  - 호스트 시스템의 `/var/lib/docker/volumes` 안에 저장됨 
- 특징:
  - 도커가 내부적으로 관리 -> 구조가 깔끔함
  - 영속성 확보: 컨테이너를 지워도 데이터 유지 가능 
  - 백업, 마이그레이션, 복제 용이 
  - 컨테이너끼리 공유 가능 

### Bind Mount 
- 개념: 
  - 호스트의 특정 디렉토리를 컨테이너에 연결하는 방식 
- 특징: 
  - 호스트의 경로 그대로 사용 -> 개발 중 실시간 파일 연동에 유리 
  - 컨테이너가 직접 호스트의 파일을 읽고 씀 
  - 디버깅/코드 핫리로드에 편리 
  - 보안 취약 가능성 있음(호스트 경로 직접 노출, 무분별한 접근) 


## 2. Volume vs Bind Mount vs tmpfs 
- 추가로 알아야 할 개념: tmpfs?
  - 도커가 호스트의 RAM(메모리)를 이용해서 컨테이너에 일시적인 파일 시스템을 만들어주는 기능으로, 
    - 컨테이너가 실행되는 동안만 존재함
    - 디스크에 기록되지 않아 빠르고 휘발성이다 (빠른 읽고/쓰기, 컨테이너를 끄면 내용이 완전히 사라짐)
  - 왜 필요하고 언제 사용하는지? 
    - 민감한 데이터 저장
      - 컨테이너 안에서 민감한 인증 토큰이나 일회성 키를 잠깐 쓸 때, 디스크에 남기고 싶지 않을 떄 사용 
    - 속도가 중요한 임시 처리 
      - 로그 분석, 캐시, 일시적인 중간 결과 저장 등, 잠깐 쓰고 날려도 되는 데이터를 저장할 때 유용 
    - 보안 + 퍼포먼스 최적화 
      - 암호화 키 같은 데이터가 디스크에 남는게 위험할 수도 있는데, tmpfs는 메모리에만 저장되므로 훨씬 안전하고 빠름 

### Volume vs Bind Mount vs tmpfs 비교표
| 항목         | tmpfs                         | volume                       | bind mount                   |
|--------------|-------------------------------|------------------------------|------------------------------|
| 저장 위치    | RAM (휘발성)                  | 디스크 (Docker 내부)         | 디스크 (호스트 직접 경로)    |
| 지속성       | ❌ 컨테이너 종료 시 삭제       | ✅ 유지됨                    | ✅ 유지됨                    |
| 사용 목적    | 민감/임시 데이터, 속도 우선   | 운영용 데이터 저장           | 개발용 코드 공유             |
| 속도         | ⚡ 매우 빠름                  | 보통                         | 보통                         |
| 보안성       | 🔒 가장 안전                  | 안전                         | 위험 가능                    |


## 실제 사용 예시 (dev/prod)
- `db-data`: 운영에서 PostgreSQL 데이터를 영속화하는 볼륨 
- `./:/app`: 개발환경에서 코드 변경 시 즉시 반영을 위한 바인드 마운트 
- 예시:
```yaml 
  # docker-compose.yml
  services:
    db:
      image: postgres:14
      volumes:
        - db-data:/var/lib/postgresql/data  # Volume

    backend:
      build: .
      volumes:
        - ./:/app  # Bind mount (개발 환경에서만 사용)
      environment:
        - DB_HOST=db

  volumes:
    db-data:
```

## 성능 차이 요약 
|구분|설명|
|--------|--------------------------------------------------|
|Volume|도커 최적화된 파일시스템 사용 → 빠르고 안정적|
|Bind Mount|호스트 디스크 직접 접근 → I/O는 좋지만 보안/정합성 이슈 가능|
|tmpfs|RAM 사용 → 속도 매우 빠름 (단, 휘발성)|

## 보안 이슈 & 대응 
|이슈|대응 방안|
|--------|----------------------------------------------------------------------|
|호스트 디렉토리 노출 위험 (bind mount)|필요한 폴더만 최소한으로 마운트|
|민감 정보가 디스크에 저장됨|.env → .dockerignore로 제외, Vault/Secret Manager 사용|
|퍼미션 오류 발생 가능|user: 1000:1000 등 명시해서 UID/GID 맞추기|


## 데이터 백업 & 마이그레이션 
```bash 
# 볼륨 백업
docker run --rm -v my_volume:/volume -v $(pwd):/backup busybox tar czf /backup/backup.tar.gz -C /volume .

# 복원
docker run --rm -v my_volume:/volume -v $(pwd):/backup busybox tar xzf /backup/backup.tar.gz -C /volume
```

## Volume 관리 명령어 정리 

```bash 
docker volume ls                      # 볼륨 목록
docker volume inspect my_volume      # 상세 정보
docker volume prune                  # 안쓰는 볼륨 정리
docker volume rm my_volume           # 볼륨 삭제
``` 

## 실전 운영 체크리스트
- 운영용 DB는 반드시 Volume 사용 (데이터 영속화)
- 개발환경에만 Bind Mount로 핫리로드 구성
- 민감한 파일은 마운트하지 않기 (.env, 비밀번호 등)
- 용량 모니터링: du -sh /var/lib/docker/volumes/*
- tmpfs는 RAM 용량 한계에 유의

## 실전 팁! 
- 운영 환경에서는 무조건 Volume 사용
- 개발 환경에서는 Bind Mount로 핫리로드 구성
- tmpfs는 빠른 처리가 필요한 캐시나 일회성 암호키 등에만 사용
- docker-compose.dev.yml / docker-compose.prod.yml로 구성 분리하고, --env-file 옵션으로 .env.dev, .env.prod 활용
- .dockerignore 잘 구성해서 빌드 타임 최적화 (node_modules, pycache 등 제외)

---
<details>
<summary>cf. reference</summary>

- 
</details> 

