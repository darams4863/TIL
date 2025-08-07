---
title: "Redis 성능 최적화"
date: 2025-08-04
categories:
  - redis
tags:
  - redis
  - performance
  - optimization
  - cache
---

# Redis 성능 최적화

## 개요
레디스에서 성능 최적화를 하기 위한 여러가지 방법을 알아보자: 
1. 자료구조 최적화 
2. 네트워크 왕복 최소화
3. 메모리 관리 
4. 대량 처리 
5. 트랜젝션 & 원자적 처리 
6. 캐시 전략
7. 모니터링 & 튜닝
---

## 1️⃣ 자료구조 최적화
의도에 맞는 적절한 자료구조로 성능을 최적화 할 수 있다.

### 자료구조 선택 기준
```python
# 상황별 최적 자료구조 선택
# 1. 단순 값: String
redis.set("user:123:name", "John")
redis.incr("page:views")  # 카운터

# 2. 객체 데이터: Hash
redis.hset("user:123", "name", "John", "age", "30")
redis.hgetall("user:123")  # 전체 객체 조회

# 3. 리스트/큐: List
redis.lpush("queue:orders", order_data)
redis.rpop("queue:orders")  # FIFO 큐

# 4. 중복 없는 집합: Set
redis.sadd("user:123:followers", follower_id)
redis.sismember("user:123:followers", user_id)  # 빠른 포함 여부 확인

# 5. 정렬된 데이터: Sorted Set
redis.zadd("leaderboard", {"player1": 100, "player2": 200})
redis.zrevrange("leaderboard", 0, 9)  # TOP 10
```

### 실제 프로젝트 적용 예시
```python
# 현재 프로젝트에서 사용하는 자료구조
# 1. List: 작업 큐 관리
redis.lpush("queue:requests", request_data)
redis.rpop("queue:requests")

# 2. String: 분산 락 관리
redis.set("lock:queue:request:123", "worker-abc", nx=True, ex=180)

# 3. Hash: 요청 상태 관리 (향후 확장 가능)
redis.hset("request:123", "status", "processing", "worker", "worker-abc")
```

---

## 2️⃣ 네트워크 왕복 최소화
- 불필요한 네트워크 왕복을 최소화 하면 성능이 좋아진다.
### Pipeline 사용 (가장 중요한 최적화)
```python
# ❌ 비효율적: 개별 명령어 (현재 프로젝트의 기존 방식)
for request in requests:
    await RedisFunction.enqueue_request("queue:requests", request)  # 개별 네트워크 왕복

# ✅ 효율적: Pipeline (개선된 방식)
async def batch_enqueue_requests_improved(queue_key: str, requests: list):
    """대량 요청을 Pipeline으로 효율적으로 큐에 추가"""
    batch_size = 100  # 적절한 배치 크기
    
    for i in range(0, len(requests), batch_size):
        batch = requests[i:i + batch_size]
        async with await redis_pool.get_redis_connection() as redis:
            async with redis.pipeline(transaction=True) as pipe:
                for request in batch:
                    pipe.rpush(queue_key, json.dumps(request, default=default_serializer))
                await pipe.execute()  # 1번 네트워크 왕복

# 성능 비교
def performance_comparison():
    # 개별 실행: 1000개 → 1000번 왕복
    start = time.time()
    for i in range(1000):
        await RedisFunction.enqueue_request("queue:requests", {"idx": i, "data": f"request_{i}"})
    individual_time = time.time() - start
    
    # Pipeline: 1000개 → 10번 왕복 (배치 크기 100)
    start = time.time()
    requests = [{"idx": i, "data": f"request_{i}"} for i in range(1000)]
    await batch_enqueue_requests_improved("queue:requests", requests)
    pipeline_time = time.time() - start
    
    print(f"성능 향상: {individual_time/pipeline_time:.1f}배")
```

