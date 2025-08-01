---
title: "Redis 캐시 & 실무 전략"
date: 2025-08-01
categories:
  - redis
tags:
  - redis
  - cache
  - strategy
  - invalidation
---

# Redis 캐시 & 실무 전략

## 개요
Redis를 캐시로 사용할 때 데이터베이스와의 일관성을 유지하고 성능을 최적화하기 위한 전략들을 다룹니다.

---

## 1️⃣ 캐시 전략 (Cache Strategy)

### Cache-Aside (Lazy Loading)
가장 일반적인 패턴으로, 필요할 때만 캐시에 데이터를 로드합니다.

```python
def get_user(user_id):
    # 1. 캐시에서 먼저 조회
    user = redis.get(f"user:{user_id}")
    
    if user is None:
        # 2. 캐시에 없으면 DB에서 조회
        user = db.query("SELECT * FROM users WHERE id = ?", user_id)
        # 3. DB 결과를 캐시에 저장
        redis.setex(f"user:{user_id}", 3600, user)  # 1시간 TTL
    
    return user
```

**장점:**
- 구현이 간단하고 직관적
- 필요할 때만 캐시에 저장하여 메모리 효율적
- 캐시 미스 시에만 DB 부하 발생

**단점:**
- Cache Miss 시 지연 발생
- 데이터 일관성 보장이 어려움
- Race condition 가능성

### Write-Through
데이터를 업데이트할 때 DB와 캐시를 동시에 업데이트합니다.

```python
def update_user(user_id, data):
    # 1. DB 업데이트
    db.execute("UPDATE users SET name = ? WHERE id = ?", data['name'], user_id)
    # 2. 캐시도 동시에 업데이트
    redis.setex(f"user:{user_id}", 3600, data)
```

**장점:**
- 항상 최신 데이터 보장
- 읽기 성능 향상 (항상 캐시 히트)
- 데이터 일관성 보장

**단점:**
- 모든 쓰기 작업이 DB + 캐시 두 번 발생
- 쓰기 성능 저하
- 구현 복잡성 증가

### Write-Behind (Write-Back)
캐시에 먼저 저장하고 백그라운드에서 DB에 배치로 저장합니다.

```python
def update_user(user_id, data):
    # 1. 캐시에만 먼저 저장
    redis.setex(f"user:{user_id}", 3600, data)
    # 2. 백그라운드에서 DB에 배치로 저장
    background_queue.add(f"UPDATE users SET name = '{data['name']}' WHERE id = {user_id}")
```

**장점:**
- 빠른 응답 시간
- DB 부하 감소
- 배치 처리로 성능 향상

**단점:**
- 데이터 유실 위험 (서버 장애 시)
- 구현 복잡성
- 일관성 보장 어려움

---

## 2️⃣ 캐시 무효화 전략 (Cache Invalidation)

### TTL 기반 무효화
```python
# 자동으로 만료되는 캐시
redis.setex("user:1001", 3600, user_data)  # 1시간 후 자동 삭제
```

**장점:** 구현 간단, 메모리 자동 관리
**단점:** 정확한 무효화 시점 제어 어려움

### 명시적 무효화
```python
def update_user(user_id, data):
    # 1. DB 업데이트
    db.execute("UPDATE users SET name = ? WHERE id = ?", data['name'], user_id)
    # 2. 관련 캐시 삭제
    redis.delete(f"user:{user_id}")
    redis.delete(f"user_profile:{user_id}")
```

**장점:** 정확한 무효화 시점 제어
**단점:** 누락 가능성, 복잡한 의존성 관리

### 패턴 기반 무효화
```python
def update_user(user_id, data):
    # 1. DB 업데이트
    db.execute("UPDATE users SET name = ? WHERE id = ?", data['name'], user_id)
    # 2. 패턴으로 관련 캐시 모두 삭제
    keys = redis.keys(f"user:{user_id}:*")
    if keys:
        redis.delete(*keys)
```

