---
title: "Redis TTL & Eviction 정리 (이론)"
date: 2025-07-31
categories:
  - redis
tags:
  - redis
  - ttl
  - eviction
  - big-key
  - hot-key
---

# Redis TTL & Eviction (이론 정리)
- Redis는 인메모리 기반의 Key-Value 데이터 저장소로, **만료(Expiration)**와 **메모리 관리(Eviction)** 정책을 이해하는 것이 중요하다.  
- TTL 설정, Eviction 정책, big key/hot key 문제에 대해서 알아보자.

---

## 1️⃣ TTL (Time To Live) & Expiration
Redis는 키에 유효기간(Time To Live, TTL)을 설정할 수 있으며, 만료된 키는 두 가지 정책으로 제거된다.

### TTL 설정
```bash 
# TTL 설정 명령어
EXPIRE key seconds` (기존 키에 초 단위 TTL 설정)
PEXPIRE key milliseconds` (기존 키에 밀리초 단위 TTL 설정)

# 키 생성 시 TTL 부여
SET key value EX seconds` (키 생성과 동시에 초 단위 TTL 부여)
SET key value PX milliseconds` (키 생성과 동시에 밀리초 단위 TTL 부여)

# 조건부 키 설정 (TTL 없이)
#SET key value NX` (키가 존재하지 않을 때만 설정, Not eXists)
#SET key value XX` (키가 존재할 때만 설정, eXists)
# 조건부 키 설정 + TTL 부여 (원자적 연산)
# SET key value EX seconds NX` (키가 존재하지 않을 때만 설정 + 초 단위 TTL)
# SET key value EX seconds XX` (키가 존재할 때만 설정 + 초 단위 TTL)
# SET key value PX milliseconds NX` (키가 존재하지 않을 때만 설정 + 밀리초 단위 TTL)
# SET key value PX milliseconds XX` (키가 존재할 때만 설정 + 밀리초 단위 TTL)

# TTL 조회 명령어
TTL key` (남은 TTL 조회, 초 단위, -1: TTL 없음, -2: 키 없음)
PTTL key` (남은 TTL 조회, 밀리초 단위, -1: TTL 없음, -2: 키 없음)

# TTL 제거 명령어
PERSIST key` (지정한 키의 TTL 제거, 영구 보존)
```

### 만료 정책
Redis는 **Lazy Expiration**과 **Active Expiration**을 혼합 사용한다.

1. **Lazy Expiration (지연 삭제)**  
   - 클라이언트가 키에 접근할 때 만료 여부 확인 후 삭제  
   - 이 방식은 명령이 실행될 때 만료여부를 확인. CPU 부하가 적음  
   - 단점: 접근하지 않는 만료 키는 메모리에 남아있음

2. **Active Expiration (주기적 스캔)**  
   - 백그라운드에서 주기적으로 만료 키를 스캔하는 작업을 수행하여 만료된 키를 제거  
   - CPU 사용량과 삭제 빈도 사이 트레이드오프 존재 (-> CPU 리소스를 제한하여 Redis의 성능에 큰 영향을 미치지 않도록 설계되었다)

### TTL Storm
- TTL Storm은 다수의 Redis 키가 동시에 만료될 때 발생하는 성능 문제
- **발생 원인**
  - 많은 키들이 같은 시점에 만료되도록 설정한 경우 
    - 예: 세션 데이터, 캐시 데이터 등을 동일한 TTL로 설정 
- **문제점**
  - CPU Spike: Active Expiration이 대량의 키를 동시에 제거하면서 CPU 사용량이 급증
  - Latency 증가: 만료 처리로 인해 다른 명령어 처리 속도가 느려짐 (e.g. 메모리가 해제되면서 해제된 공간을 효율적으로 관리/정리하는 작업을 내부적으로 진행하는데 이 작업에 집중되기 때문)
- **해결 방법**
  - TTL 값에 랜덤 offset 추가
    ```bash 
      # 기존: 모든 세션을 3600초로 설정
      EXPIRE session:123 3600
      
      # 개선: 랜덤 offset 추가 (3600 ± 300초)
      EXPIRE session:123 3600 + random(0, 600)
    ```
  - 만료 시간 분산 (Expiration spread)
    - 키 생성 시점에 따라 TTL을 다르게 설정
      - 예: 첫 번째 키는 3600초, 두 번째 키는 3650초...
  - 배치 크기 조정 
    - Redis 설정에서 Active Expiration 빈도 조절

### TTL Storm 대응 전략

#### 1. Active Expiration 부하 완화
```bash
# redis.conf 설정
# Active Expiration 빈도 조절
hz 10                    # 기본값 10, 1-500 범위
active-expire-effort 10  # 기본값 10, 1-10 범위 (높을수록 적극적)

# CPU 사용량 제한
maxmemory-policy allkeys-lru  # 메모리 부족 시 즉시 제거
```