### Lua Script 사용
```python
# 복잡한 로직을 원자적으로 처리 (현재 프로젝트 예시)
# 1. 분산 락 해제 - 원자적 실행
lua_script = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""

# 1번의 네트워크 왕복으로 락 해제
result = await redis.eval(lua_script, 1, "lock:queue:request:123", "worker-abc")

# 2. 큐에서 특정 요청 찾아 업데이트
lua_script = """
local queue_key = KEYS[1]
local request_idx = tonumber(ARGV[1])
local updated_data = ARGV[2]

local requests = redis.call('lrange', queue_key, 0, -1)
for i, request in ipairs(requests) do
    local request_data = cjson.decode(request)
    if request_data.idx == request_idx then
        redis.call('lset', queue_key, i-1, updated_data)
        return 1
    end
end
return 0
"""

# 1번의 네트워크 왕복으로 큐 업데이트
result = await redis.eval(lua_script, 1, "queue:requests", 123, json.dumps(updated_request))
```

### Pipeline vs Lua Script 트레이드오프
```python
# Pipeline: 네트워크 최적화, 병렬 실행 아님 (현재 프로젝트 예시)
async def batch_enqueue_requests_improved(queue_key: str, requests: list):
    async with await redis_pool.get_redis_connection() as redis:
        async with redis.pipeline(transaction=True) as pipe:
            for request in requests:
                pipe.rpush(queue_key, json.dumps(request))  # 독립적인 명령어들
            await pipe.execute()  # 순차 실행, 네트워크 왕복 1회

# Lua Script: 원자성 보장, 서버 부하 가능성 (현재 프로젝트 예시)
lua_script = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])  # GET + 조건 확인 + DEL
else
    return 0
end
"""
result = await redis.eval(lua_script, 1, "lock:queue:request:123", "worker-abc")
```

### 실제 프로젝트에서의 선택 기준
```python
# Pipeline 사용 케이스: 대량 요청 큐 추가
# - 독립적인 rpush 명령어들
# - 네트워크 왕복 최소화가 목적
# - 원자성이 불필요

# Lua Script 사용 케이스: 분산 락 해제
# - GET + 조건 확인 + DEL 순차적 로직
# - 원자성 보장이 필수
# - Race Condition 방지
```

---

## 3️⃣ 메모리 관리

### TTL 관리
```python
# 자동 만료로 메모리 누수 방지 (현재 프로젝트 예시)
# 1. 분산 락 TTL 설정
redis.set("lock:queue:request:123", "worker-abc", nx=True, ex=180)  # 3분 후 자동 삭제

# 2. 임시 데이터 TTL 설정
redis.setex("temp:request:123", 300, temp_data)  # 5분 후 자동 삭제

# 3. 세션 데이터 TTL 설정
redis.setex("session:worker:abc", 3600, session_data)  # 1시간 후 자동 삭제

# 4. Sorted Set으로 TTL 관리 (향후 확장 가능)
redis.zadd("expire:locks", {"lock:queue:request:123": time.time() + 180})
redis.zremrangebyscore("expire:locks", 0, time.time())  # 만료된 락 정리
```

### Eviction Policy
```python
# Redis 설정에서 메모리 정책 설정
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru  # LRU 알고리즘으로 키 삭제

# 정책 종류
# volatile-lru: TTL이 있는 키 중 LRU
# allkeys-lru: 모든 키 중 LRU  
# volatile-ttl: TTL이 있는 키 중 만료 시간이 짧은 것
# noeviction: 삭제하지 않고 에러 반환
```

### 실제 프로젝트에서의 메모리 관리
```python
# 현재 프로젝트의 Redis 설정
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru  # LRU 알고리즘으로 키 삭제

# 프로젝트에서 사용하는 키 패턴
# - lock:queue:request:* (분산 락)
# - queue:requests (작업 큐)
# - temp:request:* (임시 데이터)
# - session:worker:* (워커 세션)

# 메모리 부족 시 처리 순서
# 1. 가장 오래 사용되지 않은 임시 데이터 삭제
# 2. 만료된 락 데이터 삭제
# 3. 오래된 세션 데이터 삭제
# 4. 큐 데이터는 마지막에 삭제 (중요도 고려)
```

