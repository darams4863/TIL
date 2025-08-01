---
title: "Redis Lock & Transaction & Performance Optimization"
date: 2025-08-01
categories:
  - redis
tags:
  - redis
  - lock
  - transaction
  - pipeline
  - performance
---

# Redis Lock & Transaction & Performance Optimization

## 개요
Redis에서 분산 락 구현, 트랜잭션 처리, 성능 최적화 기법들을 다룹니다.

---

## 1️⃣ Redis 분산 락 (Distributed Lock)

### SETNX 기반 기본 락
```python
import redis
import time
import uuid

class RedisLock:
    def __init__(self, redis_client, lock_name, timeout=10):
        self.redis = redis_client
        self.lock_name = f"lock:{lock_name}"
        self.timeout = timeout
        self.lock_value = str(uuid.uuid4())  # 고유 식별자
    
    def acquire(self):
        """락 획득"""
        # SET key value NX EX seconds
        result = self.redis.set(
            self.lock_name, 
            self.lock_value, 
            nx=True,  # 키가 없을 때만 설정
            ex=self.timeout  # 자동 만료
        )
        return result
    
    def release(self):
        """락 해제 (자신이 획득한 락만)"""
        # Lua 스크립트로 원자적 해제
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        result = self.redis.eval(lua_script, 1, self.lock_name, self.lock_value)
        return result == 1

# 사용 예시
def process_with_lock(resource_id):
    lock = RedisLock(redis_client, f"resource:{resource_id}")
    
    if lock.acquire():
        try:
            # 임계 영역 작업
            print(f"Processing resource {resource_id}")
            time.sleep(2)
        finally:
            lock.release()
    else:
        print("Failed to acquire lock")
```

### Redlock 알고리즘
여러 Redis 인스턴스를 사용하여 더 안전한 분산 락을 구현합니다.

```python
class Redlock:
    def __init__(self, redis_instances, lock_name, timeout=10):
        self.redis_instances = redis_instances
        self.lock_name = f"lock:{lock_name}"
        self.timeout = timeout
        self.quorum = len(redis_instances) // 2 + 1
        self.lock_value = str(uuid.uuid4())
    
    def acquire(self):
        """Redlock으로 락 획득"""
        start_time = time.time()
        
        # 모든 인스턴스에서 락 획득 시도
        acquired_count = 0
        for redis_instance in self.redis_instances:
            try:
                result = redis_instance.set(
                    self.lock_name,
                    self.lock_value,
                    nx=True,
                    ex=self.timeout
                )
                if result:
                    acquired_count += 1
            except Exception:
                continue
        
        # 유효 시간 계산
        elapsed_time = time.time() - start_time
        validity_time = self.timeout - elapsed_time
        
        # 과반수 이상 획득하고 유효 시간이 남아있으면 성공
        if acquired_count >= self.quorum and validity_time > 0:
            return True, validity_time
        
        # 실패 시 획득한 락들 해제
        self.release()
        return False, 0
    
    def release(self):
        """모든 인스턴스에서 락 해제"""
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        for redis_instance in self.redis_instances:
            try:
                redis_instance.eval(lua_script, 1, self.lock_name, self.lock_value)
            except Exception:
                continue
```

### Redlock의 한계점
1. **Clock Drift**: 서버 간 시간 차이로 인한 문제
2. **Network Partition**: 네트워크 분할 시 일관성 문제
3. **GC Pause**: JVM GC로 인한 지연 문제
4. **복잡성**: 구현과 운영이 복잡함

---

## 2️⃣ Redis Transaction

