---
title: "Redis 보안 & 트러블슈팅"
date: 2025-08-04
categories:
  - redis
tags:
  - redis
  - security
  - troubleshooting
---

# Redis 보안 & 트러블슈팅

## 개요
Redis 보안과 트러블슈팅 (실무 사례 중심으로)에 대해 정리해보자.

---

## 1️⃣ Redis 보안 (Security)

### 기본 보안 원칙
Redis는 기본적으로 **외부 공개 금지**가 원칙입니다.

```bash
# redis.conf 기본 설정
bind 127.0.0.1          # 로컬호스트만 접근 허용
protected-mode yes      # 보호 모드 활성화
port 6379               # 기본 포트
```

### 접근 제어 설정

#### 1. 비밀번호 설정
```bash
# Redis 5 이하: requirepass
# redis.conf
requirepass your_strong_password

# Redis 6+: ACL (Access Control List) - 더 세밀한 제어
ACL SETUSER alice on >password123 ~user:* +get +set
ACL SETUSER readonly on >password123 ~* +read
```

#### 2. 바인딩 IP 제한
```bash
# 로컬호스트만 허용 (가장 안전)
bind 127.0.0.1

# 특정 IP만 허용
bind 192.168.1.100

# ❌ 위험: 모든 IP 허용
bind 0.0.0.0
```

#### 3. TLS/SSL 활성화 (클라우드 환경에서 중요)
```bash
# redis.conf
tls-port 6380
tls-cert-file /path/to/cert.pem
tls-key-file /path/to/key.pem
```

#### 4. 위험 명령어 숨기기
```bash
# redis.conf
rename-command FLUSHALL ""
rename-command CONFIG ""
rename-command SHUTDOWN ""
rename-command DEBUG ""
```

#### 5. 방화벽/보안 그룹 설정
```bash
# UFW (Ubuntu)
sudo ufw allow from 192.168.1.0/24 to any port 6379

# AWS Security Group
# 인바운드 규칙: 6379 포트를 특정 IP에서만 허용

# Docker/Kubernetes 네트워크 정책
# 내부 네트워크로 접근 제한
```

### 면접 질문 & 답변
**Q: "Redis 보안을 어떻게 설정했나요?"**
A: "requirepass로 비밀번호를 설정하고, bind 127.0.0.1로 로컬 접근만 허용했습니다. 위험한 명령어는 rename-command로 비활성화하고, 방화벽으로 6379 포트를 제한했습니다."

**Q: "Redis를 외부에 노출하면 어떤 위험이 있나요?"**
A: "인증 없이 접근 가능하면 데이터 유출, FLUSHALL로 데이터 삭제, CONFIG 명령어로 민감 정보 노출 등의 위험이 있습니다."

---

## 2️⃣ 트러블슈팅: 실무 사례 중심

### 사례 1: 메모리 문제 (OOM)

**문제 상황:**
```bash
# 에러 메시지
OOM command not allowed when used memory > 'maxmemory'
```

**원인 분석:**
```bash
# 1. maxmemory 정책 미설정
# 2. 캐시 폭주로 메모리 부족
# 3. Big Key로 인한 메모리 점유

# 확인 방법
INFO memory | grep maxmemory
INFO memory | grep used_memory
redis-cli --bigkeys
```

**해결책:**
```bash
# 1. maxmemory 설정
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru

# 2. Big Key 모니터링 및 처리
redis-cli --bigkeys
# 큰 키 발견 시 분할 또는 삭제

# 3. UNLINK로 비동기 삭제 (DEL 대신)
def batch_delete_keys(pattern):
    cursor = 0
    while True:
        cursor, keys = redis.scan(cursor, match=pattern, count=1000)
        if keys:
            redis.unlink(*keys)  # 비동기 삭제로 블로킹 방지
        if cursor == 0:
            break
```

### 사례 2: 성능 저하 (Latency Spike)

**문제 상황:**
```bash
# Redis 응답 지연, latency spike 발생
# 클라이언트 요청이 1-2초 지연
```

**원인 분석:**
```bash
# 1. 네트워크 왕복 과다
# 2. KEYS 명령어로 대량 키 조회
# 3. RDB/AOF I/O 지연
# 4. Fork 시 메모리 복사 지연

# 확인 방법
SLOWLOG GET 10
INFO stats | grep total_commands_processed
INFO memory | grep used_memory_human
```

