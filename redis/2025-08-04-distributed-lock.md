---
title: "Redis 분산 락"
date: 2025-08-04
categories:
  - redis
tags:
  - redis
  - lock
  - mutex
---


# Redis 분산 락

## 개요
Redis는 싱글 스레드라 단일 인스턴스에서는 안전하지만,
분산 환경(여러 서버/워커)에서는 여러 프로세스가 같은 자원(주문, 작업 큐 등)에 동시에 접근해 동일 작업을 중복 실행할 수 있다. 이러한 중복처리를 막기 위해 **뮤텍스**를 구현해야한다. 
*(cf. mutex (= mutual exclusion, 상호 배제)의 약자로 한번에 하나의 프로세스/스레드만 특정 자원 접근을 허용한다. 멀티 스레드/멀티 서버 환경에서 중복 실행, 데이터 꼬임을 방지한다.)*

---

## 1️⃣ Redis 분산 락 
### 왜 분산 락이 필요한가?
```python
# 문제 상황: 여러 워커에서 동시에 같은 요청 처리
# e.g. PendingManager, ProcessManager, CallbackManager가 동시에 같은 request_idx 처리 → 중복 처리 발생!

# 해결책: Redis 분산 락
async def process_request(request_idx: str, worker_id: str):
    lock_key = f"lock:queue:request:{request_idx}"
    
    # 락 획득 시도
    is_acquired, _, _ = await RedisFunction.acquire_lock(
        key=lock_key,
        request_idx=request_idx,
        worker_id=worker_id,
        expire_seconds=180  # 3분 TTL
    )
    
    if is_acquired:
        try:
            # 요청 처리 (중복 방지)
            await process_request_logic(request_idx)
        finally:
            # 자신의 락만 해제
            await RedisFunction.release_lock(lock_key, worker_id)
    else:
        print("다른 워커가 이미 처리 중")
```

### 분산 락 구현 
- 구현: 
    ```python
    import json
    import time
    from typing import Tuple

    class RedisFunction:
        DEFAULT_TIMEOUT = 180  # 3분 타임아웃
        
        @staticmethod
        async def acquire_lock(
            key: str,
            request_idx: str,
            worker_id: str,
            expire_seconds: int = DEFAULT_TIMEOUT
        ) -> Tuple[bool, str | None, str | None]:
            """락 획득 (복합키 기반) - Race Condition 방지"""
            try:
                # SET NX EX만 사용하여 원자적 락 획득
                # NX 옵션이 키 존재 여부를 내부적으로 확인하므로 별도 EXISTS 체크 불필요
                result = await set_value(
                    key=key,
                    value=worker_id,  # 워커 ID를 값으로 저장
                    ex=expire_seconds,
                    nx=True  # 키가 없을 때만 생성 (원자적 실행)
                )
                
                if not result:
                    return (False, None, None)
                return (True, worker_id, key)

            except Exception as e:
                LOGGER.error(f"요청 {request_idx}에 대한 락 획득 실패: {str(e)}")
                return (False, None, None)

        @staticmethod
        async def release_lock(
            key: str,
            worker_id: str
        ) -> Tuple[bool, str | None, str | None]:
            """락 해제 (자신이 획득한 락만) - Lua 스크립트로 원자적 실행"""
            try:
                # Lua 스크립트로 원자적 락 해제
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                
                async with await redis_pool.get_redis_connection() as redis:
                    result = await redis.eval(lua_script, 1, key, worker_id)
                    
                    if result == 1:
                        return (True, worker_id, key)
                    elif result == 0:
                        # 락이 없거나 다른 워커의 락인 경우
                        return (False, None, None)
                    else:
                        return (True, None, None)  # 락이 이미 없는 경우

            except Exception as e:
                LOGGER.error(f"락 해제 실패 - Key: {key}, Error: {str(e)}")
                return (False, None, None)
    ```
- 사용 시나리오:
    ```python
    # 1. 큐 작업 중복 방지
    async def prevent_duplicate_queue_processing(queue_key: str, request_idx: str):
        lock_key = f"lock:{queue_key}:{request_idx}"
        is_acquired, _, _ = await RedisFunction.acquire_lock(
            key=lock_key,
            request_idx=request_idx,
            worker_id=self.id
        )
        
        if is_acquired:
            try:
                # 큐에서 요청 처리
                await process_queue_request(queue_key, request_idx)
            finally:
                await RedisFunction.release_lock(lock_key, self.id)
    ```

### cf. Lua 스크립트
- **Lua 스크립트**는 Redis에서 **원자적 실행**을 보장하는 스크립트 언어입니다.

#### KEYS와 ARGV란?
- 실제 호출 예시: 
    ```python
        # Python에서 Lua 스크립트 호출 예시 
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """

        # 호출 시
        # cf. 1은 키 개수, "lock:test"는 KEYS[1], "worker-123"는 ARGV[1]
        result = await redis.eval(lua_script, 1, "lock:test", "worker-123")
    ```