### 기본 Transaction (MULTI/EXEC/DISCARD/WATCH)
```python
def basic_transaction_example():
    """기본 트랜잭션 동작"""
    pipe = redis.pipeline()
    
    try:
        # 트랜잭션 시작
        pipe.multi()
        
        # 명령어들을 큐에 추가
        pipe.set("key1", "value1")
        pipe.set("key2", "value2")
        pipe.get("key1")
        
        # 트랜잭션 실행 (모든 명령어가 성공하거나 모두 실패)
        results = pipe.execute()
        print(f"Transaction results: {results}")
        return True
        
    except Exception as e:
        # 트랜잭션 취소
        pipe.discard()
        print(f"Transaction failed: {e}")
        return False

def watch_example():
    """WATCH를 이용한 낙관적 락"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # 감시할 키 설정
            redis.watch("counter")
            
            # 현재 값 확인
            current_value = redis.get("counter")
            new_value = int(current_value or 0) + 1
            
            # 트랜잭션 시작
            pipe = redis.pipeline()
            pipe.multi()
            pipe.set("counter", new_value)
            
            # 트랜잭션 실행
            results = pipe.execute()
            print(f"Counter updated: {new_value}")
            return True
            
        except redis.WatchError:
            # 다른 클라이언트가 키를 수정함
            print(f"Watch error on attempt {attempt + 1}, retrying...")
            continue
    
    print("Failed after all retries")
    return False
```

### Optimistic Locking vs Pessimistic Locking
```python
# Optimistic Locking (WATCH 사용)
def optimistic_locking_example(user_id, new_balance):
    """낙관적 락: 충돌이 적을 때 효율적"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            redis.watch(f"user:{user_id}:balance")
            current_balance = redis.get(f"user:{user_id}:balance")
            
            pipe = redis.pipeline()
            pipe.multi()
            pipe.set(f"user:{user_id}:balance", new_balance)
            pipe.execute()
            return True
            
        except redis.WatchError:
            continue
    
    return False

# Pessimistic Locking (SETNX 사용)
def pessimistic_locking_example(resource_id):
    """비관적 락: 충돌이 많을 때 안전"""
    lock_key = f"lock:{resource_id}"
    lock_value = str(uuid.uuid4())
    
    # 락 획득 시도
    if redis.set(lock_key, lock_value, nx=True, ex=10):
        try:
            # 임계 영역 작업
            process_resource(resource_id)
            return True
        finally:
            # 락 해제 (자신의 락만)
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            redis.eval(lua_script, 1, lock_key, lock_value)
    else:
        return False
```

### 분산 환경에서의 Redlock 동작 원리
```python
class Redlock:
    def __init__(self, redis_instances, lock_name, timeout=10):
        self.redis_instances = redis_instances
        self.lock_name = f"lock:{lock_name}"
        self.timeout = timeout
        self.quorum = len(redis_instances) // 2 + 1  # 과반수
        self.lock_value = str(uuid.uuid4())
    
    def acquire(self):
        """Redlock으로 락 획득"""
        start_time = time.time()
        
        # 모든 인스턴스에서 락 획득 시도
        acquired_count = 0
        for redis_instance in self.redis_instances:
            try:
                result = redis_instance.set(
                    self.lock_name,
                    self.lock_value,
                    nx=True,
                    ex=self.timeout
                )
                if result:
                    acquired_count += 1
            except Exception:
                continue
        
        # 유효 시간 계산
        elapsed_time = time.time() - start_time
        validity_time = self.timeout - elapsed_time
        
        # 과반수 이상 획득하고 유효 시간이 남아있으면 성공
        if acquired_count >= self.quorum and validity_time > 0:
            return True, validity_time
        
        # 실패 시 획득한 락들 해제
        self.release()
        return False, 0
    
    def release(self):
        """모든 인스턴스에서 락 해제"""
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        for redis_instance in self.redis_instances:
            try:
                redis_instance.eval(lua_script, 1, self.lock_name, self.lock_value)
            except Exception:
                continue
```

### Redlock의 한계점과 실패 시나리오
```python
# Redlock의 한계점들
def redlock_limitations():
    limitations = {
        "clock_drift": "서버 간 시간 차이로 인한 문제",
        "network_partition": "네트워크 분할 시 일관성 문제", 
        "gc_pause": "JVM GC로 인한 지연 문제",
        "complexity": "구현과 운영이 복잡함"
    }
    
    # 실패 시나리오 예시
    failure_scenarios = {
        "scenario1": "과반수 노드 장애 시 락 획득 불가",
        "scenario2": "네트워크 지연으로 인한 유효 시간 초과",
        "scenario3": "Clock drift로 인한 TTL 불일치"
    }
    
    return limitations, failure_scenarios
```

### Redlock의 구체적인 한계점들