**장점:** 관련 캐시 일괄 삭제
**단점:** KEYS 명령어 성능 이슈 (O(N))

### 버전 기반 무효화
```python
def get_user(user_id):
    # 버전 정보와 함께 캐시
    cache_key = f"user:{user_id}:v{user_version}"
    user = redis.get(cache_key)
    
    if user is None:
        user = db.query("SELECT * FROM users WHERE id = ?", user_id)
        redis.setex(cache_key, 3600, user)
    
    return user

def update_user(user_id, data):
    # 업데이트 시 버전 증가
    user_version += 1
    db.execute("UPDATE users SET name = ?, version = ? WHERE id = ?", 
               data['name'], user_version, user_id)
```

**장점:** 자연스러운 무효화, 성능 좋음
**단점:** 버전 관리 복잡성

---

## 3️⃣ 실무에서 주의할 점

### Cache Stampede 문제
동시에 여러 요청이 같은 데이터를 요청할 때 발생하는 문제입니다.

```python
# 문제 상황: 동시에 여러 요청이 같은 데이터를 요청
# 해결책: 락을 사용한 중복 요청 방지
def get_user_with_lock(user_id):
    lock_key = f"lock:user:{user_id}"
    
    # 락 획득 시도
    if redis.setnx(lock_key, 1):
        redis.expire(lock_key, 10)  # 10초 TTL
        
        try:
            user = redis.get(f"user:{user_id}")
            if user is None:
                user = db.query("SELECT * FROM users WHERE id = ?", user_id)
                redis.setex(f"user:{user_id}", 3600, user)
            return user
        finally:
            redis.delete(lock_key)
    else:
        # 락 획득 실패 시 잠시 대기 후 재시도
        time.sleep(0.1)
        return redis.get(f"user:{user_id}")
```

### Latency Spike 대응 전략

#### 1. **TTL 랜덤화로 만료 시간 분산**
```python
import random

def set_cache_with_random_ttl(key, value, base_ttl=3600):
    # 기본 TTL에 ±10% 랜덤 추가
    jitter = random.uniform(0.9, 1.1)
    ttl = int(base_ttl * jitter)
    redis.setex(key, ttl, value)
    return ttl
```

#### 2. **Background Refresh (Cache Warming)**
```python
# 백그라운드에서 인기 데이터 미리 로드
def background_refresh_cache():
    """백그라운드에서 캐시 미리 로드"""
    popular_products = db.query("SELECT * FROM products WHERE views > 1000")
    for product in popular_products:
        redis.setex(f"product:{product['id']}", 3600, json.dumps(product))
```

#### 3. **Circuit Breaker 패턴**
```python
class CacheCircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
            
            raise e
```

#### 4. **Graceful Degradation**
```python
def get_user_with_fallback(user_id):
    try:
        # 1. 캐시에서 조회
        user = redis.get(f"user:{user_id}")
        if user:
            return json.loads(user)
        
        # 2. DB에서 조회
        user = db.query("SELECT * FROM users WHERE id = ?", user_id)
        if user:
            redis.setex(f"user:{user_id}", 3600, json.dumps(user))
            return user
        
        # 3. 기본값 반환 (Graceful Degradation)
        return {"id": user_id, "name": "Unknown User", "status": "degraded"}
        
    except Exception as e:
        # 4. 에러 시에도 기본값 반환
        print(f"Cache/DB error: {e}")
        return {"id": user_id, "name": "Unknown User", "status": "error"}
```

### 부분 무효화 (Partial Invalidation)
전체 캐시 삭제 대신 필요한 부분만 삭제하는 전략입니다.

```python
def update_user_profile(user_id, profile_data):
    # 프로필만 업데이트
    db.execute("UPDATE user_profiles SET bio = ? WHERE user_id = ?", 
               profile_data['bio'], user_id)
    
    # 프로필 관련 캐시만 삭제
    redis.delete(f"user_profile:{user_id}")
    # 기본 정보 캐시는 유지
    # redis.delete(f"user:{user_id}")  # 삭제하지 않음
```

