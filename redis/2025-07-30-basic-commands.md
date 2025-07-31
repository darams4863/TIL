---
title: "Redis 기본 명령어 실습 가이드"
date: 2025-07-30
categories:
  - redis
tags:
  - redis
  - commands
  - practice
---

# Redis 기본 명령어 실습 가이드

이 문서는 Redis의 다양한 자료구조를 실제로 실습해볼 수 있는 명령어들을 포함합니다. 각 자료구조별로 활용 사례에 맞는 실습을 진행할 수 있습니다.

## 1. Strings (문자열) 실습

### HTML 캐싱 활용 사례
```bash
# HTML 페이지 캐싱 예제
SET homepage "<html><body><h1>Welcome to My Site</h1></body></html>"
GET homepage

# 캐시 만료 시간 설정 (30초)
SETEX homepage_cache 30 "<html><body><h1>Cached Page</h1></body></html>"
TTL homepage_cache  # 남은 시간 확인

# 카운터 기능 (조회수 증가)
SET view_count 0
INCR view_count     # 1 증가
INCR view_count     # 2 증가
GET view_count

# 여러 값 한번에 설정
MSET user:1:name "Alice" user:1:age "25" user:1:city "Seoul"
MGET user:1:name user:1:age user:1:city

# 조건부 설정 (키가 없을 때만)
SETNX unique_key "first_value"    # 성공 (1 반환)
SETNX unique_key "second_value"   # 실패 (0 반환, 값 변경 안됨)
GET unique_key
```

## 2. Bitmaps 실습

### 사용자 출석 체크 시스템
```bash
# 사용자별 출석 체크 (1일 = 1비트)
# 사용자 ID 1001의 1월 1일~31일 출석 체크
SETBIT user:1001:attendance:2024:01 0 1    # 1월 1일 출석
SETBIT user:1001:attendance:2024:01 5 1    # 1월 6일 출석
SETBIT user:1001:attendance:2024:01 10 1   # 1월 11일 출석

# 특정 날짜 출석 여부 확인
GETBIT user:1001:attendance:2024:01 0      # 1월 1일 출석 여부
GETBIT user:1001:attendance:2024:01 1      # 1월 2일 출석 여부 (0 = 미출석)

# 전체 출석 일수 계산
BITCOUNT user:1001:attendance:2024:01

# 이벤트 참여 플래그 관리
SETBIT event:summer:participants 1001 1    # 사용자 1001 참여
SETBIT event:summer:participants 1002 1    # 사용자 1002 참여
SETBIT event:summer:participants 1003 0    # 사용자 1003 미참여

# 참여자 수 확인
BITCOUNT event:summer:participants
```

## 3. Lists (리스트) 실습

### 메시지 큐 시스템
```bash
# 이메일 발송 큐 생성
LPUSH email_queue "user1@example.com:Welcome email"
LPUSH email_queue "user2@example.com:Password reset"
LPUSH email_queue "user3@example.com:Order confirmation"

# 큐에서 작업 가져오기 (FIFO)
RPOP email_queue    # 가장 오래된 작업부터 처리

# 큐 길이 확인
LLEN email_queue

# 최근 알림 목록 (최근 10개만 유지)
LPUSH notifications "New message from Alice"
LPUSH notifications "Your post got 5 likes"
LPUSH notifications "Friend request from Bob"
LPUSH notifications "System maintenance at 2AM"

# 최근 10개만 유지하고 나머지 삭제
LTRIM notifications 0 9

# 전체 알림 확인
LRANGE notifications 0 -1

# 작업 재처리 큐 (실패한 작업을 다른 큐로 이동)
RPUSH failed_jobs "job_123:processing_failed"
RPUSH failed_jobs "job_456:timeout_error"

# 실패한 작업을 재처리 큐로 이동
RPOPLPUSH failed_jobs retry_queue
```

## 4. Hashes (해시) 실습

### 사용자 프로필 관리
```bash
# 사용자 프로필 정보 저장
HSET user:1001 name "Alice Johnson"
HSET user:1001 age "28"
HSET user:1001 email "alice@example.com"
HSET user:1001 city "Seoul"
HSET user:1001 join_date "2024-01-15"

# 특정 필드 조회
HGET user:1001 name
HGET user:1001 age

# 여러 필드 한번에 조회
HMGET user:1001 name email city

# 모든 필드 조회
HGETALL user:1001

# 필드 존재 여부 확인
HEXISTS user:1001 phone    # 0 (존재하지 않음)
HEXISTS user:1001 name     # 1 (존재함)

# 필드 개수 확인
HLEN user:1001

# 필드 이름만 조회
HKEYS user:1001

# 값만 조회
HVALS user:1001

# 세션 정보 관리
HSET session:abc123 user_id "1001"
HSET session:abc123 login_time "2024-01-30 10:30:00"
HSET session:abc123 last_activity "2024-01-30 11:45:00"
HSET session:abc123 ip_address "192.168.1.100"
```

