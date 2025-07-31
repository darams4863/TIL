---
title: "Redis TTL & Eviction 정리 (실습)"
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

# Redis TTL & Eviction (실습)

이론 정리를 바탕으로 실제 Redis에서 TTL과 Eviction을 실습해보자.

## ⚠️ 실행 방법 주의사항

### 1. Redis CLI 내부에서 실행하는 명령어
```bash
# Redis CLI 접속 후 실행
redis-cli
127.0.0.1:6379> SET key value
127.0.0.1:6379> EXPIRE key 60
127.0.0.1:6379> TTL key
```

### 2. 터미널(쉘)에서 실행하는 명령어
```bash
# 터미널에서 실행 (Redis CLI 밖에서)
redis-cli SET key value
redis-cli EXPIRE key 60
redis-cli TTL key

# for 루프 등 쉘 스크립트
for i in {1..10}; do
  redis-cli SET "key:$i" "value:$i"
done
```

**중요**: `for` 루프, `time` 명령어, 쉘 변수 등은 **터미널에서 실행**해야 합니다!

---

## 1️⃣ TTL 명령어 실습

### 기본 TTL 설정 및 조회
```bash
# Redis CLI 접속
redis-cli

# 1. 기본 키 생성
SET user:session:1 "user_data_1"
SET user:session:2 "user_data_2"

# 2. 기존 키에 TTL 설정
EXPIRE user:session:1 60  # 60초 후 만료
PEXPIRE user:session:2 120000  # 120초(120000ms) 후 만료

# 3. TTL 조회
TTL user:session:1  # 초 단위 남은 시간
PTTL user:session:2  # 밀리초 단위 남은 시간

# 4. 키 생성 시 TTL 부여
SET user:session:3 "user_data_3" EX 30  # 30초 TTL
SET user:session:4 "user_data_4" PX 60000  # 60초 TTL (밀리초)

# 5. 조건부 설정 + TTL
SET user:session:5 "user_data_5" EX 45 NX  # 키가 없을 때만 설정 + TTL
SET user:session:1 "updated_data" EX 90 XX  # 키가 있을 때만 업데이트 + TTL

# 6. TTL 제거
PERSIST user:session:1  # TTL 제거하여 영구 보존
```

### TTL 조회 결과 해석
```bash
# TTL 명령어 반환값
TTL key
# 반환값:
# -2: 키가 존재하지 않음
# -1: TTL이 설정되지 않음 (영구 키)
# 0 이상: 남은 초 수

PTTL key
# 반환값:
# -2: 키가 존재하지 않음  
# -1: TTL이 설정되지 않음
# 0 이상: 남은 밀리초 수
```

---

## 2️⃣ TTL Storm 시뮬레이션

### 문제 상황 재현
```bash
# 1. 동일한 TTL로 많은 키 생성 (TTL Storm 상황)
# 터미널에서 실행 (Redis CLI 밖에서)
for i in {1..1000}; do
  redis-cli SET "session:$i" "data_$i" EX 60
done

# 2. 60초 후 동시에 만료되는 상황 관찰
# 별도 터미널에서 모니터링
redis-cli MONITOR

# 3. 메모리 사용량 확인
redis-cli INFO memory
```

### 해결책 적용
```bash
# 터미널에서 실행 (Redis CLI 밖에서)
# 랜덤 오프셋을 적용한 개선된 방식
for i in {1..1000}; do
  # 60초 ± 30초 랜덤 오프셋
  offset=$((RANDOM % 60 - 30))
  ttl=$((60 + offset))
  redis-cli SET "session:$i" "data_$i" EX $ttl
done
```

---

## 3️⃣ Eviction 정책 실습

### 메모리 제한 설정
```bash
# 1. 현재 설정 확인
redis-cli CONFIG GET maxmemory
redis-cli CONFIG GET maxmemory-policy

# 2. 메모리 제한 설정 (100MB)
redis-cli CONFIG SET maxmemory 100mb

# 3. Eviction 정책 설정
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Eviction 동작 테스트
```bash
# 1. 메모리 한계까지 키 생성
# 터미널에서 실행 (Redis CLI 밖에서)
for i in {1..10000}; do
  redis-cli SET "test2:key:$i" "value_$i"
done

# 2. 메모리 사용량 확인
redis-cli INFO memory | grep used_memory_human

# 3. 추가 키 생성 시 Eviction 동작 확인
redis-cli SET "new:key" "new_value"

# 4. 어떤 키가 제거되었는지 확인
redis-cli EXISTS "test:key:1"  # LRU에 따라 제거된 키 확인
```

### 다양한 Eviction 정책 테스트
```bash
# 1. volatile-lru 테스트
redis-cli CONFIG SET maxmemory-policy volatile-lru

# TTL 있는 키와 없는 키 생성
redis-cli SET "persistent:key" "value"  # TTL 없음
redis-cli SET "temp:key" "value" EX 3600  # TTL 있음

# 메모리 부족 상황에서 어떤 키가 제거되는지 관찰