### 메모리 최적화 명령어 활용
```python
# 메모리 사용량 분석
async def analyze_memory_usage():
    async with await redis_pool.get_redis_connection() as redis:
        # 특정 키의 메모리 사용량
        memory_usage = await redis.memory_usage("queue:requests")
        
        # 객체 참조 횟수 확인
        refcount = await redis.object("REFCOUNT", "queue:requests")
        
        # 키의 인코딩 타입 확인
        encoding = await redis.object("ENCODING", "queue:requests")
        
        return {
            "memory_usage": memory_usage,
            "refcount": refcount,
            "encoding": encoding
        }
```

### 데이터 압축
```python
import orjson  # 빠른 JSON 직렬화

# ❌ 비효율적: 기본 json
data = json.dumps(large_object)  # 느림

# ✅ 효율적: orjson
data = orjson.dumps(large_object)  # 빠름

# MessagePack 사용
import msgpack
data = msgpack.packb(large_object)  # 더 작은 크기
```

---

## 4️⃣ 대량 처리

### Batch Insert
```python
# 대량 데이터 삽입 (현재 프로젝트 예시)
# 1. 대량 요청을 큐에 추가
async def batch_enqueue_requests_improved(queue_key: str, requests: list):
    """대량 요청을 Pipeline으로 효율적으로 큐에 추가"""
    batch_size = 100  # 적절한 배치 크기
    
    for i in range(0, len(requests), batch_size):
        batch = requests[i:i + batch_size]
        async with await redis_pool.get_redis_connection() as redis:
            async with redis.pipeline(transaction=True) as pipe:
                for request in batch:
                    pipe.rpush(queue_key, json.dumps(request, default=default_serializer))
                await pipe.execute()

# 2. 대량 락 설정 (향후 확장 가능)
def batch_set_locks(lock_data_list):
    pipe = redis.pipeline()
    for lock_data in lock_data_list:
        pipe.set(f"lock:queue:request:{lock_data['request_idx']}", 
                lock_data['worker_id'], nx=True, ex=180)
    pipe.execute()
```

### SCAN 사용
```python
# ❌ 위험: KEYS 명령어 (blocking) - 현재 프로젝트에서 주의할 점
keys = redis.keys("lock:queue:request:*")  # 대량 데이터 시 Redis 멈춤
keys = redis.keys("queue:requests")  # 큐 데이터 조회 시 위험

# ✅ 안전: SCAN 명령어 (현재 프로젝트 적용)
def safe_scan(pattern="*"):
    """안전하게 키들을 조회 (락/큐 공용 사용 가능)"""
    cursor = 0
    keys = []
    while True:
        cursor, batch = redis.scan(cursor, match=pattern, count=100)
        keys.extend(batch)
        if cursor == 0:
            break
    return keys

# 실제 프로젝트에서의 대량 데이터 처리
async def cleanup_expired_locks():
    """만료된 락 정리"""
    expired_locks = safe_scan("lock:queue:request:*")
    for lock_key in expired_locks:
        if redis.ttl(lock_key) == -1:  # TTL이 없는 경우
            redis.delete(lock_key)

async def monitor_queue_status():
    """큐 상태 모니터링"""
    queue_keys = safe_scan("queue:*")
    for queue_key in queue_keys:
        length = redis.llen(queue_key)
        print(f"Queue {queue_key}: {length} items")
```

