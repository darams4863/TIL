---
title: "Redis 보안 & 트러블슈팅"
date: 2025-08-01
categories:
  - redis
tags:
  - redis
  - security
  - troubleshooting
  - performance
---

# Redis 보안 & 트러블슈팅

## 개요
Redis 운영 시 발생할 수 있는 보안 위험과 성능 문제들을 다루며, 실무에서 자주 발생하는 트러블슈팅 사례들을 정리합니다.

---

## 1️⃣ Redis 보안 설정

### 기본 보안 원칙
Redis는 기본적으로 **외부 공개 금지**가 원칙입니다.

```bash
# redis.conf 기본 설정
bind 127.0.0.1          # 로컬호스트만 접근 허용
protected-mode yes      # 보호 모드 활성화
port 6379               # 기본 포트
```

### 인증 설정

#### Redis 5 이하: requirepass
```bash
# redis.conf
requirepass your_strong_password

# 클라이언트 연결 시
redis-cli -a your_strong_password
```

#### Redis 6+: ACL (Access Control List)
```bash
# ACL 사용자 생성
ACL SETUSER alice on >password123 ~user:* +get +set

# 특정 명령어만 허용
ACL SETUSER readonly on >password123 ~* +read

# 관리자 권한
ACL SETUSER admin on >adminpass ~* +@all
```

### TLS/SSL 설정
```bash
# redis.conf
tls-port 6380
tls-cert-file /path/to/cert.pem
tls-key-file /path/to/key.pem
tls-ca-cert-file /path/to/ca.pem
```

### 위험 명령어 숨기기
```bash
# redis.conf
rename-command FLUSHALL ""
rename-command CONFIG ""
rename-command SHUTDOWN ""
rename-command DEBUG ""
```

### Protected-mode 동작 원리
```bash
# Protected-mode가 활성화되면:
# 1. bind가 127.0.0.1로 설정되어 있지 않으면
# 2. 외부에서 접근 시도 시 연결 거부
# 3. 로그에 경고 메시지 출력

# 해제하려면 (권장하지 않음)
protected-mode no
```

### CONFIG 명령어 노출 위험
```bash
# CONFIG 명령어로 민감한 정보 노출 가능
CONFIG GET *                    # 모든 설정 조회
CONFIG GET requirepass          # 패스워드 확인
CONFIG GET bind                 # 바인딩 주소 확인

# 해결책: CONFIG 명령어 비활성화
rename-command CONFIG ""

# 또는 ACL로 제한
ACL SETUSER readonly on >password123 ~* +read -config
```

### Redis 6+ 보안 강화 기능
```bash
# 1. ACL (Access Control List)
# - 사용자별 권한 관리
# - 명령어별 접근 제어
# - 패턴 기반 키 접근 제어

# 2. TLS/SSL 지원
# - 암호화된 통신
# - 인증서 기반 인증

# 3. RESP3 프로토콜
# - 더 나은 타입 안전성
# - 향상된 보안 기능
```

### 운영 환경에서 Redis를 공개 IP에 노출하면 안 되는 이유
```bash
# 🚨 위험한 설정 예시
bind 0.0.0.0          # 모든 IP에서 접근 허용
protected-mode no     # 보호 모드 비활성화
# requirepass 없음     # 인증 없음

# 실제 보안 사고 사례:
# 1. Redis가 공개 IP에 노출되어 전 세계에서 스캔
# 2. 기본 설정으로 인증 없이 접근 가능
# 3. FLUSHALL, CONFIG 등 위험 명령어 실행
# 4. 데이터 삭제 또는 서버 장애 발생
```

**해결책:**
```bash
# 안전한 설정
bind 127.0.0.1          # 로컬호스트만 허용
protected-mode yes      # 보호 모드 활성화
requirepass strong_password  # 강력한 패스워드 설정

# 또는 내부 네트워크만 허용
bind 192.168.1.100      # 특정 IP만 허용
```

### INFO, MONITOR 등 민감 정보 노출 위험
```bash
# 🚨 위험한 명령어들
INFO server              # 서버 정보 노출
INFO clients             # 연결된 클라이언트 정보
INFO memory              # 메모리 사용량 정보
INFO keyspace            # 데이터베이스 정보
MONITOR                  # 실시간 명령어 모니터링 (성능 저하)

# 노출되는 민감 정보:
# - 서버 버전, 운영체제 정보
# - 메모리 사용량, 키 개수
# - 연결된 클라이언트 IP/포트
# - 실시간 명령어 내용
```