#### 1. Clock Drift 문제
```python
# 문제 시나리오
def clock_drift_scenario():
    """
    서버 간 시간 차이로 인한 문제:
    
    1. 서버 A의 시계가 10초 빠름
    2. 서버 B의 시계가 10초 늦음
    3. Redlock에서 TTL 계산 시 불일치 발생
    4. 락이 예상보다 일찍 만료되거나 늦게 만료됨
    """
    
    # 해결책: Clock drift 고려한 유효 시간 계산
    def calculate_validity_time(timeout, drift_factor=0.01):
        # Clock drift를 고려한 유효 시간 계산
        validity_time = timeout - (timeout * drift_factor)
        return max(validity_time, 0)
```

#### 2. Network Partition 문제
```python
# 문제 시나리오
def network_partition_scenario():
    """
    네트워크 분할 시 일관성 문제:
    
    1. 5개 노드 중 3개가 네트워크 분할
    2. 클라이언트 A가 분할된 3개 노드에서 락 획득
    3. 클라이언트 B가 나머지 2개 노드에서 락 획득
    4. 동시에 락을 가진 상태로 데이터 불일치 발생
    """
    
    # 해결책: 네트워크 상태 모니터링
    def monitor_network_partition():
        healthy_nodes = 0
        for node in redis_nodes:
            try:
                node.ping()
                healthy_nodes += 1
            except:
                continue
        
        if healthy_nodes < len(redis_nodes) // 2 + 1:
            print("⚠️ 네트워크 분할 감지")
            return False
        return True
```

#### 3. GC Pause 문제
```python
# 문제 시나리오
def gc_pause_scenario():
    """
    JVM GC로 인한 지연 문제:
    
    1. Redis가 JVM에서 실행 중
    2. GC가 발생하여 프로세스 일시 중단
    3. 락 TTL이 만료되었지만 해제되지 않음
    4. 다른 클라이언트가 락을 획득할 수 있음
    """
    
    # 해결책: GC 최적화 또는 네이티브 Redis 사용
    # 1. JVM GC 튜닝
    # 2. 네이티브 Redis 바이너리 사용
    # 3. 락 갱신 메커니즘 구현
```

### WATCH 기반 Optimistic Lock 실무 예시
```python
# 재고 관리 시스템 예시
def inventory_management_example():
    """재고 관리에서의 Optimistic Lock 활용"""
    
    def update_inventory(product_id, quantity):
        """재고 업데이트 (낙관적 락)"""
        max_retries = 5
        
        for attempt in range(max_retries):
            try:
                # 재고 정보 감시
                redis.watch(f"inventory:{product_id}")
                
                # 현재 재고 확인
                current_stock = redis.get(f"inventory:{product_id}")
                if current_stock is None:
                    redis.unwatch()
                    return False
                
                current_stock = int(current_stock)
                new_stock = current_stock + quantity
                
                # 재고 부족 체크
                if new_stock < 0:
                    redis.unwatch()
                    return False
                
                # 트랜잭션으로 업데이트
                pipe = redis.pipeline()
                pipe.multi()
                pipe.set(f"inventory:{product_id}", new_stock)
                pipe.incr(f"inventory:version:{product_id}")  # 버전 증가
                pipe.execute()
                
                print(f"재고 업데이트 성공: {current_stock} → {new_stock}")
                return True
                
            except redis.WatchError:
                print(f"재고 변경 감지, 재시도 {attempt + 1}")
                continue
        
        print("재고 업데이트 실패: 최대 재시도 횟수 초과")
        return False

# 사용자 프로필 업데이트 예시
def user_profile_update_example():
    """사용자 프로필 업데이트 (낙관적 락)"""
    
    def update_user_profile(user_id, profile_data):
        """사용자 프로필 업데이트"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 프로필 감시
                redis.watch(f"user:{user_id}:profile")
                
                # 현재 프로필 확인
                current_profile = redis.get(f"user:{user_id}:profile")
                if current_profile:
                    current_profile = json.loads(current_profile)
                else:
                    current_profile = {}
                
                # 프로필 병합
                updated_profile = {**current_profile, **profile_data}
                
                # 트랜잭션으로 업데이트
                pipe = redis.pipeline()
                pipe.multi()
                pipe.set(f"user:{user_id}:profile", json.dumps(updated_profile))
                pipe.set(f"user:{user_id}:updated_at", time.time())
                pipe.execute()
                
                print(f"프로필 업데이트 성공")
                return True
                
            except redis.WatchError:
                print(f"프로필 변경 감지, 재시도 {attempt + 1}")
                continue
        
        return False
```