**해결책:**
```python
# 1. Pipeline 사용으로 네트워크 왕복 최소화
def batch_operations():
    pipe = redis.pipeline()
    for i in range(1000):
        pipe.set(f"key:{i}", f"value:{i}")
    pipe.execute()

# 2. KEYS 대신 SCAN 사용
def safe_keys_scan(pattern="*"):
    cursor = 0
    keys = []
    while True:
        cursor, batch = redis.scan(cursor, match=pattern, count=100)
        keys.extend(batch)
        if cursor == 0:
            break
    return keys

# 3. AOF 설정 최적화
# redis.conf
appendonly yes
appendfsync everysec  # always는 너무 느림
```

### 사례 3: 데이터 유실

**문제 상황:**
```bash
# 서버 재시작 후 캐시/데이터 일부 유실
# 중요 데이터가 사라짐
```

**원인 분석:**
```bash
# 1. RDB/AOF 설정 부족
# 2. 영속성 설정 미흡
# 3. 디스크 공간 부족

# 확인 방법
INFO persistence
ls -la /var/lib/redis/
```

**해결책:**
```bash
# 1. AOF 활성화 (RDB보다 우선)
# redis.conf
appendonly yes
appendfsync everysec

# 2. RDB + AOF 혼합 사용
save 900 1      # 15분에 1개 이상 변경 시 저장
save 300 10     # 5분에 10개 이상 변경 시 저장
save 60 10000   # 1분에 10000개 이상 변경 시 저장

# 3. 재시작 시 복구 전략
# AOF가 있으면 AOF로 복구, 없으면 RDB로 복구
```

### 사례 4: 복제/클러스터 문제

**문제 상황:**
```python
# Master에 쓰기 → Replica에서 읽기 시 이전 데이터 반환
redis.set("key", "new_value")  # Master
time.sleep(0.1)
value = redis.get("key")       # Replica에서 이전 값 반환
```

**원인 분석:**
```bash
# 1. Replica 지연(lag)
# 2. 네트워크 파티션
# 3. 비동기 복제로 인한 지연

# 확인 방법
INFO replication | grep lag
INFO replication | grep role
```

**해결책:**
```python
# 1. 복제 지연 모니터링
def check_replication_lag():
    info = redis.info('replication')
    # master_repl_offset - slave_repl_offset으로 lag 계산
    lag = info.get('lag', 0)
    if lag > 10:
        print(f"⚠️ 복제 지연: {lag}초")
        # 알림 발송

# 2. WAIT 명령어로 동기화 보장
def write_with_consistency(key, value):
    redis.set(key, value)
    # 최소 1개 복제본에 동기화 보장
    redis.wait(1, 1000)  # 1개 복제본, 1초 타임아웃

# 3. Redis Sentinel 사용 (자동 failover)
```

### 면접 질문 & 답변
**Q: "Redis에서 OOM 에러가 발생하면 어떻게 해결하나요?"**
A: "maxmemory와 maxmemory-policy를 설정하고, Big Key를 모니터링해서 분할하거나 삭제합니다. UNLINK를 사용해서 비동기 삭제로 블로킹을 방지합니다."

**Q: "Redis 성능이 갑자기 느려지면 어떻게 진단하나요?"**
A: "SLOWLOG로 느린 쿼리를 확인하고, KEYS 명령어 사용 여부를 체크합니다. Pipeline 사용과 SCAN으로 대체하는 방법을 적용합니다."

**Q: "RDB와 AOF를 동시에 사용할 때 주의할 점은?"**
A: "AOF가 RDB보다 우선됩니다. 재시작 시 AOF가 있으면 AOF로 복구하고, 없으면 RDB로 복구합니다. appendfsync everysec로 성능과 안정성의 균형을 맞춥니다."

---

## 3️⃣ 실무 최적화 패턴

### 패턴 1: 분산 락 시스템 보안 강화

**문제 상황:**
```python
# 현재 프로젝트의 분산 락 시스템에서 발생할 수 있는 보안 문제
# 1. 락 키 패턴 노출로 인한 무차별 대입 공격
# 2. TTL 만료로 인한 락 무효화
# 3. 워커 ID 스푸핑 공격
```