## 5. Sets (집합) 실습

### 태그 관리 및 추천 시스템
```bash
# 게시물에 태그 추가
SADD post:1001:tags "redis" "database" "nosql" "cache"
SADD post:1002:tags "redis" "performance" "optimization"
SADD post:1003:tags "database" "sql" "nosql"

# 특정 게시물의 태그 조회
SMEMBERS post:1001:tags

# 태그 존재 여부 확인
SISMEMBER post:1001:tags "redis"    # 1 (존재함)
SISMEMBER post:1001:tags "python"   # 0 (존재하지 않음)

# 태그 개수 확인
SCARD post:1001:tags

# 중복 방지 큐 (Unique Job Queue)
SADD processed_jobs "job_123"
SADD processed_jobs "job_456"
SADD processed_jobs "job_789"

# 작업 중복 확인
SISMEMBER processed_jobs "job_123"  # 이미 처리됨
SISMEMBER processed_jobs "job_999"  # 아직 처리되지 않음

# 추천 시스템 - 교집합 연산
# VIP 고객이 주문한 상품들
SADD vip_orders "product_001" "product_002" "product_003" "product_004"

# 추천 서비스를 이용한 주문들
SADD recommended_service_orders "product_002" "product_003" "product_005"

# VIP 고객이 추천 서비스를 이용한 주문 (교집합)
SINTER vip_orders recommended_service_orders

# 일일 접속 사용자 관리 (TTL과 함께)
SADD today_users "user_001" "user_002" "user_003"
EXPIRE today_users 86400  # 24시간 후 자동 삭제
```

## 6. Sorted Sets (정렬된 집합) 실습

### 실시간 랭킹 시스템
```bash
# 인스타그램 해시태그 인기 순위
ZADD hashtag_rank 123 "post:1001"    # 좋아요 123개
ZADD hashtag_rank 89 "post:1002"     # 좋아요 89개
ZADD hashtag_rank 156 "post:1003"    # 좋아요 156개
ZADD hashtag_rank 67 "post:1004"     # 좋아요 67개
ZADD hashtag_rank 234 "post:1005"    # 좋아요 234개

# 상위 3개 인기 게시물 조회 (높은 점수 순)
ZREVRANGE hashtag_rank 0 2 WITHSCORES

# 특정 게시물의 순위 확인
ZREVRANK hashtag_rank "post:1001"    # 4위 (0부터 시작)

# 특정 게시물의 점수 확인
ZSCORE hashtag_rank "post:1001"

# 100점 이상인 게시물 개수
ZCOUNT hashtag_rank 100 +inf

# 우선순위 큐 (주문 처리)
ZADD pending_jobs 1732931200 "urgent_order_001"    # 긴급 주문
ZADD pending_jobs 1732931400 "normal_order_002"    # 일반 주문
ZADD pending_jobs 1732931100 "vip_order_003"       # VIP 주문

# 가장 시급한 작업 조회 (낮은 timestamp 먼저)
ZRANGE pending_jobs 0 0 WITHSCORES

# 지연 큐 구현 (AI 댓글 생성)
ZADD delay_queue 1732934800 "comment_job_501"      # 특정 시간에 실행
ZADD delay_queue 1732935000 "comment_job_502"      # 특정 시간에 실행

# 실행할 시점이 된 작업들 조회
ZRANGEBYSCORE delay_queue -inf 1732934800
```

## 7. HyperLogLog 실습

### 일일 UV(Unique Visitor) 집계
```bash
# 일일 방문자 IP 추가
PFADD daily_uv:2024:01:30 "192.168.1.100"
PFADD daily_uv:2024:01:30 "192.168.1.101"
PFADD daily_uv:2024:01:30 "192.168.1.100"    # 중복 IP (카운트에 영향 없음)
PFADD daily_uv:2024:01:30 "192.168.1.102"

# 방문자 수 추정
PFCOUNT daily_uv:2024:01:30

# 광고 클릭 이벤트 추적
PFADD ad_clicks:summer_campaign "user_001"
PFADD ad_clicks:summer_campaign "user_002"
PFADD ad_clicks:summer_campaign "user_001"    # 중복 클릭 (카운트에 영향 없음)
PFADD ad_clicks:summer_campaign "user_003"

# 클릭한 유니크 사용자 수 추정
PFCOUNT ad_clicks:summer_campaign

# 여러 HLL 병합 (월간 통계)
PFADD monthly_uv:2024:01 "192.168.1.100" "192.168.1.101"
PFADD monthly_uv:2024:01 "192.168.1.102" "192.168.1.103"

# 일일 데이터를 월간 데이터에 병합
PFMERGE monthly_uv:2024:01 daily_uv:2024:01:30
PFCOUNT monthly_uv:2024:01
```