### 캐시 키 설계 전략
```python
# 좋은 캐시 키 패턴
redis.set(f"user:{user_id}:profile", profile_data)      # 명확한 구조
redis.set(f"user:{user_id}:posts:page:{page}", posts)   # 페이지네이션
redis.set(f"product:{product_id}:reviews:count", count) # 집계 데이터

# 피해야 할 패턴
redis.set(f"data", huge_data)                           # 너무 일반적
redis.set(f"user_data_very_long_key_name", data)       # 너무 긴 키
```

---

## 4️⃣ 캐시 vs DB 일관성 처리

### Cache-Aside 패턴의 일관성 문제
```python
# 문제 상황: 동시 업데이트 시 캐시와 DB 불일치
def update_user_race_condition(user_id, data):
    # 스레드 A: DB 업데이트
    db.execute("UPDATE users SET name = 'Alice' WHERE id = ?", user_id)
    
    # 스레드 B: DB 업데이트 (동시에)
    db.execute("UPDATE users SET name = 'Bob' WHERE id = ?", user_id)
    
    # 스레드 A: 캐시 업데이트
    redis.setex(f"user:{user_id}", 3600, {"name": "Alice"})
    
    # 스레드 B: 캐시 업데이트 (나중에)
    redis.setex(f"user:{user_id}", 3600, {"name": "Bob"})
    
    # 결과: DB는 'Bob', 캐시는 'Bob' (일관성 있음)
    # 하지만 스레드 A의 업데이트가 무시됨
```

### 해결 방법: 캐시 무효화
```python
def update_user_safe(user_id, data):
    # 1. DB 업데이트
    db.execute("UPDATE users SET name = ? WHERE id = ?", data['name'], user_id)
    # 2. 캐시 삭제 (다음 읽기 시 새로운 데이터 로드)
    redis.delete(f"user:{user_id}")
```

---

## 5️⃣ Redis Cluster & 복제 관련 이슈

### Redis Cluster Hash Slot 16384개 이유
Redis Cluster는 16384개(2^14)의 Hash Slot으로 데이터를 분산합니다.

**16384개인 이유:**
1. **메모리 효율성**: 16KB로 모든 슬롯 정보 저장 가능
2. **분산 균등성**: 충분한 슬롯으로 균등한 분산 보장
3. **성능**: 슬롯 계산이 빠름 (비트 연산으로 최적화)

```python
# Hash Slot 계산
def get_hash_slot(key):
    # CRC16 계산 후 16384로 모듈로 연산
    crc = crc16(key)
    return crc % 16384

# 해시태그를 사용한 동일 슬롯 보장
redis.set("user:{1001}:profile", data)  # {1001}이 해시태그
redis.set("user:{1001}:posts", posts)   # 같은 슬롯에 저장
```

### Redis 복제 지연과 데이터 유실
Redis 복제는 비동기 방식으로 데이터 유실 가능성이 있습니다.

**데이터 유실 시나리오:**
1. Master에 쓰기 요청
2. Master는 클라이언트에 성공 응답
3. Replica로 복제 전에 Master 장애
4. Replica가 Master로 승격되지만 최신 데이터 없음

**해결 방법:**
```python
# 최소 복제본 수 설정
min-replicas-to-write 1
min-replicas-max-lag 10

# 복제 지연 모니터링
def check_replication_lag():
    info = redis.info('replication')
    lag = info.get('lag', 0)
    if lag > 10:  # 10초 이상 지연
        print(f"⚠️ 복제 지연 감지: {lag}초")
```

### Redis 6+ 멀티스레드 I/O
Redis 6부터 I/O 스레드를 도입하여 네트워크 처리 성능을 향상시켰습니다.

**동작 방식:**
- **I/O 스레드**: accept, read, write만 담당
- **메인 스레드**: 명령어 파싱과 실행 담당
- **활성화 조건**: `io-threads > 1` 설정 시