### UNLINK 활용 (대량 삭제 시 비동기 삭제)
```python
# ❌ 동기 삭제: 블로킹 발생
redis.delete("large_key")  # 큰 키 삭제 시 Redis 멈춤

# ✅ 비동기 삭제: 블로킹 방지
redis.unlink("large_key")  # 백그라운드에서 삭제

# 현재 프로젝트에서의 활용
async def cleanup_large_data():
    """대량 데이터 정리 시 UNLINK 활용"""
    # 만료된 락들을 비동기로 삭제
    expired_locks = safe_scan("lock:queue:request:*")
    for lock_key in expired_locks:
        if redis.ttl(lock_key) == -1:
            redis.unlink(lock_key)  # 블로킹 방지
```

---

## 5️⃣ 트랜잭션 & 원자적 처리

### MULTI/EXEC
```python
# 트랜잭션으로 원자적 처리 (현재 프로젝트 예시)
# 1. 큐에서 요청 제거하고 상태 업데이트
async def process_request_atomically(queue_key: str, request_idx: str):
    async with await redis_pool.get_redis_connection() as redis:
        async with redis.pipeline(transaction=True) as pipe:
            try:
                pipe.multi()
                # 큐에서 요청 제거
                pipe.rpop(queue_key)
                # 처리 상태 업데이트
                pipe.set(f"status:request:{request_idx}", "completed", ex=3600)
                await pipe.execute()
                return True
            except:
                pipe.discard()
                return False

# 2. 락 획득과 큐 추가를 원자적으로 처리 (향후 확장 가능)
async def atomic_lock_and_enqueue(lock_key: str, queue_key: str, request_data: dict):
    async with await redis_pool.get_redis_connection() as redis:
        async with redis.pipeline(transaction=True) as pipe:
            try:
                pipe.multi()
                # 락 획득
                pipe.set(lock_key, "worker-abc", nx=True, ex=180)
                # 큐에 추가
                pipe.rpush(queue_key, json.dumps(request_data))
                await pipe.execute()
                return True
            except:
                pipe.discard()
                return False
```

### WATCH (Optimistic Lock)
```python
# 낙관적 락으로 동시성 제어 (현재 프로젝트 예시)
# 1. 큐 상태 업데이트 시 낙관적 락 사용
async def update_queue_status_with_watch(queue_key: str, new_status: str):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with await redis_pool.get_redis_connection() as redis:
                await redis.watch(queue_key)
                current_status = await redis.get(f"status:{queue_key}")
                
                async with redis.pipeline(transaction=True) as pipe:
                    pipe.multi()
                    pipe.set(f"status:{queue_key}", new_status, ex=3600)
                    await pipe.execute()
                return True
        except redis.WatchError:
            continue
    return False

# 2. 요청 상태 업데이트 시 낙관적 락 사용
async def update_request_status_with_watch(request_idx: str, new_status: str):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with await redis_pool.get_redis_connection() as redis:
                await redis.watch(f"status:request:{request_idx}")
                current_status = await redis.get(f"status:request:{request_idx}")
                
                async with redis.pipeline(transaction=True) as pipe:
                    pipe.multi()
                    pipe.set(f"status:request:{request_idx}", new_status, ex=3600)
                    await pipe.execute()
                return True
        except redis.WatchError:
            continue
    return False
```

---

## 6️⃣ 캐시 전략
- Redis를 캐시로 사용할 때는 데이터 일관성과 성능을 균형 있게 유지해야 합니다.
대표적으로 세 가지 캐시 전략을 씁니다.
    - Cache-Aside (Lazy Loading)
    - Write-Through
    - Write-Behind

### Cache-Aside (Lazy Loading)
가장 일반적인 패턴으로, 필요할 때만 캐시에 데이터를 로드합니다.