## 8. Streams 실습

### 유실 없는 메시지 큐
```bash
# 작업 스트림에 새 메시지 추가
XADD job_stream * type "image_processing" task_id "123" priority "high"
XADD job_stream * type "email_sending" task_id "124" priority "normal"
XADD job_stream * type "data_analysis" task_id "125" priority "low"

# 스트림에서 메시지 읽기 (처음부터)
XREAD COUNT 2 STREAMS job_stream 0

# 특정 ID 이후의 메시지 읽기
XREAD COUNT 1 STREAMS job_stream 1753854859092-0

# 스트림 범위 조회
XRANGE job_stream - + COUNT 3

# 역순 조회 (최신부터)
XREVRANGE job_stream + - COUNT 3

# 메시지 개수 확인
XLEN job_stream

# Consumer Group 생성
XGROUP CREATE job_stream processing_group 0

# 그룹 단위로 메시지 읽기
XREADGROUP GROUP processing_group consumer1 COUNT 1 STREAMS job_stream >

# 메시지 처리 완료 확인
XACK job_stream processing_group 1753854859092-0

# Slack 입금 알림 예제
XADD payment_stream * user_id "1001" amount "50000" type "deposit" timestamp "2024-01-30 14:30:00"
XADD payment_stream * user_id "1002" amount "30000" type "withdrawal" timestamp "2024-01-30 14:31:00"

# 실시간 알림 처리
XREAD COUNT 1 STREAMS payment_stream 0
```

## 9. Geospatial Indexes 실습

### 위치 기반 서비스
```bash
# 편의점 위치 등록
GEOADD store_locations 127.0276 37.5665 "convenience_store_1"    # 서울
GEOADD store_locations 127.0244 37.5663 "convenience_store_2"    # 서울
GEOADD store_locations 126.9780 37.5665 "convenience_store_3"    # 서울
GEOADD store_locations 127.0017 37.5642 "convenience_store_4"    # 서울

# 현재 위치에서 2km 내 편의점 검색
GEOSEARCH store_locations 127.0276 37.5665 BYRADIUS 2 km

# 특정 편의점의 좌표 조회
GEOPOS store_locations convenience_store_1

# 두 편의점 간의 거리 계산
GEODIST store_locations convenience_store_1 convenience_store_2 km

# 상자 영역 검색 (사각형 영역)
GEOSEARCH store_locations 127.0276 37.5665 BYBOX 1 1 km

# 배달 앱 라이더 배차 예제
GEOADD available_riders 127.0276 37.5665 "rider_001"
GEOADD available_riders 127.0244 37.5663 "rider_002"
GEOADD available_riders 126.9780 37.5665 "rider_003"

# 고객 위치에서 500m 내 라이더 검색
GEOSEARCH available_riders 127.0276 37.5665 BYRADIUS 0.5 km
```

## 10. Bitfields 실습

### 비트 단위 데이터 관리
```bash
# 출석 체크 (30일치)
# 사용자 1001의 1월 출석 체크 (1일 = 1비트)
BITFIELD user:1001:attendance:2024:01 SET u1 0 1    # 1일 출석
BITFIELD user:1001:attendance:2024:01 SET u1 5 1    # 6일 출석
BITFIELD user:1001:attendance:2024:01 SET u1 10 1   # 11일 출석

# 특정 날짜 출석 여부 확인
BITFIELD user:1001:attendance:2024:01 GET u1 0      # 1일 출석 여부

# 주문 상태 플래그 관리 (대규모 상품)
SETBIT order_status 1001 1    # 주문 1001 처리중
SETBIT order_status 1002 0    # 주문 1002 미확인
SETBIT order_status 1003 1    # 주문 1003 처리중

# 특정 주문 상태 확인
GETBIT order_status 1001      # 1 (처리중)
GETBIT order_status 1002      # 0 (미확인)

# 처리중인 주문 개수 확인
BITCOUNT order_status

# 첫 번째 1 비트 위치 찾기 (처리중인 첫 번째 주문)
BITPOS order_status 1

# 비트 단위 정수 읽기/쓰기
BITFIELD user:1001:flags SET u8 0 255    # 8비트 플래그 설정
BITFIELD user:1001:flags GET u8 0        # 8비트 플래그 읽기
```

## 실습 완료 후 정리

```bash
# 모든 키 확인
KEYS *

# 특정 패턴의 키만 확인
KEYS user:*

# 키 개수 확인
DBSIZE

# 특정 키 삭제
DEL user:1001

# 모든 키 삭제 (주의!)
FLUSHALL

# Redis 서버 정보 확인
INFO

# 연결 종료
QUIT
```