**해결책:**
```bash
# 위험 명령어 비활성화
rename-command INFO ""
rename-command MONITOR ""
rename-command CONFIG ""

# 또는 ACL로 제한
ACL SETUSER readonly on >password123 ~* +read -info -monitor -config
```

### 실제 보안 사고 사례와 대응
```python
# 사고 시나리오 1: 무차별 대입 공격
def brute_force_attack_scenario():
    """
    공격자가 Redis에 무차별 대입 공격을 시도하는 경우
    """
    # 공격 패턴
    common_passwords = ["", "redis", "123456", "password", "admin"]
    
    # 대응 방법
    def prevent_brute_force():
        # 1. 강력한 패스워드 설정
        requirepass "complex_password_with_special_chars_123!"
        
        # 2. ACL로 로그인 시도 제한
        ACL SETUSER attacker off >password123 ~* +@all
        
        # 3. 방화벽으로 접근 IP 제한
        # iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 6379 -j ACCEPT

# 사고 시나리오 2: 데이터 유출
def data_leakage_scenario():
    """
    Redis가 공개 IP에 노출되어 데이터가 유출되는 경우
    """
    # 위험한 상황
    # 1. Redis가 0.0.0.0:6379에 바인딩
    # 2. 인증 없이 접근 가능
    # 3. 민감한 데이터가 평문으로 저장
    
    # 대응 방법
    def secure_redis():
        # 1. 바인딩 주소 제한
        bind 127.0.0.1
        
        # 2. TLS/SSL 활성화
        tls-port 6380
        tls-cert-file /path/to/cert.pem
        
        # 3. 데이터 암호화
        # 민감한 데이터는 애플리케이션 레벨에서 암호화
```

---

## 2️⃣ 네트워크 보안

### 방화벽 설정
```bash
# UFW (Ubuntu)
sudo ufw allow from 192.168.1.0/24 to any port 6379

# iptables
iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 6379 -j ACCEPT
iptables -A INPUT -p tcp --dport 6379 -j DROP
```

### VPC/보안 그룹 설정
```bash
# AWS Security Group 예시
# 인바운드 규칙: 6379 포트를 특정 IP에서만 허용
Type: Custom TCP
Port: 6379
Source: 10.0.1.0/24 (내부 네트워크)
```

### Redis Sentinel/Cluster 보안
```bash
# Sentinel 설정
sentinel auth-pass mymaster your_password
sentinel down-after-milliseconds mymaster 5000

# Cluster 설정
cluster-require-full-coverage no
cluster-node-timeout 15000
```

---

## 3️⃣ 트러블슈팅: 실무 사례 중심

### 사례 1: TTL 수백만 개 설정 시 Latency Spike 발생

**문제 상황:**
```python
# 문제가 있는 코드
for i in range(1000000):
    redis.setex(f"session:{i}", 3600, session_data)  # 모두 1시간 후 만료
```

**원인 분석:**
```bash
# Active Expiration으로 인한 CPU Burst
# 1. Redis는 10초마다 만료된 키를 정리
# 2. 수백만 개 키가 동시에 만료되면 CPU 사용량 급증
# 3. 다른 명령어 처리 지연 발생

# 모니터링으로 확인
INFO stats | grep expired_keys
INFO memory | grep mem_fragmentation_ratio
```

**해결책:**
```python
# 1. TTL 랜덤화로 만료 시간 분산
import random
for i in range(1000000):
    ttl = 3600 + random.randint(-300, 300)  # 3300~3900초
    redis.setex(f"session:{i}", ttl, session_data)

# 2. 슬로우키 설정으로 만료 처리 속도 조절
# redis.conf
hz 10  # 기본값 10, 낮출수록 만료 처리 빈도 감소

# 3. 배치로 TTL 설정
def batch_set_ttl(keys, base_ttl=3600):
    pipe = redis.pipeline()
    for key in keys:
        ttl = base_ttl + random.randint(-300, 300)
        pipe.expire(key, ttl)
    pipe.execute()
```

### 사례 2: Fork 시 I/O 블로킹 발생

**문제 상황:**
```bash
# RDB 저장 시 서비스 응답 지연
# 클라이언트 요청이 1-2초 지연되는 현상 발생
```

**원인 분석:**
```bash
# Fork()로 인한 메모리 복사
# 1. RDB 저장 시 fork() 호출
# 2. 메모리 페이지 복사로 인한 지연
# 3. 대용량 메모리일수록 지연 심화

# 모니터링
INFO stats | grep fork
INFO memory | grep used_memory_human
```