### Pipeline + Lua Script 활용 가능성
```python
# 복잡한 비즈니스 로직을 Pipeline + Lua로 최적화
def complex_business_logic_example():
    """Pipeline과 Lua Script 조합 활용"""
    
    # 1. Pipeline으로 데이터 수집
    def collect_data_with_pipeline(user_ids):
        pipe = redis.pipeline()
        for user_id in user_ids:
            pipe.get(f"user:{user_id}:profile")
            pipe.get(f"user:{user_id}:last_login")
            pipe.get(f"user:{user_id}:points")
        return pipe.execute()
    
    # 2. Lua Script로 복잡한 계산
    complex_calculation_script = """
    local user_id = KEYS[1]
    local points_to_add = tonumber(ARGV[1])
    local multiplier = tonumber(ARGV[2])
    
    -- 현재 포인트 조회
    local current_points = redis.call('GET', 'points:' .. user_id)
    if not current_points then
        current_points = 0
    else
        current_points = tonumber(current_points)
    end
    
    -- 보너스 포인트 계산
    local bonus_points = points_to_add * multiplier
    
    -- 총 포인트 계산
    local total_points = current_points + points_to_add + bonus_points
    
    -- 포인트 업데이트
    redis.call('SET', 'points:' .. user_id, total_points)
    
    -- 포인트 히스토리 기록
    redis.call('LPUSH', 'points_history:' .. user_id, 
               string.format('%d:%d:%d', points_to_add, bonus_points, total_points))
    
    return {current_points, total_points, bonus_points}
    """
    
    def calculate_points_with_lua(user_id, points, multiplier=1.5):
        """Lua Script로 포인트 계산"""
        result = redis.eval(complex_calculation_script, 1, user_id, points, multiplier)
        return {
            'previous_points': result[0],
            'total_points': result[1],
            'bonus_points': result[2]
        }
    
    # 3. Pipeline + Lua 조합 활용
    def batch_process_users(user_ids, points):
        """여러 사용자 배치 처리"""
        # Pipeline으로 데이터 수집
        user_data = collect_data_with_pipeline(user_ids)
        
        # Lua Script로 각 사용자 처리
        results = []
        for i, user_id in enumerate(user_ids):
            if user_data[i*3]:  # 프로필이 존재하는 사용자만
                result = calculate_points_with_lua(user_id, points)
                results.append(result)
        
        return results
```

---

## 3️⃣ Pipeline 최적화

### Pipeline vs Transaction 차이점

#### Pipeline (성능 최적화)
```python
def pipeline_example():
    """Pipeline: 네트워크 왕복 최소화"""
    pipe = redis.pipeline()
    
    # 여러 명령어를 파이프라인에 추가
    pipe.set("key1", "value1")
    pipe.set("key2", "value2")
    pipe.get("key1")
    pipe.get("key2")
    
    # 한 번에 실행 (원자성 없음)
    results = pipe.execute()
    print(f"Pipeline results: {results}")

# 성능 비교
def performance_comparison():
    # 개별 실행 (느림)
    start_time = time.time()
    for i in range(1000):
        redis.set(f"key:{i}", f"value:{i}")
    individual_time = time.time() - start_time
    
    # Pipeline 사용 (빠름)
    start_time = time.time()
    pipe = redis.pipeline()
    for i in range(1000):
        pipe.set(f"key:{i}", f"value:{i}")
    pipe.execute()
    pipeline_time = time.time() - start_time
    
    print(f"Individual: {individual_time:.3f}s")
    print(f"Pipeline: {pipeline_time:.3f}s")
    print(f"Speedup: {individual_time/pipeline_time:.1f}x")
```