**보안 강화 해결책:**
```python
# 1. 락 키 패턴 난독화 및 접근 제한
class SecureRedisFunction:
    @staticmethod
    async def acquire_lock_secure(
        key: str, 
        request_idx: str, 
        worker_id: str, 
        expire_seconds: int = 180
    ) -> Tuple[bool, str | None, str | None]:
        """보안 강화된 락 획득"""
        try:
            # 락 키 패턴 난독화
            secure_key = f"l:{hashlib.sha256(key.encode()).hexdigest()[:16]}"
            
            # 워커 ID 검증 (실제 프로젝트에서 사용하는 워커 ID 패턴)
            if not re.match(r'^worker-[a-f0-9]{8}$', worker_id):
                LOGGER.warning(f"잘못된 워커 ID 패턴: {worker_id}")
                return (False, None, None)
            
            # 락 획득 시도
            result = await set_value(
                key=secure_key,
                value=f"{worker_id}:{int(time.time())}",  # 타임스탬프 추가
                ex=expire_seconds,
                nx=True
            )
            
            if not result:
                return (False, None, None)
            
            return (True, worker_id, secure_key)
            
        except Exception as e:
            LOGGER.error(f"보안 락 획득 실패: {str(e)}")
            return (False, None, None)

# 2. 락 해제 시 추가 검증
@staticmethod
async def release_lock_secure(key: str, worker_id: str) -> Tuple[bool, str | None, str | None]:
    """보안 강화된 락 해제"""
    try:
        # Lua 스크립트로 원자적 검증 및 해제
        lua_script = """
        local lock_key = KEYS[1]
        local worker_id = ARGV[1]
        local current_time = tonumber(ARGV[2])
        
        local lock_value = redis.call("get", lock_key)
        if not lock_value then
            return 0
        end
        
        local stored_worker_id, timestamp = string.match(lock_value, "([^:]+):(%d+)")
        if stored_worker_id ~= worker_id then
            return 0
        end
        
        -- 타임스탬프 검증 (5분 이상 된 락은 무시)
        if current_time - tonumber(timestamp) > 300 then
            redis.call("del", lock_key)
            return 0
        end
        
        return redis.call("del", lock_key)
        """
        
        async with await redis_pool.get_redis_connection() as redis:
            result = await redis.eval(
                lua_script, 
                1, 
                key, 
                worker_id, 
                int(time.time())
            )
            
            if result == 1:
                return (True, worker_id, key)
            else:
                return (False, None, None)
                
    except Exception as e:
        LOGGER.error(f"보안 락 해제 실패: {str(e)}")
        return (False, None, None)
```

### 패턴 2: 작업 큐 시스템 트러블슈팅

**문제 상황:**
```python
# 현재 프로젝트의 작업 큐에서 발생할 수 있는 문제
# 1. 큐에 쌓인 요청이 너무 많아 메모리 부족
# 2. 특정 요청이 큐에서 사라짐 (데이터 유실)
# 3. 큐 처리 속도가 느려짐 (성능 저하)
```