- **KEYS**: Redis 키 배열
    - `KEYS[1]`: 첫 번째 키 (예: "lock:queue:request:123")
    - `KEYS[2]`: 두 번째 키 (필요시)
    - Redis에서 키를 안전하게 관리하기 위한 배열
- **ARGV**: 인자 배열  
    - `ARGV[1]`: 첫 번째 인자 (예: "worker-abc123")
    - `ARGV[2]`: 두 번째 인자 (필요시)
    - 스크립트 실행 시 전달되는 값들

#### **Lua 스크립트의 특징:**
- **원자적 실행**: Redis 서버에서 Lua 스크립트가 실행되는 동안 다른 명령어는 대기
- **단일 스레드**: Redis의 싱글 스레드 특성으로 인해 스크립트 실행 중 경쟁 상태 없음
- **성능**: 네트워크 왕복을 줄이고 복잡한 로직을 서버에서 처리

#### **Lua 스크립트 네트워크 왕복 감소 원리**
- **원자적 실행**: 
    - GET과 DEL이 하나의 트랜잭션으로 처리
- 예시:
    - ❌ Lua 스크립트 없이 (2번 왕복)
    ```python
    # 1번째 왕복: GET 명령어
    current_owner = await redis.get("lock:test")

    # 2번째 왕복: DEL 명령어 (조건 확인 후)
    if current_owner == "worker-123":
        await redis.delete("lock:test")
    ```
    - ✅ Lua 스크립트 사용 (1번 왕복)
    ```python
    # 1번의 왕복으로 모든 로직 처리
    result = await redis.eval(lua_script, 1, "lock:test", "worker-123")
    ```

#### **Lua 스크립트로 원자적 락 해제의 장점:**
- **1. 원자성 보장**
    ```python 
    # e.g. ❌ 문제가 될 수 있는 코드
    current_owner = await redis.get("lock:test")  # T1: worker-123 반환
    # 이 시점에서 다른 프로세스가 락을 변경할 수 있음!
    if current_owner == "worker-123":
        await redis.delete("lock:test")  # T2: 이미 다른 락일 수 있음

    # ✅ Lua 스크립트로 해결
    # GET과 DEL이 원자적으로 실행되어 Race Condition 없음
    ```
- **2. 성능 향상**
    - 네트워크 왕복 2회 → 1회로 감소
    - 서버에서 조건 검사와 삭제를 한 번에 처리
- **3. 안전성 향상**
    - 자신이 획득한 락만 해제 가능
    - 다른 프로세스의 락을 실수로 해제하는 문제 방지


### NX 옵션의 동작 원리
```python
# Redis 명령어: SET key value NX EX seconds
# NX (Not eXists): 키가 존재하지 않을 때만 설정

# 시나리오 1: 키가 없는 경우
await redis.set("lock:test", "worker1", nx=True, ex=180)
# 결과: True (락 획득 성공)

# 시나리오 2: 키가 이미 있는 경우  
await redis.set("lock:test", "worker2", nx=True, ex=180)
# 결과: None (락 획득 실패)

# 왜 별도 EXISTS 체크가 불필요한가?
# 1. NX 옵션이 키 존재 여부를 내부적으로 확인
# 2. Redis 싱글 스레드로 원자적 실행 보장
# 3. 네트워크 왕복 1회로 성능 향상
```

### Redlock?
- Q: “Redis 단일 인스턴스에서 락 잡으면 안전한가요?”
    ```
    단일 인스턴스 장애 시, 락 정보가 사라질 수 있고, 이 때문에 동일 작업 중복 실행 가능성이 생깁니다. 
    Redlock은 다중 Redis 인스턴스에 동일 키를 분산 저장하는 기능으로, 과반수 (e.g. 5개 중 3개 이상) 락 획득시 성공으로 간주합니다. 
    장애나 네트워크 분리 상황에도 비교적 안전하기 때문에 Redlock을 고려할 수 있습니다.
    ```

### Race Condition & Deadlock? 
#### **Race Condition**
- **정의**: 
    - 여러 스레드/프로세스가 동시에 같은 자원에 접근할 때, 실행 순서에 따라 결과가 달라지는 문제