#### Transaction (원자성 보장)
```python
def transaction_example():
    """Transaction: 원자성 보장"""
    pipe = redis.pipeline()
    
    try:
        pipe.multi()
        
        # 모든 명령어가 성공하거나 모두 실패
        pipe.set("account:1", 100)
        pipe.set("account:2", 200)
        pipe.incr("account:1", 50)
        pipe.decr("account:2", 50)
        
        # 원자적으로 실행
        results = pipe.execute()
        print(f"Transaction results: {results}")
        return True
        
    except Exception as e:
        print(f"Transaction failed: {e}")
        return False
```

### Pipeline vs Lua Script 성능 차이
```python
# Pipeline: 네트워크 왕복 최소화
def pipeline_approach():
    pipe = redis.pipeline()
    for i in range(100):
        pipe.get(f"key:{i}")
        pipe.set(f"key:{i}", f"value:{i}")
    return pipe.execute()  # 1번의 네트워크 왕복

# Lua Script: 서버에서 처리
lua_script = """
for i = 1, 100 do
    redis.call('GET', 'key:' .. i)
    redis.call('SET', 'key:' .. i, 'value:' .. i)
end
"""
def lua_approach():
    return redis.eval(lua_script, 0)  # 1번의 네트워크 왕복

# 성능 비교:
# - Pipeline: 복잡한 로직 불가, 단순 명령어에 유리
# - Lua Script: 복잡한 로직 가능, 서버 리소스 사용
```

### MULTI/EXEC vs Pipeline의 latency 특성
```python
# MULTI/EXEC: 원자성 보장, 큐잉 오버헤드
def multi_exec_example():
    pipe = redis.pipeline()
    pipe.multi()
    pipe.set("key1", "value1")
    pipe.set("key2", "value2")
    pipe.execute()  # 큐잉 + 원자적 실행

# Pipeline: 성능 최적화, 원자성 없음
def pipeline_example():
    pipe = redis.pipeline()
    pipe.set("key1", "value1")
    pipe.set("key2", "value2")
    pipe.execute()  # 단순 배치 실행

# Latency 특성:
# - MULTI/EXEC: 큐잉 오버헤드로 약간 느림
# - Pipeline: 최소한의 오버헤드
```

### Connection Pooling과 단일 연결 과부하
```python
# 문제 상황: 단일 연결 과부하
redis_client = redis.Redis(host='localhost', port=6379)  # 단일 연결

# 해결책: Connection Pool 사용
from redis import ConnectionPool

pool = ConnectionPool(
    host='localhost', 
    port=6379, 
    max_connections=20,      # 최대 연결 수
    retry_on_timeout=True,   # 타임아웃 시 재시도
    socket_keepalive=True    # 연결 유지
)
redis_client = redis.Redis(connection_pool=pool)

# Connection Pool 모니터링
def monitor_connection_pool():
    info = redis.info('clients')
    connected_clients = info['connected_clients']
    max_clients = info['maxclients']
    print(f"연결 수: {connected_clients}/{max_clients}")
```

### Redis에서 CPU vs 메모리 병목 구분
```python
# CPU 병목 확인
def check_cpu_bottleneck():
    info = redis.info('stats')
    
    # CPU 사용량 지표
    total_commands_processed = info['total_commands_processed']
    total_connections_received = info['total_connections_received']
    
    # 명령어 처리율 계산
    commands_per_second = total_commands_processed / uptime
    
    if commands_per_second > 100000:  # 10만 명령어/초
        print("⚠️ CPU 병목 가능성")
    
    return commands_per_second

# 메모리 병목 확인
def check_memory_bottleneck():
    info = redis.info('memory')
    
    used_memory = info['used_memory']
    max_memory = info['maxmemory']
    mem_fragmentation_ratio = info['mem_fragmentation_ratio']
    
    # 메모리 사용률
    memory_usage_ratio = used_memory / max_memory if max_memory > 0 else 0
    
    if memory_usage_ratio > 0.8:  # 80% 이상
        print("⚠️ 메모리 병목 가능성")
    
    if mem_fragmentation_ratio > 1.5:  # 파편화율 1.5 이상
        print("⚠️ 메모리 파편화 문제")
    
    return memory_usage_ratio

# MONITOR 명령어로 실시간 분석
def analyze_with_monitor():
    """
    MONITOR 명령어로 실시간 명령어 분석
    주의: 성능에 영향 주므로 디버깅 시에만 사용
    """
    monitor = redis.monitor()
    for command in monitor:
        print(command)  # 실시간 명령어 출력
```