#### 2. 만료 시간 랜덤화 (Expiration Jitter)
```python
import random

# 방법 1: 기본 TTL + 랜덤 오프셋
def set_with_jitter(key, value, base_ttl=3600, jitter_range=300):
    jitter = random.randint(-jitter_range, jitter_range)
    actual_ttl = base_ttl + jitter
    redis_client.setex(key, actual_ttl, value)

# 방법 2: 키별 고유 오프셋
def set_with_hash_jitter(key, value, base_ttl=3600, jitter_range=600):
    # 키의 해시값으로 일관된 오프셋 생성
    hash_value = hash(key) % (jitter_range * 2 + 1)
    jitter = hash_value - jitter_range
    actual_ttl = base_ttl + jitter
    redis_client.setex(key, actual_ttl, value)

# 방법 3: 시간대별 분산
def set_with_time_based_jitter(key, value, base_ttl=3600):
    import time
    current_minute = int(time.time() / 60)
    jitter = (current_minute % 10) * 60  # 0~9분 분산
    actual_ttl = base_ttl + jitter
    redis_client.setex(key, actual_ttl, value)
```

#### 3. 키워드 암기 포인트
- **TTL Storm**: 동시 만료로 인한 CPU Spike
- **Active Expiration**: 백그라운드 주기적 만료 처리
- **Expiration Jitter**: 만료 시간 랜덤화
- **hz 설정**: Active Expiration 빈도 조절
- **active-expire-effort**: 만료 처리 강도 조절

#### 4. 실무 적용 예시
```bash
# 세션 관리 시 TTL Storm 방지
# ❌ 문제가 되는 패턴
SET session:user1 "data" EX 3600
SET session:user2 "data" EX 3600
SET session:user3 "data" EX 3600

# ✅ 개선된 패턴 (랜덤 오프셋)
SET session:user1 "data" EX 3600
SET session:user2 "data" EX 3650
SET session:user3 "data" EX 3700

# ✅ 더 나은 패턴 (해시 기반 일관된 분산)
SET session:user1 "data" EX 3620  # user1의 해시값 기반
SET session:user2 "data" EX 3680  # user2의 해시값 기반
SET session:user3 "data" EX 3640  # user3의 해시값 기반
```

#### 5. 모니터링 및 감지
```bash
# TTL Storm 감지 방법
# 1. INFO 명령어로 만료 통계 확인
INFO stats | grep expired_keys

# 2. 모니터링 도구로 CPU Spike 감지
# 3. 만료 키 수 추이 그래프 확인
```

---

## 2️⃣ Eviction (메모리 관리 정책)
- Eviction은 Redis가 메모리 한계 도달했을 경우 메모리를 확보하기 위해 일부 데이터를 제거하는 프로세스를 의미한다. 레디스는 메모리 한계에 도달하면 스왑이 발생해서 성능 저하가 발생하기 때문에 이를 방지하기 위해 maxmemory 설정 + eviction 정책 설정으로 메모리를 관리한다. 
- cf. 스왑(Swap)이 발생한다는 의미
  - RAM(메모리)이 부족할 때 디스크(HDD/SSD)를 임시 메모리처럼 사용하는 것
  - 스왑 발생 = 물리 RAM 대신 디스크를 쓰는 상태
  - 문제점: 
    - 디스크는 RAM보다 수백 배 느림 → Redis 성능 급락
    - Redis는 in-memory DB라 스왑이 심하면 거의 멈춘 것처럼 느껴짐
  - 결론: Redis는 maxmemory + eviction 정책으로 스왑 발생 전에 키를 제거해야 함


Redis에서 `maxmemory`를 설정하면 메모리 초과 시 **Eviction** 정책에 따라 키를 제거한다. 

### 조건
1. `maxmemory` 설정 필요
2. Eviction 정책 설정

### Eviction 정책 (8가지)
| 정책             | 설명                                |
|-----------------|-----------------------------------|
| **noeviction**   | 메모리 초과 시 쓰기 명령 실패 (기본값) |
| **volatile-lru** | TTL 있는 키 중 LRU 제거             |
| **volatile-lfu** | TTL 있는 키 중 LFU 제거             |
| **volatile-ttl** | TTL 있는 키 중 만료 가까운 순 제거   |
| **volatile-random** | TTL 있는 키 중 랜덤 제거         |
| **allkeys-lru**  | 전체 키 중 LRU 제거                 |
| **allkeys-lfu**  | 전체 키 중 LFU 제거                 |
| **allkeys-random** | 전체 키 중 랜덤 제거             |

- **LRU (Least Recently Used)**: 가장 오래 사용되지 않은 키 제거
- **LFU (Least Frequently Used)**: 사용 빈도 낮은 키 제거
- **volatile-***: TTL 있는 키만 대상
- **allkeys-***: 전체 키 대상

### cf. Eviction 정책 설정 방법
```bash 
# maxmemory 설정 (메모리 제한)
CONFIG SET maxmemory 100mb

# Eviction 정책 설정
CONFIG SET maxmemory-policy allkeys-lru
```

### Eviction 트리거
- Eviction은 Redis 메모리가 **maxmemory를 초과한 시점**에 동작
- 설정된 정책에 따라 우선순위 키를 제거하며, 기본값 `noeviction`이면 쓰기 명령 실패