```bash
# redis.conf
io-threads 4              # I/O 스레드 수
io-threads-do-reads yes   # 읽기 작업도 I/O 스레드 사용
```

**성능 향상 효과:**
- 대용량 데이터 전송 시 성능 향상
- 네트워크 I/O 병목 해소
- 단일 명령어 처리 성능은 동일 (메인 스레드가 처리)

---

## 6️⃣ 실무 적용 예시

### 사용자 세션 관리
```python
def create_user_session(user_id):
    session_data = {
        'user_id': user_id,
        'login_time': datetime.now().isoformat(),
        'permissions': get_user_permissions(user_id)
    }
    session_id = generate_session_id()
    redis.setex(f"session:{session_id}", 3600, json.dumps(session_data))
    return session_id

def invalidate_user_sessions(user_id):
    # 사용자 관련 모든 세션 삭제 (보안)
    pattern = f"session:*"
    for key in redis.scan_iter(match=pattern):
        session_data = json.loads(redis.get(key))
        if session_data['user_id'] == user_id:
            redis.delete(key)
```

### 상품 정보 캐싱
```python
def get_product_with_cache(product_id):
    cache_key = f"product:{product_id}"
    product = redis.get(cache_key)
    
    if product is None:
        product = db.query("SELECT * FROM products WHERE id = ?", product_id)
        if product:
            # 상품 정보는 자주 변경되지 않으므로 긴 TTL
            redis.setex(cache_key, 7200, json.dumps(product))  # 2시간
    
    return json.loads(product) if product else None

def update_product_inventory(product_id, quantity):
    # 재고는 실시간 업데이트 필요
    db.execute("UPDATE products SET stock = ? WHERE id = ?", quantity, product_id)
    # 재고 관련 캐시만 삭제
    redis.delete(f"product:{product_id}")
    redis.delete(f"product:{product_id}:stock")
```

---

## 7️⃣ 성능 최적화 팁

### Pipeline 사용
```python
def get_multiple_users(user_ids):
    pipe = redis.pipeline()
    for user_id in user_ids:
        pipe.get(f"user:{user_id}")
    results = pipe.execute()
    return results
```

### 적절한 TTL 설정
```python
# 데이터 특성에 따른 TTL 설정
TTL_CONFIG = {
    'user_profile': 3600,      # 1시간 (자주 변경)
    'product_info': 7200,      # 2시간 (중간 변경)
    'static_content': 86400,   # 24시간 (거의 변경 안됨)
    'session': 1800,           # 30분 (보안)
}
```

### 메모리 사용량 모니터링
```python
def monitor_cache_usage():
    info = redis.info('memory')
    used_memory = info['used_memory_human']
    max_memory = info['maxmemory_human']
    print(f"캐시 사용량: {used_memory}/{max_memory}")
```

---

## 8️⃣ 실무 체크리스트

### 캐시 설계 시 확인사항
- [ ] 적절한 캐시 전략 선택 (Cache-Aside, Write-Through, Write-Behind)
- [ ] TTL 설정 및 랜덤화 적용
- [ ] 캐시 무효화 전략 수립
- [ ] Cache Stampede 방지 로직 구현
- [ ] Graceful Degradation 고려

### 운영 시 모니터링 항목
- [ ] 캐시 히트율 (80% 이상 권장)
- [ ] 메모리 사용량
- [ ] 네트워크 지연시간
- [ ] 에러율 및 Circuit Breaker 상태
- [ ] Big Key/Hot Key 모니터링

### Cluster 환경 고려사항
- [ ] Hash Slot 분산 확인
- [ ] 복제 지연 모니터링
- [ ] MGET/MSET 제약사항 고려
- [ ] 해시태그 활용 검토

---
---
<details>
<summary>cf. reference</summary>

- https://redis.io/docs/latest/develop/data-types/streams/
- https://kingjakeu.github.io/page2/
- https://splendidlolli.tistory.com/762
</details>