```python
# 현재 프로젝트에서의 캐시 적용 예시
async def get_request_status(request_idx: str):
    # 1. 캐시에서 먼저 조회
    status = await redis.get(f"status:request:{request_idx}")
    
    if status is None:
        # 2. 캐시에 없으면 큐에서 조회
        status = await RedisFunction.is_request_in_queue("queue:requests", request_idx)
        # 3. 조회 결과를 캐시에 저장
        await redis.setex(f"status:request:{request_idx}", 300, status)  # 5분 TTL
    
    return status

async def get_worker_session(worker_id: str):
    # 1. 캐시에서 먼저 조회
    session = await redis.get(f"session:worker:{worker_id}")
    
    if session is None:
        # 2. 캐시에 없으면 DB에서 조회 (향후 확장)
        session = await db.query("SELECT * FROM worker_sessions WHERE worker_id = ?", worker_id)
        # 3. DB 결과를 캐시에 저장
        await redis.setex(f"session:worker:{worker_id}", 3600, session)  # 1시간 TTL
    
    return session
```

**장점:** 구현 간단, 메모리 효율적
**단점:** Cache Miss 시 지연, 데이터 일관성 보장 어려움

### Write-Through
데이터를 업데이트할 때 DB와 캐시를 동시에 업데이트합니다.

```python
# 현재 프로젝트에서의 Write-Through 적용 예시
async def update_request_status(request_idx: str, new_status: str):
    # 1. 큐 상태 업데이트
    await RedisFunction.update_request_in_queue("queue:requests", request_idx, {"status": new_status})
    # 2. 캐시도 동시에 업데이트
    await redis.setex(f"status:request:{request_idx}", 300, new_status)

async def update_worker_session(worker_id: str, session_data: dict):
    # 1. DB 업데이트 (향후 확장)
    await db.execute("UPDATE worker_sessions SET data = ? WHERE worker_id = ?", session_data, worker_id)
    # 2. 캐시도 동시에 업데이트
    await redis.setex(f"session:worker:{worker_id}", 3600, session_data)
```

**장점:** 항상 최신 데이터 보장, 읽기 성능 향상
**단점:** 모든 쓰기 작업이 DB + 캐시 두 번 발생

### 캐시 무효화 전략
```python
# TTL 기반 무효화 (현재 프로젝트 예시)
await redis.setex("status:request:123", 300, "processing")  # 5분 후 자동 삭제
await redis.setex("session:worker:abc", 3600, session_data)  # 1시간 후 자동 삭제

# 명시적 무효화
async def update_request_status(request_idx: str, new_status: str):
    # 큐 상태 업데이트
    await RedisFunction.update_request_in_queue("queue:requests", request_idx, {"status": new_status})
    # 관련 캐시 삭제
    await redis.delete(f"status:request:{request_idx}")

# 패턴 기반 무효화 (향후 확장 가능)
async def update_worker_info(worker_id: str, worker_data: dict):
    # DB 업데이트 (향후 확장)
    await db.execute("UPDATE workers SET data = ? WHERE worker_id = ?", worker_data, worker_id)
    # 관련된 모든 캐시 삭제
    keys = await redis.keys(f"worker:{worker_id}:*")
    if keys:
        await redis.delete(*keys)
```

### Cache Stampede 방지
동시에 여러 요청이 같은 데이터를 요청할 때 발생하는 문제를 방지합니다.

```python
# 현재 프로젝트에서의 Cache Stampede 방지
async def get_request_status_with_lock(request_idx: str):
    lock_key = f"lock:status:request:{request_idx}"
    
    # 락 획득 시도
    if await redis.setnx(lock_key, 1):
        await redis.expire(lock_key, 10)  # 10초 TTL
        
        try:
            status = await redis.get(f"status:request:{request_idx}")
            if status is None:
                # 큐에서 상태 조회
                status = await RedisFunction.is_request_in_queue("queue:requests", request_idx)
                await redis.setex(f"status:request:{request_idx}", 300, status)
            return status
        finally:
            await redis.delete(lock_key)
    else:
        # 락 획득 실패 시 잠시 대기 후 재시도
        await asyncio.sleep(0.1)
        return await redis.get(f"status:request:{request_idx}")

async def get_worker_session_with_lock(worker_id: str):
    lock_key = f"lock:session:worker:{worker_id}"
    
    # 락 획득 시도
    if await redis.setnx(lock_key, 1):
        await redis.expire(lock_key, 10)  # 10초 TTL
        
        try:
            session = await redis.get(f"session:worker:{worker_id}")
            if session is None:
                # DB에서 세션 조회 (향후 확장)
                session = await db.query("SELECT * FROM worker_sessions WHERE worker_id = ?", worker_id)
                await redis.setex(f"session:worker:{worker_id}", 3600, session)
            return session
        finally:
            await redis.delete(lock_key)
    else:
        # 락 획득 실패 시 잠시 대기 후 재시도
        await asyncio.sleep(0.1)
        return await redis.get(f"session:worker:{worker_id}")
```

