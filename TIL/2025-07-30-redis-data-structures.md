---
title: "Redis 자료구조 (String, Hash, List, Set, SortedSet)"
date: 2025-07-30
categories:
  - redis
tags:
  - redis
  - datatypes
---

# Redis Collection 
- Redis의 장점 중 하나는 key-value 형식으로 저장할 떄의 value는 단순한 Object가 아니라 다양한 자료구조를 갖을 수 있다는 점인데, Redis에서 지원하는 데이터 타입은 아래와 같다: 
  - 문자열 (Strings)
  - 리스트 (Lists)
  - 집합 (Sets)
  - 해시 (Hashes)
  - 정렬된 집합 (Sorted Sets)
  - 스트림 (Streams)
  - 지리공간 인덱스 (Geospatial Indexes)
  - 하이퍼로그로그 (HyperLogLog)
  - 비트맵 (Bitmaps)
  - 비트필드 (Bitfields)

## Strings 
- 일반적인 문자열 
- Redis의 String 타입은 binary-safe 문자열이라서 HTML, JSON, XML, 또는 JPEG 이미지(이미지는 저장되거나 전송될 때 이미 바이너리 상태임)와 같은 binary data도 저장 가능하다
- 최대 512MB까지 저장 가능하다
- 활용 사례: 
  - HTML 캐싱: 
    - DB나 템플릿 렌더링 없이 Redis에 캐싱된 e.g. 정적 페이지로 빠르게 HTML 제공 가능
- 주요 명령어:
```bash 
SET key value
GET key
DEL key
INCR key
DECR key
MSET key1 v1 key2 v2
MGET key1 key2
SETNX key value         # 지정한 key가 없을 경우에만 데이터를 저장
```

## Bitmaps
- Bitmaps는 String 자료구조를 비트 단위로 활용하는 자료구조이다 
- 최대 길이는 String 자료구조의 최대 길이인 512MB -> 2^9 * 1024 * 1024 -> 2 ^ 29 * 8bit -> 2^32 bit 관리 가능 
- 0 / 1 형태의 상태 저장에 최적화  
  - e.g. 플래그 관리, 이벤트 참여 여부, 사용자 출석 체크 


## Lists
- array 형식의 데이터 구조. 데이터를 순서대로 저장
- 양쪽에서 Push/Pop 가능하며 Queue, Stack 모두 구현 가능
- 추가 / 삭제 / 조회하는 것은 O(1)의 속도를 가지지만, 중간의 특정 index 값을 조회할 때는 O(N)의 속도를 가지는 단점이 있다 
  - 즉, 중간에 추가/삭제가 느리다. 따라서 head-tail에서 추가/삭제한다 (push/pop 연산)
- 메세지 큐로 사용하기 적절하다 (LPUSH/RPOP)
- 주요 명령어:
```bash
LPUSH key value [value ...]    # 왼쪽(head)에 값 삽입
RPUSH key value [value ...]    # 오른쪽(tail)에 값 삽입
LPOP key                       # 왼쪽에서 pop 후 반환
RPOP key                       # 오른쪽에서 pop 후 반환
BLPOP key [key ...] timeout    # Blocking pop (왼쪽), 리스트에 값이 없을 경우, 지정한 시간만큼 기다려서 값이 들어오면 RPOP 실행
BRPOP key [key ...] timeout    # Blocking pop (오른쪽), 리스트에 값이 없을 경우, 지정한 시간만큼 기다려서 값이 들어오면 RPOPLPUSH 실행
LLEN key                       # 리스트 길이 조회
LRANGE key start stop          # 인덱스로 범위를 지정해서 리스트 구간 조회 (0 -1 전체)
LTRIM key start stop           # 특정 구간만 남기고 나머지 삭제
LREM key count value           # 값 삭제 (앞에서 count개)
RPOPLPUSH src dst              # src에서 pop → dst로 push
```
- 활용 사례: 
  - 메시지 큐
	  - 간단한 Job Queue, Task Queue 구현
	  - LPUSH로 enqueue, BRPOP으로 dequeue
	  - 예: 이메일 발송, 이미지 처리 등 비동기 작업
	- 타임라인 / 최근 기록 저장
	  - 소셜 피드, 최근 알림 목록
	  - LPUSH + LTRIM 조합으로 최근 N개만 유지
	- 작업 재처리 / 실패 처리
	  - RPOPLPUSH를 활용하여 실패 시 재처리 가능
	  - 예: 한쪽 큐에서 pop → 작업 실패 시 다른 큐로 이동