- **❌ 개선 전 문제 상황 (Redis 분산 락 해제 시)**:
    ```python
    # 문제가 될 수 있는 코드 - Race Condition 발생 가능
    async def release_lock_unsafe(key: str, worker_id: str):
        # T1: 워커A가 GET 실행 (락 소유자 확인)
        current_owner = await redis.get("lock:queue:request:123")
        # 결과: "worker-A" 반환
        
        # T2: 이 시점에서 워커A의 락이 만료되어 자동 삭제됨
        # Redis에서 TTL 만료로 인해 키가 삭제됨
        
        # T3: 워커B가 락 획득 시도
        # 워커B: await redis.set("lock:queue:request:123", "worker-B", nx=True, ex=180)
        # 결과: 성공 (키가 없어졌으므로)
        
        # T4: 워커A가 DEL 실행 (워커B의 락을 삭제!)
        if current_owner == "worker-A":
            await redis.delete("lock:queue:request:123")  # 워커B의 락 삭제!
    ```
- **✅ 해결책 (Lua 스크립트 사용)**:
    ```python
    # Lua 스크립트로 원자적 락 해제
    async def release_lock_safe(key: str, worker_id: str):
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        # GET과 DEL이 원자적으로 실행되어 Race Condition 방지
        # TTL 만료로 인한 키 삭제와 동시에 발생하는 문제도 방지
        result = await redis.eval(lua_script, 1, key, worker_id)
    ```
- **왜 이런 Race Condition이 발생하는가?**
    ```
    시나리오 설명:

    1. 워커A가 락을 획득하고 작업 수행 중
    2. TTL 만료로 인해 Redis에서 자동으로 락 키 삭제
    3. 워커A가 작업 완료 후 락 해제 시도
    - GET으로 락 소유자 확인 (이미 삭제된 키이므로 None 반환)
    - 하지만 워커A는 여전히 자신이 락 소유자라고 생각
    4. 워커B가 동시에 락 획득 시도 (성공)
    5. 워커A가 DEL 실행 (워커B의 락 삭제!)

    결과: 워커B의 락이 의도치 않게 삭제되어 다른 워커가 동시에 작업 수행 가능
    ```

#### **Deadlock**
- **정의**: 두 개 이상의 작업이 서로 락을 기다리며 영원히 멈추는 상태
- **❌ 개선 전 문제 상황 (TTL 없이 락 획득 시)**:
    ```python
    # 문제가 될 수 있는 코드 - Deadlock 발생 가능
    async def acquire_lock_unsafe(key: str, worker_id: str):
        # TTL 없이 락 획득
        result = await redis.set(key, worker_id, nx=True)
        # 워커A가 락을 획득했지만 TTL이 없음
        
        # 만약 워커A가 크래시되거나 네트워크 문제로 락을 해제하지 못하면?
        # 다른 워커들이 영원히 락을 기다리게 됨 (Deadlock)
        
        # 워커B, 워커C가 계속 락 획득 시도하지만 실패
        # await redis.set(key, "worker-B", nx=True)  # 실패
        # await redis.set(key, "worker-C", nx=True)  # 실패
    ```
- **✅ 해결책 (TTL 설정)**:
    ```python
    # TTL로 Deadlock 방지
    async def acquire_lock_safe(key: str, worker_id: str):
        # 3분 TTL로 자동 해제 보장
        result = await redis.set(key, worker_id, nx=True, ex=180)
        # 워커A가 크래시되어도 3분 후 자동으로 락 해제
        # 다른 워커들이 3분 후 락을 획득할 수 있음
    ```

#### **실제 프로젝트에서의 적용**
```python
# 현재 프로젝트의 안전한 분산 락 구현
class RedisFunction:
    @staticmethod
    async def acquire_lock(key: str, worker_id: str, expire_seconds: int = 180):
        # ✅ TTL로 Deadlock 방지
        result = await set_value(key=key, value=worker_id, ex=expire_seconds, nx=True)
        return result is not None
    
    @staticmethod
    async def release_lock(key: str, worker_id: str):
        # ✅ Lua 스크립트로 Race Condition 방지
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        return await redis.eval(lua_script, 1, key, worker_id)
```

#### **면접에서 나올 수 있는 질문**
- **Q: "Race Condition과 Deadlock의 차이점은?"**
    ```
    답변 포인트:

    1. Race Condition
    - 정의: 실행 순서에 따라 결과가 달라지는 문제
    - 예시: 락 해제 시 GET과 DEL 사이에 다른 프로세스가 락 획득
    - 해결책: Lua 스크립트로 원자적 실행

    2. Deadlock  
    - 정의: 서로 락을 기다리며 영원히 멈추는 상태
    - 예시: TTL 없는 락에서 프로세스 크래시 시 다른 프로세스들이 영원히 대기
    - 해결책: TTL 설정으로 자동 해제 보장

    3. 실제 프로젝트 적용
    - acquire_lock: TTL로 Deadlock 방지
    - release_lock: Lua 스크립트로 Race Condition 방지
    ```


---
<details>
<summary>cf. reference</summary>

- https://redis.io/docs/latest/develop/data-types/streams/
- https://kingjakeu.github.io/page2/
- https://splendidlolli.tistory.com/762
</details> 