**해결책:**
```bash
# 1. RDB Save 시점 조절
# redis.conf
save 900 1      # 15분에 1개 이상 변경 시 저장
save 300 10     # 5분에 10개 이상 변경 시 저장
save 60 10000   # 1분에 10000개 이상 변경 시 저장

# 2. save 대신 bgsave + Replica 활용
# Master에서는 RDB 저장 비활성화
save ""
# Replica에서만 RDB 저장
save 900 1

# 3. 메모리 최적화
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### 사례 3: 클러스터에서 MGET 불가

**문제 상황:**
```python
# 클러스터 환경에서 MGET 실패
keys = ["user:1", "user:2", "user:3"]
redis.mget(keys)  # CROSSSLOT Keys in request don't hash to the same slot
```

**원인 분석:**
```bash
# Hash Slot 분산
# 1. 각 키가 다른 Hash Slot에 분산
# 2. MGET은 단일 슬롯에서만 동작
# 3. 클러스터 모드에서는 제약사항
```

**해결책:**
```python
# 1. Hash Tag 활용
# 같은 태그를 가진 키는 같은 슬롯에 저장
redis.set("user:{1}:profile", data1)
redis.set("user:{1}:posts", data2)
redis.set("user:{1}:settings", data3)

# 이제 MGET 가능
redis.mget(["user:{1}:profile", "user:{1}:posts", "user:{1}:settings"])

# 2. Pipeline으로 개별 GET
def cluster_mget(keys):
    pipe = redis.pipeline()
    for key in keys:
        pipe.get(key)
    return pipe.execute()

# 3. 키를 슬롯별로 그룹화
def group_keys_by_slot(keys):
    slots = {}
    for key in keys:
        slot = get_hash_slot(key)
        if slot not in slots:
            slots[slot] = []
        slots[slot].append(key)
    return slots
```

### 사례 4: 메모리 부족으로 인한 서비스 중단

**문제 상황:**
```bash
# Redis 메모리 부족으로 OOM 발생
# 서비스 응답 불가 상태
```

**원인 분석:**
```bash
# 1. maxmemory 미설정
# 2. Eviction 정책 미설정
# 3. 메모리 사용량 모니터링 부족

# 확인 방법
INFO memory | grep maxmemory
INFO memory | grep used_memory
```

**해결책:**
```bash
# 1. maxmemory 설정
maxmemory 2gb
maxmemory-policy allkeys-lru

# 2. 메모리 모니터링
def monitor_memory():
    info = redis.info('memory')
    used_memory = info['used_memory']
    max_memory = info['maxmemory']
    
    if used_memory > max_memory * 0.8:
        print("⚠️ 메모리 사용량 80% 초과")
        # 알림 발송 또는 자동 조치

# 3. Big Key 모니터링
redis-cli --bigkeys
```

### 사례 5: 복제 지연으로 인한 데이터 불일치

**문제 상황:**
```python
# Master에 쓰기 → Replica에서 읽기 시 이전 데이터 반환
redis.set("key", "new_value")  # Master
time.sleep(0.1)
value = redis.get("key")       # Replica에서 이전 값 반환
```

**원인 분석:**
```bash
# 비동기 복제로 인한 지연
# 1. Master는 즉시 응답
# 2. Replica로 복제는 비동기
# 3. 네트워크 지연으로 복제 지연 발생

# 확인 방법
INFO replication | grep lag
```

**해결책:**
```python
# 1. 최소 복제본 수 설정
# redis.conf
min-replicas-to-write 1
min-replicas-max-lag 10

# 2. 일관성 보장을 위한 읽기 전략
def read_with_consistency(key, require_consistency=False):
    if require_consistency:
        # Master에서 읽기
        return redis.get(key)
    else:
        # Replica에서 읽기 (성능 우선)
        return redis.get(key)

# 3. 복제 지연 모니터링
def check_replication_lag():
    info = redis.info('replication')
    lag = info.get('lag', 0)
    if lag > 10:
        print(f"⚠️ 복제 지연: {lag}초")
        # 알림 발송