### 운영 시 추천
- `allkeys-lru` (최근 안 쓴 키부터 삭제) or `allkeys-lfu` (사용 빈도 낮은 키부터 삭제)
  - 이유: Redis는 캐시 저장소로 사용되는 경우가 많은데, 캐시는 "핫 데이터 유지"가 핵심 -> 자연스럽게 LRU/LFU가 최적 && volatile-* 정책은 TTL있는 키만 관리하므로 만료 가능성 있음

### cf. 예시 답변: 
```
질문: Eviction 정책에 대해 설명해주세요 
Redis는 메모리 초과 시 Eviction 정책을 통해 데이터를 삭제합니다.
LRU, LFU, Random, TTL 우선 정책이 있으며,
운영 환경에서는 maxmemory와 maxmemory-policy로 설정합니다.
```
---

## 3️⃣ Big Key & Hot Key 문제

### Big Key
- **정의**
  - 한 개의 키가 지나치게 큰 데이터(예: 100MB 리스트, 100만 원소 Hash 등)를 갖는 경우
- **문제점**
  - Expire/Eviction 시 한 번에 삭제 → CPU Spike
  - RDB/AOF 저장 시 성능 저하 (Fork Latency 증가)
  - 복제 시 한 키 때문에 네트워크 지연 발생
- **대응**
  - 데이터를 shard(분할)해서 여러 키로 나누기
  - Lazy deletion (`UNLINK`, 비동기 삭제) 활용

### Hot Key
- **정의**
  - 짧은 시간에 특정 키에 트래픽이 몰리는 현상
- **문제점**
  - 싱글 스레드 구조라 해당 키 처리로 CPU 편중 -> 병목 발생
  - 클러스터 환경에서는 특정 노드 과부하
- **대응**
  - Key sharding (`user:{id}%N`)
  - Lua script를 통한 원자적 처리

---
### TTL과 Eviction의 관계
- TTL은 만료 기준, Eviction은 메모리 관리
- **중요**: TTL 설정만으로는 메모리 초과 시 자동 삭제가 일어나지 않음 → maxmemory + policy 필요
  - TTL은 만료된 키만 제거하므로, 메모리 부족 상황에서는 `maxmemory` + `maxmemory-policy` 설정 필요
    - 예: TTL이 1시간인 키가 100만개 있어도, 메모리 부족 시 Eviction 정책이 동작해야 함

### maxmemory 설정 전략
```bash
# 권장 설정 예시
CONFIG SET maxmemory 6gb  # 전체 RAM 8GB 중 75% 할당
CONFIG SET maxmemory-policy allkeys-lru
```
- **전체 RAM의 60~70%만 Redis에 할당**
  - 이유: OS buffer/cache, replication, fork 작업 등 여유 공간 필요
  - 나머지 30~40%는 시스템 안정성을 위한 여유 공간으로 확보
- **설정 시 고려사항**
  - RDB/AOF 저장 시 fork로 인한 메모리 복제 발생
  - 복제(Replication) 시 추가 메모리 사용
  - OS의 buffer/cache 사용량

### TTL Storm → Eviction 동작과 충돌 가능
- **문제 상황**: TTL로 동시에 만료되는 키가 많으면 Active Expiration + Eviction 동시 발생
- **결과**: CPU Spike 및 성능 저하
- **해결책**: TTL 랜덤 오프셋으로 분산 권장
  ```bash
  # 문제가 되는 패턴
  SET session:1 "data" EX 3600
  SET session:2 "data" EX 3600
  SET session:3 "data" EX 3600
  
  # 개선된 패턴 (랜덤 오프셋 추가)
  SET session:1 "data" EX 3600
  SET session:2 "data" EX 3650
  SET session:3 "data" EX 3700
  ```
---

## 4️⃣ 핵심 요약
- TTL은 Lazy + Active Expiration 혼합
- TTL Storm → 대량 만료 시점 분산 필요
- Eviction 정책은 LRU/LFU, volatile/allkeys 조합
- big key → 삭제/저장 시 성능 저하
- hot key → 트래픽 집중으로 단일 노드 병목 발생

---
<details>
<summary>cf. reference</summary>

- https://velog.io/@wlsgur1533/%ED%9A%A8%EC%9C%A8%EC%A0%81%EC%9D%B8-%EC%BA%90%EC%8B%9C-%EB%9D%84%EC%9A%B0%EA%B8%B0%EB%A5%BC-%EC%9C%84%ED%95%9C-Redis-Eviction-%EC%A0%95%EC%B1%85
- https://lhr0419.medium.com/redis-eviction-policy-%EC%82%AC%EC%9A%A9%ED%95%98%EC%97%AC-%ED%9A%A8%EC%9C%A8%EC%A0%81%EC%9C%BC%EB%A1%9C-%EB%A0%88%EB%94%94%EC%8A%A4-%EC%82%AC%EC%9A%A9%ED%95%98%EA%B8%B0-adf30a2b9483
</details>