# 2. volatile-ttl 테스트  
redis-cli CONFIG SET maxmemory-policy volatile-ttl

# 다양한 TTL로 키 생성
redis-cli SET "key:1h" "value" EX 3600
redis-cli SET "key:2h" "value" EX 7200
redis-cli SET "key:30m" "value" EX 1800
```

---

## 4️⃣ Big Key 문제 실습

### Big Key 생성 및 문제점 관찰
```bash
# 1. 큰 리스트 생성 (Big Key)
# 터미널에서 실행 (Redis CLI 밖에서)
for i in {1..100000}; do
  redis-cli LPUSH "big:list" "item_$i"
done

# 2. 메모리 사용량 확인
redis-cli MEMORY USAGE "big:list"

# 3. 삭제 시 성능 측정
time redis-cli DEL "big:list"

# 4. 비동기 삭제 (UNLINK) 성능 비교
time redis-cli UNLINK "big:list"
```

### Big Key 해결책 적용
```bash
# 1. 데이터 분할 저장 (Sharding)
# 터미널에서 실행 (Redis CLI 밖에서)
for i in {1..100000}; do
  shard=$((i % 10))  # 10개 샤드로 분할
  redis-cli LPUSH "big:list:shard:$shard" "item_$i"
done

# 2. 분할된 데이터 삭제 (더 빠름)
time redis-cli DEL "big:list:shard:0" "big:list:shard:1" "big:list:shard:2"
```

---

## 5️⃣ Hot Key 문제 실습

### Hot Key 상황 시뮬레이션
```bash
# 1. 특정 키에 집중된 트래픽 생성
# 터미널에서 실행 (Redis CLI 밖에서)
for i in {1..1000}; do
  redis-cli GET "hot:key" &
done

# 2. Redis 성능 모니터링
redis-cli INFO stats | grep total_commands_processed
redis-cli INFO stats | grep instantaneous_ops_per_sec
```

### Hot Key 해결책 적용
```bash
# 1. Key Sharding 적용
# 터미널에서 실행 (Redis CLI 밖에서)
user_id=12345
shard=$((user_id % 4))  # 4개 샤드로 분할
redis-cli SET "user:$user_id:shard:$shard" "user_data"

# 2. 분산된 키로 접근
redis-cli GET "user:$user_id:shard:$shard"
```

---

## 6️⃣ 모니터링 및 디버깅

### Redis 상태 모니터링
```bash
# 1. 실시간 모니터링
redis-cli MONITOR

# 2. 메모리 정보
redis-cli INFO memory

# 3. 키 통계
redis-cli INFO keyspace

# 4. 성능 통계
redis-cli INFO stats

# 5. 특정 키 정보
redis-cli DEBUG OBJECT "key_name"
```

### 유용한 디버깅 명령어
```bash
# 1. 키 패턴 검색
redis-cli KEYS "pattern:*"

# 2. 키 개수 확인
redis-cli DBSIZE

# 3. 랜덤 키 선택
redis-cli RANDOMKEY

# 4. 키 타입 확인
redis-cli TYPE "key_name"

# 5. 키 크기 확인
redis-cli MEMORY USAGE "key_name"
```

---

## 7️⃣ 실습 체크리스트

### TTL 실습
- [ ] EXPIRE/PEXPIRE 명령어 사용
- [ ] SET + EX/PX 옵션 사용
- [ ] NX/XX 조건부 설정 실습
- [ ] TTL/PTTL 조회 및 결과 해석
- [ ] PERSIST로 TTL 제거

### Eviction 실습
- [ ] maxmemory 설정
- [ ] 다양한 eviction 정책 테스트
- [ ] 메모리 부족 상황에서의 동작 관찰
- [ ] volatile-* vs allkeys-* 정책 차이 확인

### Big Key 실습
- [ ] 큰 데이터 생성 및 메모리 사용량 확인
- [ ] DEL vs UNLINK 성능 비교
- [ ] 데이터 분할 저장 실습

### Hot Key 실습
- [ ] 집중 트래픽 상황 시뮬레이션
- [ ] Key Sharding 적용
- [ ] 성능 개선 효과 확인

### 모니터링
- [ ] INFO 명령어로 상태 확인
- [ ] MONITOR로 실시간 명령어 관찰
- [ ] 메모리 사용량 추적

---

## 8️⃣ 실습 후 정리

### 주요 학습 포인트
1. **TTL 명령어의 다양한 옵션과 사용법**
2. **TTL Storm의 실제 영향과 해결책**
3. **Eviction 정책별 동작 차이**
4. **Big Key/Hot Key 문제의 실제 성능 영향**
5. **Redis 모니터링과 디버깅 방법**

### 운영 환경 적용 시 고려사항
- TTL 설정 시 랜덤 오프셋 적용
- maxmemory는 전체 RAM의 60-70%로 설정
- Big Key는 사전에 분할 설계
- Hot Key는 Sharding이나 캐싱 전략 적용
- 지속적인 모니터링으로 성능 추적