## Hashes
- field-value로 구성되어있는 전형적인 hash 형태의 자료구조 (파이썬의 딕셔너리를 생각하면 쉽다)
- key 하위에 subkey를 이용해 추가적인 Hash Table을 제공하는 자료구조 
- 메모리가 허용하는 한, 제한없이 field들을 넣을 수가 있다 
```bash 
hash-key → {
    field1: value1,
    field2: value2
}
# 여기서 hash-key는 Redis 전체에서의 Key
# field1, field2는 해시 내부의 식별자(서브키)
# 그래서 혼동을 막기 위해 field-value라고 부름
```
- 주요 명령어: 
```bash
# 필드 추가/수정
HSET key field value         # 필드 생성 또는 수정
HMSET key field1 value1 field2 value2  # 여러 필드 한번에 설정 (deprecated → HSET multiple)

# 필드 조회
HGET key field               # 특정 필드 조회
HMGET key field1 field2      # 여러 필드 조회
HGETALL key                  # 모든 필드-값 조회

# 필드 존재 확인
HEXISTS key field            # 필드 존재 여부 확인

# 필드 삭제
HDEL key field1 [field2 ...] # 필드 삭제

# 전체 통계
HLEN key                     # 필드 개수 조회
HKEYS key                    # 모든 필드 이름 조회
HVALS key                    # 모든 값 조회
```
- 활용 사례: 
  - 사용자 프로필 저장: 
    ```bash 
      HSET user:100 name "Alice"
      HSET user:100 age 25
      HSET user:100 country "KR"
    ```
    → 한 Key(user:100)에 유저 정보를 한 번에 관리 가능
  - 캐시된 세션 정보: 
    - 세션 Key 안에 다양한 상태값, 토큰, 최근 로그인 시간 등을 저장


## Sets
- 중복된 데이터를 담지 않기 위해 사용하는 자료구조 
- 유니크한 key 값
- 정렬되지 않은 집합 
- 중복된 데이터를 여러번 저장하면 최종 한번만 저장됨 
- set간의 연산을 지원하고, 교집합, 합집합, 차이를 매우 빠른 시간내에 추출할 수 있다 
- 주요 명령어: 
```bash 
SADD key member1 [member2 ...]     # 집합에 요소 추가
SREM key member1 [member2 ...]     # 요소 제거
SMEMBERS key                       # 모든 요소 조회
SISMEMBER key member                # 요소 존재 여부 확인
SCARD key                           # 요소 개수 조회
SPOP key [count]                    # 임의의 요소 제거 & 반환
SRANDMEMBER key [count]             # 임의의 요소 반환
SUNION key1 key2 [...]              # 합집합
SINTER key1 key2 [...]              # 교집합
SDIFF key1 key2 [...]               # 차집합
```
- 활용 사례: 
  - 태그 관리(중복 제거)
	- 중복 방지 큐(Unique Job Queue) 
    - 특정 작업을 한 번만 처리하도록 보장할 때 사용 
    - 예: AI 댓글 생성 요청 ID를 Set에 저장 -> 이미 처리된 Job 재실행 방지 
	- 추천 시스템의 교집합/차집합 연산: 
    - 예: recommended_service(추천 서비스), vip_orders(VIP 고객 주문) 
    -> SINTER로 VIP 고객 주문중 추천 서비스를 이용하는 주문만 빠르게 조회 
  - 임시 데이터 캐시 
    - 예: 하루 동안 접속한 사용자 ID 저장 -> BITFIELD보다 빠른 중복 체크 
    - TTL과 함께 사용하면 자동으로 청소 가능  
      ```bash 
      SADD today_users user_id0
      EXPIRE today_users 86400
      ```


## Sorted Sets
- Set에 score(가중치) 개념이 추가된 자료구조
- 일반적으로 set은 정렬이 되어있지 않고 insert한 순서대로 들어간다.
그러나 Sorted Set은 score 순으로 오름차순 정렬되면서 저장되고, 만약 score 값이 같으면 사전 순으로 정렬되어 저장 
- value는 중복 불가능, score는 중복 가능하다 
- 주요 명령어: 
```bash
ZADD key score1 member1 [score2 member2 ...]  # 요소 추가
ZRANGE key start stop [WITHSCORES]            # 낮은 점수 순 조회
ZREVRANGE key start stop [WITHSCORES]         # 높은 점수 순 조회
ZSCORE key member                             # 특정 요소 점수 조회
ZREM key member1 [member2 ...]                # 요소 제거
ZRANK key member                              # 순위 조회 (오름차순)
ZREVRANK key member                           # 순위 조회 (내림차순)
ZCARD key                                     # 요소 개수
ZCOUNT key min max                            # 특정 점수 범위 개수
```
- 활용 사례: 
  - 실시간 랭킹 시스템 (게임 점수판)
    - 예: 인스타그램 해시태그 인기 순위 
      - score = 좋아요 수, member = 게시물 ID 
        ```bash 
        ZADD hashtag_rank 123 post:1001
        ZREVRANGE hashtag_rank 0 9 WITHSCORES  # 상위 10개 인기 게시물
        ```
  - 우선순위 큐 
    - 예: 주문 처리 → 긴급 주문(score 낮음) 우선 처리
      - score = 처리 예정 시간 timestamp → 낮은 timestamp 먼저 처리 
      ```bash 
      ZADD pending_jobs 1732931200 job_101
      ZRANGE pending_jobs 0 0 WITHSCORES  # 가장 시급한 작업
      ```
  - 지연 큐 구현
    - 특정 시간 이후에만 처리할 Job 관리
    - 예: AI 댓글 생성 지연 처리
    ```bash 
    ZADD delay_queue 1732934800 comment_job_501
    ZRANGEBYSCORE delay_queue -inf 1732934800  # 실행할 시점 Job 조회
    ``` 