**트러블슈팅 해결책:**
```python
# 1. 큐 모니터링 및 자동 정리
class QueueMonitor:
    @staticmethod
    async def monitor_queue_health():
        """큐 상태 모니터링 및 자동 정리"""
        try:
            async with await redis_pool.get_redis_connection() as redis:
                # 큐 길이 확인
                queue_length = await redis.llen("queue:requests")
                
                # 큐가 너무 길면 경고
                if queue_length > 10000:
                    LOGGER.warning(f"큐 길이 초과: {queue_length}")
                    # 알림 발송
                    await send_alert(f"큐 길이 {queue_length} 초과")
                
                # 오래된 요청 정리 (30분 이상)
                await QueueMonitor.cleanup_old_requests(redis)
                
                # 큐 처리 속도 모니터링
                await QueueMonitor.monitor_processing_rate(redis)
                
        except Exception as e:
            LOGGER.error(f"큐 모니터링 실패: {str(e)}")
    
    @staticmethod
    async def cleanup_old_requests(redis):
        """오래된 요청 정리"""
        try:
            # 큐의 모든 요청을 확인 (SCAN 사용)
            requests = await redis.lrange("queue:requests", 0, -1)
            current_time = time.time()
            
            for i, request_data in enumerate(requests):
                try:
                    request = json.loads(request_data)
                    request_time = request.get('timestamp', 0)
                    
                    # 30분 이상 된 요청 제거
                    if current_time - request_time > 1800:
                        await redis.lrem("queue:requests", 1, request_data)
                        LOGGER.info(f"오래된 요청 제거: {request.get('idx', 'unknown')}")
                        
                except json.JSONDecodeError:
                    # 잘못된 JSON 데이터 제거
                    await redis.lrem("queue:requests", 1, request_data)
                    LOGGER.warning("잘못된 JSON 데이터 제거")
                    
        except Exception as e:
            LOGGER.error(f"오래된 요청 정리 실패: {str(e)}")
    
    @staticmethod
    async def monitor_processing_rate(redis):
        """큐 처리 속도 모니터링"""
        try:
            # 처리된 요청 수 확인
            processed_count = await redis.get("stats:processed_requests")
            if processed_count:
                processed_count = int(processed_count)
                
                # 1분당 처리 속도 계산
                current_time = time.time()
                last_check = await redis.get("stats:last_check_time")
                
                if last_check:
                    last_check = float(last_check)
                    time_diff = current_time - last_check
                    
                    if time_diff >= 60:  # 1분마다 체크
                        rate = processed_count / (time_diff / 60)
                        
                        if rate < 10:  # 분당 10개 미만이면 경고
                            LOGGER.warning(f"큐 처리 속도 저하: {rate:.1f}/분")
                            await send_alert(f"큐 처리 속도 {rate:.1f}/분")
                        
                        # 통계 초기화
                        await redis.set("stats:processed_requests", 0)
                        await redis.set("stats:last_check_time", current_time)
                        
        except Exception as e:
            LOGGER.error(f"처리 속도 모니터링 실패: {str(e)}")

# 2. 큐 백업 및 복구
class QueueBackup:
    @staticmethod
    async def backup_queue():
        """큐 데이터 백업"""
        try:
            async with await redis_pool.get_redis_connection() as redis:
                # 큐 데이터 백업
                requests = await redis.lrange("queue:requests", 0, -1)
                backup_data = {
                    "timestamp": time.time(),
                    "requests": requests,
                    "count": len(requests)
                }
                
                # 백업 데이터 저장
                await redis.setex(
                    "backup:queue:requests", 
                    3600,  # 1시간 TTL
                    json.dumps(backup_data)
                )
                
                LOGGER.info(f"큐 백업 완료: {len(requests)}개 요청")
                
        except Exception as e:
            LOGGER.error(f"큐 백업 실패: {str(e)}")
    
    @staticmethod
    async def restore_queue():
        """큐 데이터 복구"""
        try:
            async with await redis_pool.get_redis_connection() as redis:
                # 백업 데이터 조회
                backup_data = await redis.get("backup:queue:requests")
                
                if backup_data:
                    backup = json.loads(backup_data)
                    requests = backup.get("requests", [])
                    
                    # 큐 복구
                    if requests:
                        async with redis.pipeline(transaction=True) as pipe:
                            for request in requests:
                                pipe.rpush("queue:requests", request)
                            await pipe.execute()
                        
                        LOGGER.info(f"큐 복구 완료: {len(requests)}개 요청")
                        return True
                        
        except Exception as e:
            LOGGER.error(f"큐 복구 실패: {str(e)}")
            return False
```

### 패턴 3: 성능 최적화 및 모니터링