### Pipeline 최적화 전략
```python
def optimized_batch_operations():
    """배치 작업 최적화"""
    batch_size = 1000
    
    # 대량 데이터 삽입
    def insert_batch(data_list):
        pipe = redis.pipeline()
        for item in data_list:
            pipe.set(f"item:{item['id']}", json.dumps(item))
        pipe.execute()
    
    # 데이터를 배치로 나누어 처리
    all_data = [{"id": i, "value": f"data_{i}"} for i in range(10000)]
    
    for i in range(0, len(all_data), batch_size):
        batch = all_data[i:i + batch_size]
        insert_batch(batch)
        print(f"Processed batch {i//batch_size + 1}")
```

---

## 4️⃣ Lua Script 활용

### Lua Script로 원자적 연산
```python
# 복잡한 비즈니스 로직을 Lua로 구현
lua_script = """
local user_id = KEYS[1]
local amount = tonumber(ARGV[1])
local min_balance = tonumber(ARGV[2])

-- 현재 잔액 확인
local current_balance = redis.call('GET', 'balance:' .. user_id)
if not current_balance then
    return {err = 'User not found'}
end

current_balance = tonumber(current_balance)

-- 잔액 검증
if current_balance - amount < min_balance then
    return {err = 'Insufficient balance'}
end

-- 잔액 업데이트
redis.call('DECRBY', 'balance:' .. user_id, amount)
redis.call('INCRBY', 'total_withdrawn:' .. user_id, amount)

-- 새로운 잔액 반환
local new_balance = redis.call('GET', 'balance:' .. user_id)
return {ok = new_balance}
"""

def withdraw_money_atomic(user_id, amount, min_balance=0):
    """원자적 출금 처리"""
    try:
        result = redis.eval(lua_script, 1, user_id, amount, min_balance)
        
        if result.get('err'):
            print(f"Withdrawal failed: {result['err']}")
            return False
        
        print(f"Withdrawal successful. New balance: {result['ok']}")
        return True
        
    except Exception as e:
        print(f"Script execution error: {e}")
        return False
```

### Lua Script 장점
1. **원자성**: 여러 명령어를 하나의 원자적 연산으로 실행
2. **성능**: 네트워크 왕복 최소화
3. **복잡한 로직**: 조건부 처리와 반복문 지원
4. **일관성**: 데이터 일관성 보장

---

## 5️⃣ 성능 최적화 전략

### RTT (Round Trip Time) 최소화
```python
# 1. Pipeline 사용
def minimize_rtt_with_pipeline():
    pipe = redis.pipeline()
    for i in range(100):
        pipe.get(f"key:{i}")
    results = pipe.execute()  # 1번의 네트워크 왕복

# 2. Connection Pool 사용
from redis import ConnectionPool

pool = ConnectionPool(host='localhost', port=6379, max_connections=20)
redis_client = redis.Redis(connection_pool=pool)

# 3. 적절한 배치 크기
def optimal_batch_size():
    batch_sizes = [10, 50, 100, 500, 1000]
    
    for batch_size in batch_sizes:
        start_time = time.time()
        
        pipe = redis.pipeline()
        for i in range(1000):
            pipe.set(f"test:{i}", f"value:{i}")
            if (i + 1) % batch_size == 0:
                pipe.execute()
                pipe = redis.pipeline()
        
        elapsed = time.time() - start_time
        print(f"Batch size {batch_size}: {elapsed:.3f}s")
```

### Big Key 분할 전략
```python
def handle_big_hash(hash_key, chunk_size=1000):
    """큰 Hash를 청크로 분할"""
    
    def store_big_hash(data_dict):
        # 데이터를 청크로 나누기
        items = list(data_dict.items())
        chunks = [items[i:i+chunk_size] for i in range(0, len(items), chunk_size)]
        
        pipe = redis.pipeline()
        for i, chunk in enumerate(chunks):
            chunk_key = f"{hash_key}:chunk:{i}"
            pipe.hmset(chunk_key, dict(chunk))
        pipe.set(f"{hash_key}:chunks", len(chunks))
        pipe.execute()
    
    def get_big_hash():
        chunks_count = redis.get(f"{hash_key}:chunks")
        if not chunks_count:
            return {}
        
        result = {}
        pipe = redis.pipeline()
        for i in range(int(chunks_count)):
            pipe.hgetall(f"{hash_key}:chunk:{i}")
        
        chunks = pipe.execute()
        for chunk in chunks:
            result.update(chunk)
        
        return result
    
    return store_big_hash, get_big_hash
```