### 캐시 일관성 시나리오
```python
# 실무에서 자주 발생하는 문제 (현재 프로젝트 예시)
async def update_request_consistency_issue(request_idx: str, new_status: str):
    # 문제: 동시 업데이트 시 캐시와 큐 불일치
    # 해결: 캐시 무효화로 다음 읽기 시 새로운 데이터 로드
    
    # 1. 큐에서 요청 상태 업데이트
    await RedisFunction.update_request_in_queue("queue:requests", request_idx, {"status": new_status})
    # 2. 캐시 삭제로 일관성 보장
    await redis.delete(f"status:request:{request_idx}")

async def update_worker_consistency_issue(worker_id: str, worker_data: dict):
    # 문제: 동시 업데이트 시 캐시와 DB 불일치 (향후 확장)
    # 해결: 캐시 무효화로 다음 읽기 시 새로운 데이터 로드
    
    # 1. DB 업데이트 (향후 확장)
    await db.execute("UPDATE workers SET data = ? WHERE worker_id = ?", worker_data, worker_id)
    # 2. 캐시 삭제로 일관성 보장
    await redis.delete(f"session:worker:{worker_id}")
```

---

## 7️⃣ 모니터링 & 튜닝

### 성능 모니터링
```python
# Redis 정보 조회 (현재 프로젝트 적용)
async def monitor_redis_performance():
    async with await redis_pool.get_redis_connection() as redis:
        info = await redis.info()
        memory_info = await redis.info('memory')
        stats_info = await redis.info('stats')

        # 메모리 사용량
        used_memory = memory_info['used_memory_human']
        max_memory = memory_info['maxmemory_human']

        # 성능 지표
        keyspace_hits = stats_info['keyspace_hits']
        keyspace_misses = stats_info['keyspace_misses']
        hit_rate = keyspace_hits / (keyspace_hits + keyspace_misses)

        # 프로젝트 특화 지표
        queue_length = await redis.llen("queue:requests")
        active_locks = len(await safe_scan("lock:queue:request:*"))

        return {
            "memory_usage": f"{used_memory}/{max_memory}",
            "hit_rate": f"{hit_rate:.2%}",
            "queue_length": queue_length,
            "active_locks": active_locks
        }
```

### Slowlog 분석
```python
# 느린 쿼리 확인 (현재 프로젝트 적용)
async def analyze_slow_queries():
    async with await redis_pool.get_redis_connection() as redis:
        slow_logs = await redis.slowlog_get(10)
        for log in slow_logs:
            print(f"Duration: {log['duration']}ms")
            print(f"Command: {log['command']}")

# Slowlog 설정
async def configure_slowlog():
    async with await redis_pool.get_redis_connection() as redis:
        await redis.config_set('slowlog-log-slower-than', 10000)  # 10ms 이상
        await redis.config_set('slowlog-max-len', 128)
```