**성능 최적화 적용:**
```python
# 1. 대량 요청 처리 최적화
class OptimizedQueueProcessor:
    @staticmethod
    async def batch_enqueue_requests_optimized(queue_key: str, requests: list):
        """최적화된 대량 요청 큐 추가"""
        try:
            batch_size = 100  # 적절한 배치 크기
            total_processed = 0
            
            for i in range(0, len(requests), batch_size):
                batch = requests[i:i + batch_size]
                
                async with await redis_pool.get_redis_connection() as redis:
                    async with redis.pipeline(transaction=True) as pipe:
                        for request in batch:
                            # 요청에 타임스탬프 추가
                            request['timestamp'] = time.time()
                            pipe.rpush(queue_key, json.dumps(request))
                        
                        await pipe.execute()
                        total_processed += len(batch)
                
                # 배치 간 짧은 대기 (Redis 부하 분산)
                await asyncio.sleep(0.01)
            
            # 처리 통계 업데이트
            await OptimizedQueueProcessor.update_processing_stats(total_processed)
            
            LOGGER.info(f"대량 요청 처리 완료: {total_processed}개")
            
        except Exception as e:
            LOGGER.error(f"대량 요청 처리 실패: {str(e)}")
    
    @staticmethod
    async def update_processing_stats(processed_count: int):
        """처리 통계 업데이트"""
        try:
            async with await redis_pool.get_redis_connection() as redis:
                # 처리된 요청 수 증가
                await redis.incr("stats:processed_requests", processed_count)
                
                # 마지막 처리 시간 업데이트
                await redis.set("stats:last_processing_time", time.time())
                
        except Exception as e:
            LOGGER.error(f"통계 업데이트 실패: {str(e)}")

# 2. 실시간 성능 모니터링
class PerformanceMonitor:
    @staticmethod
    async def monitor_redis_performance():
        """Redis 성능 실시간 모니터링"""
        try:
            async with await redis_pool.get_redis_connection() as redis:
                # 기본 정보 수집
                info = await redis.info()
                memory_info = await redis.info('memory')
                stats_info = await redis.info('stats')
                
                # 성능 지표 계산
                performance_metrics = {
                    "memory_usage": memory_info['used_memory_human'],
                    "max_memory": memory_info['maxmemory_human'],
                    "connected_clients": info['connected_clients'],
                    "total_commands": stats_info['total_commands_processed'],
                    "keyspace_hits": stats_info['keyspace_hits'],
                    "keyspace_misses": stats_info['keyspace_misses'],
                    "queue_length": await redis.llen("queue:requests"),
                    "active_locks": len(await safe_scan("lock:queue:request:*"))
                }
                
                # 히트율 계산
                total_requests = performance_metrics['keyspace_hits'] + performance_metrics['keyspace_misses']
                if total_requests > 0:
                    performance_metrics['hit_rate'] = performance_metrics['keyspace_hits'] / total_requests
                else:
                    performance_metrics['hit_rate'] = 0
                
                # 성능 경고 체크
                await PerformanceMonitor.check_performance_alerts(performance_metrics)
                
                return performance_metrics
                
        except Exception as e:
            LOGGER.error(f"성능 모니터링 실패: {str(e)}")
            return None
    
    @staticmethod
    async def check_performance_alerts(metrics: dict):
        """성능 경고 체크"""
        try:
            # 메모리 사용량 경고
            if metrics['memory_usage'] and metrics['max_memory']:
                memory_usage_gb = float(metrics['memory_usage'].replace('G', ''))
                max_memory_gb = float(metrics['max_memory'].replace('G', ''))
                
                if memory_usage_gb / max_memory_gb > 0.8:
                    await send_alert(f"메모리 사용량 80% 초과: {metrics['memory_usage']}")
            
            # 히트율 경고
            if metrics['hit_rate'] < 0.8:
                await send_alert(f"캐시 히트율 저하: {metrics['hit_rate']:.2%}")
            
            # 연결 수 경고
            if metrics['connected_clients'] > 1000:
                await send_alert(f"연결 수 초과: {metrics['connected_clients']}")
            
            # 큐 길이 경고
            if metrics['queue_length'] > 10000:
                await send_alert(f"큐 길이 초과: {metrics['queue_length']}")
                
        except Exception as e:
            LOGGER.error(f"성능 경고 체크 실패: {str(e)}")
```

### 면접 질문 & 답변
**Q: "실제 프로젝트에서 Redis 보안 문제를 어떻게 해결했나요?"**
A: "분산 락 시스템에서 락 키 패턴을 난독화하고, 워커 ID 검증을 추가했습니다. Lua 스크립트로 타임스탬프 검증까지 포함하여 스푸핑 공격을 방지했습니다."

**Q: "작업 큐에서 데이터 유실 문제를 어떻게 해결했나요?"**
A: "큐 모니터링 시스템을 구축하여 오래된 요청을 자동으로 정리하고, 백업/복구 기능을 추가했습니다. 처리 속도 모니터링으로 성능 저하를 사전에 감지합니다."

