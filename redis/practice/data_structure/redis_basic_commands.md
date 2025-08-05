# Redis 자료구조별 기본 명령어 가이드

이 문서는 Redis의 각 자료구조별 기본 명령어와 사용법을 정리한 가이드입니다.

## 1. Strings (문자열)

### 기본 명령어
```bash
# 값 설정/조회
SET key value                    # 값 설정
GET key                          # 값 조회
DEL key                          # 키 삭제

# 조건부 설정
SETNX key value                  # 키가 없을 때만 설정
SET key value XX                 # 키가 있을 때만 업데이트

# TTL 관리
SETEX key seconds value          # TTL과 함께 설정
TTL key                          # 남은 시간 확인
EXPIRE key seconds               # TTL 설정

# 숫자 연산
INCR key                         # 1 증가
DECR key                         # 1 감소
INCRBY key increment             # 지정값 증가
DECRBY key decrement             # 지정값 감소

# 일괄 처리
MSET key1 value1 key2 value2     # 여러 값 설정
MGET key1 key2                   # 여러 값 조회
```

### 활용 사례
- HTML/JSON 캐싱
- 조회수 카운터
- 사용자 정보 저장
- 세션 데이터

---

## 2. Bitmaps (비트맵)

### 기본 명령어
```bash
# 비트 설정/조회
SETBIT key offset value          # 특정 비트 설정 (0 또는 1)
GETBIT key offset                # 특정 비트 조회

# 비트 집계
BITCOUNT key [start end]         # 1인 비트 개수 계산
BITPOS key bit [start end]       # 첫 번째 1/0 비트 위치

# 비트 연산
BITOP operation destkey key1 key2 # 비트 연산 (AND, OR, XOR, NOT)
```

### 활용 사례
- 출석 체크 시스템
- 이벤트 참여자 관리
- 플래그 기반 상태 관리
- 대규모 boolean 데이터

---

## 3. Lists (리스트)

### 기본 명령어
```bash
# 양쪽 끝 추가/제거
LPUSH key value                  # 왼쪽에 추가
RPUSH key value                  # 오른쪽에 추가
LPOP key                         # 왼쪽에서 제거
RPOP key                         # 오른쪽에서 제거

# 범위 조회
LRANGE key start stop            # 범위 조회
LINDEX key index                 # 특정 인덱스 조회
LLEN key                         # 리스트 길이

# 삽입/제거
LINSERT key BEFORE|AFTER pivot value  # 특정 값 앞/뒤에 삽입
LREM key count value             # 특정 값 제거
LTRIM key start stop             # 범위만 유지

# 블로킹 연산
BLPOP key1 key2 timeout          # 블로킹 왼쪽 제거
BRPOP key1 key2 timeout          # 블로킹 오른쪽 제거
```

### 활용 사례
- 메시지 큐
- 최근 알림 목록
- 작업 재처리 큐
- 실시간 피드

---

## 4. Hashes (해시)

### 기본 명령어
```bash
# 필드 설정/조회
HSET key field value             # 필드 설정
HGET key field                   # 필드 조회
HDEL key field                   # 필드 삭제

# 여러 필드 처리
HMSET key field1 value1 field2 value2  # 여러 필드 설정
HMGET key field1 field2          # 여러 필드 조회
HGETALL key                      # 모든 필드 조회

# 필드 정보
HEXISTS key field                # 필드 존재 여부
HLEN key                         # 필드 개수
HKEYS key                        # 필드 이름만 조회
HVALS key                        # 값만 조회

# 숫자 연산
HINCRBY key field increment      # 정수 증가
HINCRBYFLOAT key field increment # 실수 증가
```

### 활용 사례
- 사용자 프로필 관리
- 세션 정보 저장
- 상품 정보 캐싱
- 설정 정보 관리

---

## 5. Sets (집합)

### 기본 명령어
```bash
# 멤버 추가/제거
SADD key member1 member2         # 멤버 추가
SREM key member                  # 멤버 제거
SPOP key [count]                 # 랜덤 멤버 제거

# 멤버 조회
SMEMBERS key                     # 모든 멤버 조회
SISMEMBER key member             # 멤버 존재 여부
SCARD key                        # 멤버 개수
SRANDMEMBER key [count]          # 랜덤 멤버 조회

# 집합 연산
SINTER key1 key2                 # 교집합
SUNION key1 key2                 # 합집합
SDIFF key1 key2                  # 차집합
```

### 활용 사례
- 태그 관리
- 중복 방지 큐
- 추천 시스템
- 일일 접속 사용자 관리

---

## 6. Sorted Sets (정렬된 집합)

