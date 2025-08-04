---
title: "Redis 보안 & 트러블슈팅 (3년차 백엔드 개발자 면접용)"
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
3년차 백엔드 개발자가 면접에서 자주 받는 Redis 보안과 트러블슈팅 관련 질문들과 답변을 정리합니다.

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

## 3️⃣ O(N) 명령어 & 안전한 대안

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

## 4️⃣ 모니터링 & 예방적 점검

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

## 5️⃣ 면접 요약 포인트

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

**결론: Redis는 보안 설정과 성능 모니터링이 가장 중요합니다!**

---
<details>
<summary>cf. reference</summary>

- https://redis.io/docs/latest/operate/security/
- https://redis.io/docs/latest/operate/troubleshooting/
- https://redis.io/docs/latest/operate/monitoring/
</details>