**Q: "Redis 성능 최적화를 어떻게 적용했나요?"**
A: "Pipeline으로 대량 요청 처리 성능을 향상시키고, 실시간 성능 모니터링으로 메모리 사용량, 히트율, 큐 길이를 추적합니다. 성능 저하 시 자동 알림을 발송합니다."

---

## 4️⃣ O(N) 명령어 & 안전한 대안

### 위험한 명령어들
```bash
# O(N) 명령어 - 대규모 데이터에서 위험
KEYS pattern          # 모든 키 검색
SMEMBERS set_name     # Set 전체 멤버 조회
LRANGE list_name 0 -1 # List 전체 조회
HGETALL hash_name     # Hash 전체 조회
ZRANGE zset_name 0 -1 # Sorted Set 전체 조회
DEL key               # 대량 삭제 시 블로킹
```

### 안전한 대안
```python
# KEYS 대신 SCAN 사용
def safe_keys_scan(pattern="*", batch_size=100):
    cursor = 0
    keys = []
    while True:
        cursor, batch = redis.scan(cursor, match=pattern, count=batch_size)
        keys.extend(batch)
        if cursor == 0:
            break
    return keys

# SMEMBERS 대신 SSCAN 사용
def safe_set_members(set_name, batch_size=100):
    cursor = 0
    members = []
    while True:
        cursor, batch = redis.sscan(set_name, cursor, count=batch_size)
        members.extend(batch)
        if cursor == 0:
            break
    return members

# DEL 대신 UNLINK 사용 (비동기 삭제)
def safe_delete_keys(keys):
    redis.unlink(*keys)  # 블로킹 없이 비동기 삭제
```

### 면접 질문 & 답변
**Q: "KEYS 명령어가 왜 위험한가요?"**
A: "O(N) 복잡도로 대량 데이터에서 Redis를 블로킹할 수 있습니다. SCAN을 사용해서 점진적으로 조회하는 것이 안전합니다."

**Q: "대량 데이터 삭제 시 주의할 점은?"**
A: "DEL은 블로킹이므로 UNLINK를 사용해서 비동기 삭제를 합니다. 이렇게 하면 다른 명령어 처리에 영향을 주지 않습니다."

---

## 5️⃣ 모니터링 & 예방적 점검

### 기본 모니터링 명령어
```bash
# 서버 정보
INFO server
INFO clients
INFO memory
INFO stats
INFO replication

# 느린 쿼리 로그
SLOWLOG GET 10

# 메모리 사용량
MEMORY USAGE key_name
MEMORY STATS
```

### 성능 지표 해석
```python
def monitor_redis_performance():
    """Redis 성능 모니터링"""
    info = redis.info()
    
    # 메모리 사용량
    memory_info = redis.info('memory')
    used_memory = memory_info['used_memory_human']
    max_memory = memory_info['maxmemory_human']
    
    # 성능 지표
    stats_info = redis.info('stats')
    keyspace_hits = stats_info['keyspace_hits']
    keyspace_misses = stats_info['keyspace_misses']
    hit_rate = keyspace_hits / (keyspace_hits + keyspace_misses)
    
    # 연결 정보
    clients_info = redis.info('clients')
    connected_clients = clients_info['connected_clients']
    
    print(f"메모리: {used_memory}/{max_memory}")
    print(f"히트율: {hit_rate:.2%}")
    print(f"연결 수: {connected_clients}")
    
    return {
        'memory_usage': used_memory,
        'hit_rate': hit_rate,
        'connected_clients': connected_clients
    }
```

### Slowlog 활용
```python
def analyze_slow_queries():
    """느린 쿼리 분석"""
    slow_logs = redis.slowlog_get(10)
    
    print("=== 느린 쿼리 분석 ===")
    for i, log in enumerate(slow_logs):
        duration_ms = log['duration'] / 1000
        command = ' '.join(log['command'])
        
        print(f"{i+1}. 지속시간: {duration_ms:.2f}ms")
        print(f"   명령어: {command}")
        
        # 위험한 명령어 체크
        if 'KEYS' in command:
            print("⚠️ KEYS 명령어 사용 - 성능 위험")
        if 'FLUSHALL' in command:
            print("🚨 FLUSHALL 명령어 사용 - 데이터 위험")
```