## HyperLogLog
- 굉장히 많은 양의 데이터를 dump할 때 사용되는 자료구조 
- 중복되지 않은 대용량 데이터를 count할 때 주로 많이 사용한다
- set과 비슷하지만 저장되는 용량은 매우 작다 (저장 되는 모든 값이 12kb 고정)
- 정확도가 100%는 아니고, 약 ±0.81% 오차 있음
- 또한 저장된 데이터는 다시 확인할 수 없다 (데이터 보호에 적절)
- 주요 명령어: 
```bash
PFADD key element1 [element2 ...]     # 요소 추가
PFCOUNT key                           # 추정된 유니크 개수 반환
PFMERGE destkey sourcekey1 sourcekey2 # 여러 HLL 병합
```
- 활용 사례: 
  - 이벤트 로그 유저 중복 제거 
    - 예: 광고 클릭 수 추정
  - 일일 UV(Unique Visitor) 집게 
  ```bash 
  PFADD daily_uv 192.168.0.1 192.168.0.2
  PFCOUNT daily_uv  # 방문자 수 추정
  ```


## Streams
- Redis 5.0부터 추가된 메시지 스트리밍 자료구조
- Pub/Sub + Queue + Log의 장점을 합친 구조
- 유실 없는 메시지 처리가 가능하고, 소비 이력을 (log) Redis에 저장할 수 있음
- Append-Only
- 주요 명령어: 
```bash
XADD key * field1 value1 [field2 value2 ...]   # 새 메시지 추가
XREAD COUNT n STREAMS key [ID]                 # 메시지 읽기
XRANGE key start end [COUNT n]                 # 범위 조회
XREVRANGE key end start [COUNT n]              # 역순 조회
XDEL key ID                                    # 특정 메시지 삭제
XLEN key                                       # 메시지 개수
XGROUP CREATE key groupname ID                 # Consumer Group 생성
XREADGROUP GROUP group consumer STREAMS key >  # 그룹 단위 읽기
XACK key group ID                              # 메시지 처리 완료
```
- 활용 사례: 
  - 분산 작업 큐
    - Worker들이 Consumer Group으로 분산 처리
    - 예: 
•	유실 없는 메시지 큐
	•	Pub/Sub 대체 (소비 확인 가능)
	•	마이크로서비스 간 이벤트 스트리밍
- 
- 예: Slack 입금 알림
  - 실시간 로그 스트리밍 + 알림 후 Ack 처리


## Geospatial Indexes
- 좌표 기반 데이터 저장 및 거리 계산 가능
- 지구 반경 계산을 위해 내부적으로 GeoHash 사용
- 주요 명령어: 
```bash
GEOADD key longitude latitude member        # 위치 추가
GEODIST key member1 member2 [unit]          # 거리 계산
GEOPOS key member1 [member2 ...]            # 좌표 조회
# GEORADIUS key lon lat radius m|km           # 원형 반경 검색 (deprecated → GEOSEARCH)
GEOSEARCH key lon lat BYRADIUS r m|km       # 좌표 기반 검색
GEOSEARCH key member BYBOX w h m|km         # 상자 영역 검색
```
- 활용 사례:
  - 위치 정보를 이용해서 현재 위치 기준으로 가장 가까운 정류장 5개를 추출해서 고객에게 길안내 정보 제공 
  - 주변 매장 검색
    - 예: store_locations에 편의점 좌표 등록 후 2km 내 검색
  - 라이더/기사 배차
    - 예: 배달 앱에서 고객 주변 500m 라이더 탐색
  - 위치 기반 푸시 알림
    - 예: 특정 행사장 반경 1km 사용자에게 푸시 발송


## Bitfields
- 비트 단위 데이터 관리 (대규모 boolean/flag 저장 효율적)
- 주요 명령어: 
```bash
SETBIT key offset value        # 특정 위치 비트 설정
GETBIT key offset              # 특정 위치 비트 조회
BITCOUNT key [start end]       # 1로 설정된 비트 수
BITPOS key bit [start end]     # 첫 번째 1/0 비트 위치
BITFIELD key GET type offset   # 비트 단위 정수 읽기
BITFIELD key SET type offset v # 비트 단위 정수 쓰기
```
- 활용 사례: 
  - 출석 체크 / 일 단위 상태 저장
    - 예: user:checkin에서 하루 1bit -> 30일 관리 
  - 플래그 저장 (Y/N)
    - 예: 주문 상태 (0 = 미확인, 1 = 처리중) 관리  
  - 대규모 boolean 데이터 관리
    - 예: 1억개 상품 중 재고 여부 플래그 관리 


---
> cf. reference 
- https://inpa.tistory.com/entry/REDIS-%F0%9F%93%9A-%EB%8D%B0%EC%9D%B4%ED%84%B0-%ED%83%80%EC%9E%85Collection-%EC%A2%85%EB%A5%98-%EC%A0%95%EB%A6%AC