```

---

## 4️⃣ O(N) 명령어 주의사항

### 위험한 명령어들
```bash
# O(N) 명령어 - 대규모 데이터에서 위험
KEYS pattern          # 모든 키 검색
SMEMBERS set_name     # Set 전체 멤버 조회
LRANGE list_name 0 -1 # List 전체 조회
HGETALL hash_name     # Hash 전체 조회
ZRANGE zset_name 0 -1 # Sorted Set 전체 조회
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
```

---

## 5️⃣ 네트워크 파티션 문제

### Master-Replica 불일치
**문제**: 네트워크 장애로 Master와 Replica 간 데이터 불일치

```bash
# 복제 상태 확인
INFO replication

# 복제 지연 확인
redis-cli -p 6380 INFO replication | grep lag

# 해결책: 최소 복제본 수 설정
min-replicas-to-write 1
min-replicas-max-lag 10
```

### Sentinel Failover 시나리오
```bash
# Sentinel 상태 확인
redis-cli -p 26379 SENTINEL masters

# 수동 Failover
redis-cli -p 26379 SENTINEL failover mymaster

# 복제본 승격
redis-cli -p 6380 REPLICAOF no one
```

---

## 6️⃣ 메모리 관리

### Eviction 정책 설정
```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru  # LRU 기반 삭제

# 정책 옵션
# volatile-lru: 만료 시간이 있는 키 중 LRU
# volatile-lfu: 만료 시간이 있는 키 중 LFU
# volatile-ttl: 만료 시간이 있는 키 중 TTL이 짧은 것
# volatile-random: 만료 시간이 있는 키 중 랜덤
# allkeys-lru: 모든 키 중 LRU
# allkeys-lfu: 모든 키 중 LFU
# allkeys-random: 모든 키 중 랜덤
# noeviction: 삭제하지 않음 (에러 반환)
```

### 메모리 단편화 문제
```bash
# 메모리 단편화 확인
INFO memory | grep mem_fragmentation_ratio

# 해결책: 메모리 압축
activedefrag yes
active-defrag-ignore-bytes 100mb
active-defrag-threshold-lower 10
active-defrag-threshold-upper 100
```

---

## 7️⃣ 성능 모니터링

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

# 실시간 모니터링
MONITOR

# 메모리 사용량
MEMORY USAGE key_name
MEMORY STATS
```

### 성능 지표 해석
```bash
# 히트율 확인
INFO stats | grep keyspace_hits
INFO stats | grep keyspace_misses

# 연결 수 확인
INFO clients | grep connected_clients

# 명령어별 통계
INFO commandstats
```

---

## 8️⃣ 실무 트러블슈팅 체크리스트

### 장애 발생 시 확인사항
1. **네트워크 연결 상태**
   ```bash
   redis-cli ping
   telnet redis_host 6379
   ```

2. **메모리 사용량**
   ```bash
   INFO memory
   redis-cli --bigkeys
   ```

3. **성능 지표**
   ```bash
   INFO stats
   SLOWLOG GET 10
   ```

4. **복제 상태** (Master-Replica 환경)
   ```bash
   INFO replication
   redis-cli -p 26379 SENTINEL masters
   ```

5. **로그 확인**
   ```bash
   tail -f /var/log/redis/redis-server.log
   ```

### 예방적 모니터링
```python
import redis
import time

def health_check():
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

# 주기적 실행
while True:
    health_check()
    time.sleep(60)  # 1분마다 체크
```

### 실무 모니터링 예시

#### INFO memory 활용
```python
def monitor_memory_usage():
    """메모리 사용량 상세 모니터링"""
    info = redis.info('memory')
    
    # 핵심 지표
    used_memory = info['used_memory_human']
    max_memory = info['maxmemory_human']
    mem_fragmentation_ratio = info['mem_fragmentation_ratio']
    
    # 메모리 사용률 계산
    used_memory_bytes = info['used_memory']
    max_memory_bytes = info['maxmemory']
    memory_usage_ratio = used_memory_bytes / max_memory_bytes if max_memory_bytes > 0 else 0
    
    print(f"메모리 사용량: {used_memory}/{max_memory}")
    print(f"메모리 사용률: {memory_usage_ratio:.2%}")
    print(f"파편화율: {mem_fragmentation_ratio:.2f}")
    
    # 임계값 체크
    if memory_usage_ratio > 0.8:
        print("🚨 메모리 사용량 80% 초과 - 조치 필요")
    
    if mem_fragmentation_ratio > 1.5:
        print("🚨 메모리 파편화 심각 - 압축 필요")
    
    return {
        'usage_ratio': memory_usage_ratio,
        'fragmentation': mem_fragmentation_ratio
    }
```