### Hot Key Sharding
```python
def hot_key_sharding():
    """Hot Key를 여러 Redis로 분산"""
    
    def get_sharded_key(key, shard_count=4):
        """키를 샤드로 분산"""
        import hashlib
        hash_value = hashlib.md5(key.encode()).hexdigest()
        shard_id = int(hash_value, 16) % shard_count
        return f"shard:{shard_id}:{key}"
    
    def get_from_shard(key):
        """샤드에서 데이터 조회"""
        sharded_key = get_sharded_key(key)
        return redis.get(sharded_key)
    
    def set_to_shard(key, value):
        """샤드에 데이터 저장"""
        sharded_key = get_sharded_key(key)
        return redis.set(sharded_key, value)
    
    return get_from_shard, set_to_shard
```

---

## 6️⃣ 성능 모니터링

### 성능 지표 수집
```python
def monitor_redis_performance():
    """Redis 성능 모니터링"""
    
    # 기본 지표
    info = redis.info()
    
    # 메모리 사용량
    memory_info = redis.info('memory')
    used_memory = memory_info['used_memory_human']
    max_memory = memory_info['maxmemory_human']
    
    # 명령어 통계
    command_stats = redis.info('commandstats')
    
    # 연결 정보
    client_info = redis.info('clients')
    connected_clients = client_info['connected_clients']
    
    # 성능 지표
    stats_info = redis.info('stats')
    keyspace_hits = stats_info['keyspace_hits']
    keyspace_misses = stats_info['keyspace_misses']
    
    # 히트율 계산
    hit_rate = keyspace_hits / (keyspace_hits + keyspace_misses) if (keyspace_hits + keyspace_misses) > 0 else 0
    
    print(f"Memory: {used_memory}/{max_memory}")
    print(f"Connected clients: {connected_clients}")
    print(f"Hit rate: {hit_rate:.2%}")
    
    return {
        'memory_usage': used_memory,
        'connected_clients': connected_clients,
        'hit_rate': hit_rate
    }
```

### 느린 쿼리 분석
```python
def analyze_slow_queries():
    """느린 쿼리 분석"""
    
    # 느린 쿼리 로그 조회
    slow_logs = redis.slowlog_get(10)
    
    print("Slow queries:")
    for log in slow_logs:
        print(f"ID: {log['id']}")
        print(f"Duration: {log['duration']} microseconds")
        print(f"Command: {log['command']}")
        print(f"Timestamp: {log['start_time']}")
        print("---")

# 느린 쿼리 임계값 설정
redis.config_set('slowlog-log-slower-than', 10000)  # 10ms 이상
redis.config_set('slowlog-max-len', 128)  # 최대 128개 로그 유지
```

---

## 7️⃣ 실무 체크리스트

### 분산 락 구현 시 확인사항
- [ ] TTL 설정으로 데드락 방지
- [ ] 고유 식별자로 자신의 락만 해제
- [ ] Lua 스크립트로 원자적 해제
- [ ] Redlock 고려 (높은 가용성 필요 시)

### 트랜잭션 사용 시 주의사항
- [ ] WATCH로 낙관적 락 구현
- [ ] 재시도 로직 구현
- [ ] 에러 처리 및 롤백 고려
- [ ] 성능 vs 일관성 트레이드오프

### 성능 최적화 체크리스트
- [ ] Pipeline 사용으로 RTT 최소화
- [ ] Connection Pool 설정
- [ ] Big Key 분할 처리
- [ ] Hot Key Sharding 고려
- [ ] 적절한 배치 크기 설정

---
---
<details>
<summary>cf. reference</summary>

- https://redis.io/docs/latest/develop/data-types/streams/
- https://kingjakeu.github.io/page2/
- https://splendidlolli.tistory.com/762
</details>