### BigKeys 분석
```bash
# Big Key 모니터링
redis-cli --bigkeys

# 메모리 사용량 상세 분석
MEMORY USAGE key_name
MEMORY STATS
```

### 헬스 체크
```python
def health_check():
    """Redis 헬스 체크"""
    try:
        r = redis.Redis(host='localhost', port=6379)
        
        # 기본 연결 확인
        r.ping()
        
        # 메모리 사용량 확인
        info = r.info('memory')
        used_memory = info['used_memory']
        max_memory = info['maxmemory']
        
        if used_memory > max_memory * 0.8:
            print("⚠️ 메모리 사용량 80% 초과")
        
        # 연결 수 확인
        clients_info = r.info('clients')
        connected_clients = clients_info['connected_clients']
        
        if connected_clients > 1000:
            print("⚠️ 연결 수 1000개 초과")
            
        return True
        
    except Exception as e:
        print(f"❌ Redis 연결 실패: {e}")
        return False
```

### 면접 질문 & 답변
**Q: "Redis 성능을 어떻게 모니터링하나요?"**
A: "INFO 명령어로 메모리, 연결 수, 히트율을 확인하고, SLOWLOG로 느린 쿼리를 분석합니다. BigKeys 분석으로 메모리 사용량을 모니터링합니다."

**Q: "실제 프로젝트에서 Redis 성능 문제를 어떻게 해결했나요?"**
A: "SLOWLOG로 KEYS 명령어 병목을 발견하고, SCAN으로 변경하여 응답 시간을 50% 단축했습니다. UNLINK 사용으로 대량 삭제 시 블로킹도 해결했습니다."

---

## 6️⃣ 면접 요약 포인트

### 핵심 개념
- **보안**: requirepass, ACL, bind IP, TLS, 위험 명령어 숨기기, 방화벽
- **성능**: Pipeline, SCAN, SLOWLOG, O(N) 명령어 주의, UNLINK
- **안정성**: maxmemory + eviction, RDB/AOF, TTL
- **트러블슈팅**: OOM, latency spike, 복제 지연, 데이터 유실

### 면접 질문 & 답변
**Q: "Redis 보안을 어떻게 설정했나요?"**
A: "requirepass로 비밀번호를 설정하고, bind 127.0.0.1로 로컬 접근만 허용했습니다. 위험한 명령어는 rename-command로 비활성화하고, 방화벽으로 6379 포트를 제한했습니다."

**Q: "Redis에서 OOM 에러가 발생하면 어떻게 해결하나요?"**
A: "maxmemory와 maxmemory-policy를 설정하고, Big Key를 모니터링해서 분할하거나 삭제합니다. UNLINK를 사용해서 비동기 삭제로 블로킹을 방지합니다."

**Q: "Redis 성능이 갑자기 느려지면 어떻게 진단하나요?"**
A: "SLOWLOG로 느린 쿼리를 확인하고, KEYS 명령어 사용 여부를 체크합니다. Pipeline 사용과 SCAN으로 대체하는 방법을 적용합니다."

**Q: "실제 프로젝트에서 Redis 문제를 어떻게 해결했나요?"**
A: "SLOWLOG로 KEYS 명령어 병목을 발견하고, SCAN으로 변경하여 응답 시간을 50% 단축했습니다. UNLINK 사용으로 대량 삭제 시 블로킹도 해결했습니다."

### 면접 답변 포인트
1. **보안 우선**: 외부 노출 금지, 인증 필수, 방화벽 설정
2. **성능 모니터링**: SLOWLOG, INFO 명령어, BigKeys 분석 활용
3. **실무 경험**: 실제 문제 해결 사례 언급 (구체적 수치 포함)
4. **예방적 조치**: maxmemory, TTL, 위험 명령어 제한
5. **트러블슈팅**: 체계적인 진단과 해결 방법


---
<details>
<summary>cf. reference</summary>

- https://redis.io/docs/latest/operate/security/
- https://redis.io/docs/latest/operate/troubleshooting/
- https://redis.io/docs/latest/operate/monitoring/
</details> 