### 기본 명령어
```bash
# 멤버 추가/제거
ZADD key score1 member1 score2 member2  # 멤버 추가
ZREM key member                  # 멤버 제거

# 순위 조회
ZRANGE key start stop [WITHSCORES]      # 오름차순 조회
ZREVRANGE key start stop [WITHSCORES]   # 내림차순 조회
ZRANK key member                 # 순위 조회 (오름차순)
ZREVRANK key member              # 순위 조회 (내림차순)

# 점수 조회
ZSCORE key member                # 점수 조회
ZRANGEBYSCORE key min max [WITHSCORES]  # 점수 범위 조회
ZCOUNT key min max               # 점수 범위 개수

# 점수 연산
ZINCRBY key increment member     # 점수 증가
```

### 활용 사례
- 실시간 랭킹 시스템
- 인기 상품 순위
- 우선순위 큐
- 지연 큐 구현

---

## 7. HyperLogLog

### 기본 명령어
```bash
# 멤버 추가
PFADD key element1 element2      # 멤버 추가

# 개수 추정
PFCOUNT key                      # 유니크 개수 추정

# 병합
PFMERGE destkey sourcekey1 sourcekey2  # 여러 HLL 병합
```

### 활용 사례
- 일일 UV(Unique Visitor) 집계
- 광고 클릭 수 추정
- 이벤트 참여자 수 추정
- 월간 통계 병합

---

## 8. Geospatial (지리공간)

### 기본 명령어
```bash
# 위치 추가
GEOADD key longitude latitude member    # 위치 추가

# 거리 계산
GEODIST key member1 member2 [unit]      # 두 지점 간 거리

# 위치 조회
GEOPOS key member                       # 좌표 조회
GEOHASH key member                      # GeoHash 조회

# 범위 검색
GEORADIUS key longitude latitude radius unit [WITHCOORD] [WITHDIST]  # 반경 검색
GEOSEARCH key FROMMEMBER member BYRADIUS radius unit                 # 멤버 기준 반경 검색
```

### 활용 사례
- 주변 매장 검색
- 라이더/기사 배차
- 거리 계산
- 지리적 범위 검색

---

## 9. Streams (스트림)

### 기본 명령어
```bash
# 메시지 추가
XADD key * field1 value1 field2 value2  # 메시지 추가

# 메시지 읽기
XREAD COUNT count STREAMS key id        # 메시지 읽기
XRANGE key start end [COUNT count]      # 범위 조회
XREVRANGE key end start [COUNT count]   # 역순 조회

# Consumer Group
XGROUP CREATE key groupname id          # 그룹 생성
XREADGROUP GROUP groupname consumer COUNT count STREAMS key >  # 그룹으로 읽기
XACK key groupname id                   # 메시지 확인
```

### 활용 사례
- 유실 없는 메시지 큐
- 실시간 알림 시스템
- 이벤트 스트리밍
- 로그 수집

---

## 10. Bitfields

### 기본 명령어
```bash
# 비트 단위 정수 설정/조회
BITFIELD key SET type offset value      # 비트 단위 정수 설정
BITFIELD key GET type offset            # 비트 단위 정수 조회
BITFIELD key INCRBY type offset increment  # 비트 단위 정수 증가
```

### 활용 사례
- 출석 체크 (30일치)
- 주문 상태 플래그 관리
- 사용자 권한 플래그
- 비트 단위 데이터 관리

---

## 공통 명령어

### 키 관리
```bash
KEYS pattern                     # 패턴으로 키 검색
DEL key1 key2                    # 키 삭제
EXISTS key                       # 키 존재 여부
TYPE key                         # 자료구조 타입
TTL key                          # 남은 시간
EXPIRE key seconds               # 만료 시간 설정
```

### 데이터베이스 관리
```bash
SELECT db                        # 데이터베이스 선택
FLUSHDB                          # 현재 DB 초기화
FLUSHALL                         # 모든 DB 초기화
DBSIZE                           # 키 개수
```

### 서버 정보
```bash
INFO [section]                   # 서버 정보
CLIENT LIST                      # 연결된 클라이언트
MONITOR                          # 실시간 명령어 모니터링
SLOWLOG GET [count]              # 느린 쿼리 로그
```

---

## 명령어 사용 팁

1. **키 네이밍**: `object:type:id:field` 형태로 일관성 있게 작성
2. **TTL 활용**: 캐시 데이터는 적절한 TTL 설정
3. **파이프라인**: 여러 명령어를 한번에 실행하여 성능 향상
4. **트랜잭션**: 원자성이 필요한 작업은 MULTI/EXEC 사용
5. **메모리 관리**: 큰 데이터는 적절한 만료 시간 설정

---

## 성능 고려사항

- **KEYS 명령어**: 대용량 데이터에서는 SCAN 사용 권장
- **HGETALL**: 큰 해시에서는 HSCAN 사용 권장
- **SMEMBERS**: 큰 집합에서는 SSCAN 사용 권장
- **ZRANGE**: 큰 정렬집합에서는 ZSCAN 사용 권장 