### 실무 경험: Slowlog 활용
```python
# 실제 프로젝트에서 발견한 병목과 개선 사례
async def slowlog_improvement_example():
    """
    실무 경험: KEYS 명령어로 인한 성능 문제 발견
    - 문제: KEYS "lock:queue:request:*" 명령어가 50ms 이상 소요
    - 해결: SCAN으로 변경하여 5ms 이하로 개선
    - 결과: 전체 응답 시간 30% 단축
    """
    # Before: KEYS 사용 (느림)
    # keys = await redis.keys("lock:queue:request:*")
    
    # After: SCAN 사용 (빠름)
    keys = await safe_scan("lock:queue:request:*")
    return keys
```

### 메모리 분석 명령어
```python
# 메모리 사용량 상세 분석
async def analyze_memory_detailed():
    async with await redis_pool.get_redis_connection() as redis:
        # 특정 키의 메모리 사용량
        memory_usage = await redis.memory_usage("queue:requests")
        
        # 객체 참조 횟수 확인
        refcount = await redis.object("REFCOUNT", "queue:requests")
        
        # 키의 인코딩 타입 확인
        encoding = await redis.object("ENCODING", "queue:requests")
        
        # 메모리 사용량이 큰 키들 찾기
        large_keys = []
        for key in await safe_scan("*"):
            usage = await redis.memory_usage(key)
            if usage and usage > 1024:  # 1KB 이상
                large_keys.append((key, usage))
        
        return {
            "queue_memory": memory_usage,
            "queue_refcount": refcount,
            "queue_encoding": encoding,
            "large_keys": sorted(large_keys, key=lambda x: x[1], reverse=True)[:10]
        }
```

---

## 8️⃣ 실무 적용 요약

### 핵심 개념
- **자료구조 최적 선택**: String (락), List (큐), Hash (상태 관리)
- **Pipeline**: 대량 요청 큐 추가 시 네트워크 왕복 최소화
- **Lua Script**: 분산 락 해제, 큐 업데이트 시 원자적 처리
- **TTL**: 락, 세션, 임시 데이터의 자동 만료 관리
- **Eviction Policy**: 메모리 부족 시 LRU 기반 키 삭제
- **SCAN**: 락 키, 큐 키의 안전한 대량 조회
- **트랜잭션**: 큐 처리와 상태 업데이트의 원자적 실행
- **캐시 전략**: 요청 상태, 워커 세션의 Cache-Aside 패턴
- **모니터링**: 큐 길이, 활성 락 수, 캐시 히트율 추적

### 실제 프로젝트 적용 사례
1. **분산 락 시스템**: SET NX EX + Lua Script로 Race Condition 방지
2. **작업 큐 최적화**: Pipeline으로 대량 요청 처리 성능 향상
3. **상태 관리**: TTL 기반 캐시로 메모리 효율성 확보
4. **성능 모니터링**: Slowlog로 KEYS 명령어 병목 발견 및 개선
5. **확장성 고려**: 향후 Redis Cluster 적용을 위한 해시태그 설계

### 성능 최적화 효과
- **네트워크 왕복**: 100개 요청 → 1번 왕복 (100배 감소)
- **원자성 보장**: Lua Script로 Race Condition 완전 방지
- **메모리 효율성**: TTL로 자동 정리, LRU로 메모리 관리
- **처리 속도**: SCAN으로 안전한 대량 데이터 처리
- **응답 시간**: 전체 시스템 30% 성능 향상

### Redis Pub/Sub vs Stream vs List
```python
# 현재 프로젝트: List 기반 큐 사용
# - 장점: 단순한 FIFO, 구현 간단, 메모리 효율적
# - 단점: 메시지 손실 가능, 그룹 소비 불가

# 향후 확장 고려사항:
# - Pub/Sub: 실시간 알림, 메시지 손실 가능
# - Stream: 복잡한 메시징, 그룹 소비, 메시지 보장
# - List: 단순한 큐, 현재 프로젝트에 적합
```

---
<details>
<summary>cf. reference</summary>

- https://redis.io/docs/latest/develop/data-types/streams/
- https://kingjakeu.github.io/page2/
- https://splendidlolli.tistory.com/762
</details> 