#### SLOWLOG 활용
```python
def analyze_slow_queries():
    """느린 쿼리 분석"""
    slow_logs = redis.slowlog_get(10)  # 최근 10개
    
    print("=== 느린 쿼리 분석 ===")
    for i, log in enumerate(slow_logs):
        duration_ms = log['duration'] / 1000  # 마이크로초 → 밀리초
        command = ' '.join(log['command'])
        
        print(f"{i+1}. 지속시간: {duration_ms:.2f}ms")
        print(f"   명령어: {command}")
        print(f"   타임스탬프: {log['start_time']}")
        print("---")
        
        # 위험한 명령어 체크
        if 'KEYS' in command:
            print("⚠️ KEYS 명령어 사용 - 성능 위험")
        if 'FLUSHALL' in command:
            print("🚨 FLUSHALL 명령어 사용 - 데이터 위험")
```

#### MONITOR 활용 (디버깅 시에만)
```python
def debug_redis_commands():
    """Redis 명령어 실시간 디버깅 (성능 영향 주의)"""
    print("Redis 명령어 모니터링 시작 (Ctrl+C로 종료)")
    
    try:
        monitor = redis.monitor()
        for command in monitor:
            # 특정 패턴 필터링
            if 'KEYS' in command or 'FLUSH' in command:
                print(f"🚨 위험 명령어 감지: {command}")
            elif 'GET' in command or 'SET' in command:
                print(f"일반 명령어: {command}")
    except KeyboardInterrupt:
        print("모니터링 종료")
```

### Redis 운영 실수 사례

#### 실수 1: KEYS 명령어 남용
```python
# ❌ 잘못된 사용법
def bad_keys_usage():
    # 수백만 키에서 KEYS 사용
    keys = redis.keys("user:*")  # O(N) - 매우 느림
    for key in keys:
        redis.delete(key)

# ✅ 올바른 사용법
def good_keys_usage():
    # SCAN으로 배치 처리
    cursor = 0
    while True:
        cursor, keys = redis.scan(cursor, match="user:*", count=1000)
        if keys:
            redis.delete(*keys)
        if cursor == 0:
            break
```

#### 실수 2: maxmemory 미설정
```python
# ❌ 잘못된 설정
# redis.conf에 maxmemory 설정 없음
# 메모리 부족 시 OOM 발생

# ✅ 올바른 설정
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

#### 실수 3: TTL 없는 세션 관리
```python
# ❌ 잘못된 사용법
def bad_session_management():
    redis.set(f"session:{session_id}", session_data)  # TTL 없음

# ✅ 올바른 사용법
def good_session_management():
    redis.setex(f"session:{session_id}", 3600, session_data)  # 1시간 TTL
```

#### 실수 4: Pipeline 미사용
```python
# ❌ 잘못된 사용법
def bad_batch_operations():
    for i in range(1000):
        redis.set(f"key:{i}", f"value:{i}")  # 1000번의 네트워크 왕복

# ✅ 올바른 사용법
def good_batch_operations():
    pipe = redis.pipeline()
    for i in range(1000):
        pipe.set(f"key:{i}", f"value:{i}")
    pipe.execute()  # 1번의 네트워크 왕복
```

#### 실수 5: 보안 설정 부족
```python
# ❌ 잘못된 설정
bind 0.0.0.0          # 모든 IP 허용
protected-mode no     # 보호 모드 비활성화
# requirepass 없음     # 인증 없음

# ✅ 올바른 설정
bind 127.0.0.1        # 로컬호스트만 허용
protected-mode yes    # 보호 모드 활성화
requirepass strong_password  # 강력한 패스워드
```

---

## 9️⃣ 보안 체크리스트

### 기본 보안 설정 확인
- [ ] `bind 127.0.0.1` 설정
- [ ] `requirepass` 또는 ACL 설정
- [ ] `protected-mode yes` 설정
- [ ] 위험 명령어 `rename-command` 설정
- [ ] 방화벽/보안 그룹 설정
- [ ] TLS/SSL 설정 (운영 환경)

### 정기적 보안 점검
- [ ] 접근 로그 모니터링
- [ ] 인증 실패 로그 확인
- [ ] 네트워크 접근 제한 확인
- [ ] 패스워드 정기 변경
- [ ] 권한 최소화 원칙 적용

---
---
<details>
<summary>cf. reference</summary>

- https://redis.io/docs/latest/operate/security/
- https://redis.io/docs/latest/operate/troubleshooting/
- https://redis.io/docs/latest/operate/monitoring/
</details>