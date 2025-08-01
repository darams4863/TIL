---
title: "Redis Pub/Sub vs Stream vs Queue"
date: 2025-08-01
categories:
  - redis
tags:
  - redis
  - pub-sub
  - stream
  - consumer-group
  - message-queue
  - queue
---

# Redis Pub/Sub vs Stream vs Queue 

## 개요
Redis에서 제공하는 메시징 방식들:

- **Pub/Sub**: 메시지 브로드캐스트를 위한 실시간 통신 방식
- **Stream**: 메시지 큐와 이벤트 스트리밍(cf.발생하는 사건(로그인,주문,클릭,결제 등)을 로그처럼 기록하면서 동시에 실시간 소비(Processing)도 가능하게 데이터가 흐르는 파이프라인처럼 처리되는 구조/패턴)을 위한 고급 메시징 시스템
- **Queue**: 단순한 생산자-소비자 패턴의 메시지 큐 (List 기반)

각각 실시간성, 영속성, 개발 복잡도 측면에서 다른 특성을 가지며, 용도에 따라 적절히 선택하여 사용한다.

---

## 1️⃣ Redis Pub/Sub (Publish/Subscribe)
> Publish / Subscribe 란 특정한 주제(topic)에 대하여 해당 topic을 구독한 모두에게 메시지를 발행하는 통신 방법으로 채널을 구독한 수신자(클라이언트) 모두에게 메시지를 전송 하는것을 의미한다. 하나의 Client가 메시지를 Publish하면, 이 Topic에 연결되어 있는 다수의 클라이언트가 메시지를 받을 수 있는 구조이다.
쉽게 생각하면, Youtube 채널 구독과 비슷하다. 구독과 좋아요(Subscribe )를 누르면, 나중에 크리에이터가 새로운 글을 발행(Publish)하면 구독자 한테만 알림(notification)이 오게 되는 원리이다 

### 기본 개념
- **실시간 브로드캐스트**: 발행자(Publisher)가 메시지를 채널에 발행하면, 구독자(Subscriber)들이 실시간으로 수신
- **Fire-and-Forget**: 메시지 발행 후 즉시 전달, 수신 여부 확인 불가
- **메모리 기반**: 메시지가 메모리에만 저장되어 구독자 오프라인 시 유실

### 주요 명령어
```bash
# 1. 구독자들이 채널 구독
SUBSCRIBE news:tech
SUBSCRIBE news:sports

# 2. 발행자가 메시지 발행
PUBLISH news:tech "새로운 AI 기술 발표"
PUBLISH news:sports "월드컵 결승전 결과"

# 3. 구독자들이 실시간으로 메시지 수신
# news:tech 구독자 → "새로운 AI 기술 발표" 수신
# news:sports 구독자 → "월드컵 결승전 결과" 수신

# 4. 구독 해제
UNSUBSCRIBE news:tech
PUNSUBSCRIBE news:*
```

### Pub/Sub 구조
```
발행자(Publisher)     채널(Channel)     구독자(Subscriber)
     │                    │                    │
     ├─ PUBLISH ──────────┤                    │
     │                    ├─ SUBSCRIBE ────────┤
     │                    │                    │
     └─ 메시지 발행 ───────┴─ 실시간 전달 ───────┘
```

### 특징
**장점:**
- **실시간 전달**: 메시지 발행 즉시 모든 구독자에게 전달
- **간단한 구조**: 복잡한 설정 없이 바로 사용 가능
- **패턴 구독**: 와일드카드 패턴으로 여러 채널 동시 구독 
(cf. `PSUBSCRIBE`와 같은 명령어를 사용해서 여러 채널을 한 번에 구독할 수 있는 기능)

**단점:**
- **메시지 유실**: 구독자가 오프라인이면 메시지 유실
- **브로드캐스트 한계**: 브로드캐스트만 가능. 특정 구독자에게만 전달 불가
- **메시지 영속성 없음**: 메모리에만 저장되어 서버 재시작 시 유실

### 실무 활용 사례
- **실시간 알림**: 웹소켓 대신 Pub/Sub으로 실시간 알림
- **이벤트 브로드캐스트**: 시스템 간 이벤트 전파
- **채팅 시스템**: 실시간 채팅 메시지 전달

---

## 2️⃣ Redis Stream

### 기본 개념
- **Stream**: 메시지 큐와 이벤트 스트리밍을 위한 자료구조
- **메시지 영속성**: 메시지가 디스크에 저장되어 유실 방지. 쌓인 메시지는 언제든 다시 읽을 수 있다. 
- **Consumer Group**: 여러 Consumer가 한 큐를 나눠서 처리하도록 지원 (`메시지 분산 처리 및 장애 복구`)
- **ID 기반 메시지**: 메시지마다 고유한 ID(시간 기반)가 있어서, 어디까지 읽었는지(Offset) 추적 가능 -> 재처리, 중복 방지 (`ID 기반 과거 메세지 조회 및 재처리 가능`)
- **Offset 관리**: 각 소비자가 어디까지 읽었는지 추적
- **ACK & Pending**: 메시지 처리 후 ACK 해야 최종 완료. ACK 안하면 Pending 상태 -> 다른 Consumer가 재처리 가능 (`메세지 처리 상태 관리`)

### 주요 명령어
```bash
# 메시지 추가
XADD stream key value [key value ...]
XADD user:events * user_id 1001 action login

# 메시지 읽기
XREAD [COUNT count] [BLOCK milliseconds] STREAMS key [key ...] id [id ...]
XREAD COUNT 10 STREAMS user:events 0

# Consumer Group
XGROUP CREATE stream groupname id [MKSTREAM]    # Consumer Group 생성
XREADGROUP GROUP groupname consumer [COUNT count] [BLOCK milliseconds] STREAMS key [key ...] id [id ...]
XREADGROUP GROUP groupname consumer STREAMS user:events >
```

### Stream 구조
```bash 
Stream: user:events
├── 1703123456789-0: {"user_id": 1001, "action": "login"}
├── 1703123456790-0: {"user_id": 1002, "action": "purchase"}
├── 1703123456791-0: {"user_id": 1001, "action": "logout"}
└── 1703123456792-0: {"user_id": 1003, "action": "register"}
```
- Stream의 특징:
    - **ID**: 타임스탬프 기반 + 시퀀스 번호
        - 1703123456789-0 → ms 단위 시간 + 동일 시간에 여러 메시지가 있으면 뒤에 -1, -2 식으로 증가
    - **Append-only**: 항상 뒤에만 추가 (XADD)
    - **순서 보장**: 메시지가 시간순으로 쌓이고, ID 기반으로 순서가 유지됨

---

## 3️⃣ Redis Queue (List 기반)

### 기본 개념
- **FIFO 큐**: Redis List 자료구조 기반 메시지 큐
- **생산자-소비자 패턴**: 생산자가 메시지 생산, 소비자가 순서대로 소비
- **영속성**: RDB/AOF를 통해 메시지 영속성 보장
- **단순한 구조**: Consumer Group 없이 기본적인 큐 기능만 제공

### 주요 명령어
```bash
# 메시지 추가 (생산자)
LPUSH queue_name message    # 왼쪽에서 추가 (FIFO)
RPUSH queue_name message    # 오른쪽에서 추가 (LIFO - 스택)

# 메시지 소비 (소비자)
LPOP queue_name             # 왼쪽에서 제거 (FIFO)
RPOP queue_name             # 오른쪽에서 제거 (LIFO)
BLPOP queue_name timeout    # 블로킹 방식으로 왼쪽에서 제거
BRPOP queue_name timeout    # 블로킹 방식으로 오른쪽에서 제거

# 큐 정보 확인
LLEN queue_name             # 큐 길이 확인
LRANGE queue_name 0 -1      # 전체 메시지 조회
```

### Queue 구조
```bash
# Redis List 기반 큐
Queue: task_queue
├── [task1] ← LPUSH (생산자)
├── [task2] ← LPUSH
├── [task3] ← LPUSH
└── [task4] ← LPUSH
    ↓
BRPOP (소비자) → task1, task2, task3, task4 순서대로 처리
```

---

## 4️⃣ 세 가지 방식 비교
### 핵심 차이점
```
Pub/Sub: 실시간 브로드캐스트 (Fire-and-Forget)
    ↓ 영속성 추가
Queue: 안정적인 메시지 처리 (FIFO/LIFO)
    ↓ 재처리 + 분산 처리 추가  
Stream: 이벤트 스트리밍 + 메시지 큐 (하이브리드)
```

### 상세 비교표

| 구분 | Pub/Sub | Stream | Queue |
|------|---------|--------|-------|
| **메시지 유실** | 구독자 오프라인 시 유실 | 영속성 보장 (RDB/AOF) | 영속성 보장 (RDB/AOF) |
| **처리 방식** | 브로드캐스트 | Consumer Group 분산 | 단순 순차 처리 |
| **재처리** | 불가능 | ACK 기반 자동 재처리 | 수동 구현 필요 |
| **분산 처리** | 불가능 | Consumer Group 자동 분산 | 수동 구현 필요 |
| **과거 조회** | 불가능 | ID 기반 과거 조회 가능 | 불가능 |
| **복잡도** | 간단 | 복잡하지만 기능 풍부 | 간단 |

### 선택 기준

| 사용 사례 | 권장 방식 | 이유 |
|-----------|-----------|------|
| **실시간 알림** | Pub/Sub | 단순하고 빠름, 메시지 유실 허용 |
| **단순 작업 큐** | Queue | FIFO 보장, 간단한 구조 |
| **이벤트 로그** | Stream | 영속성 + 재처리 + 과거 조회 |
| **복잡한 분산 처리** | Stream | Consumer Group 자동 분산 |
| **실시간 + 영속성** | Stream | 둘 다 필요할 때 |

---

## 5️⃣ 실무 활용 예시
### Pub/Sub 활용
```python
# 실시간 알림
import redis

# 구독자
async def subscribe_events():
    r = redis.Redis()
    pubsub = r.pubsub()
    pubsub.subscribe('user:events')
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"수신: {message['data']}")

# 발행자
def publish_event(event_data):
    r = redis.Redis()
    r.publish('user:events', event_data)
```

### Stream 활용
```python
# 이벤트 스트리밍
import redis

# Consumer Group 생성
r = redis.Redis()
r.xgroup_create('user:events', 'notification_group', id='0')

# 메시지 처리
def process_messages():
    while True:
        messages = r.xreadgroup(
            'notification_group', 'consumer1',
            {'user:events': '>'}, count=10, block=1000
        )
        
        for stream, msgs in messages:
            for msg_id, data in msgs:
                # 메시지 처리
                process_event(data)
                # ACK 전송
                r.xack('user:events', 'notification_group', msg_id)
```

### Queue 활용
```python
# 작업 큐
import redis

# 생산자
def producer():
    r = redis.Redis()
    tasks = ['task1', 'task2', 'task3', 'task4']
    
    for task in tasks:
        r.lpush('task_queue', task)

# 소비자
def consumer():
    r = redis.Redis()
    
    while True:
        result = r.brpop('task_queue', timeout=1)
        if result:
            queue_name, message = result
            process_task(message.decode('utf-8'))
```

---

## 6️⃣ 주의사항 및 모범 사례
### Pub/Sub 주의사항
- 메시지 유실 가능성 고려
- 구독자 연결 상태 관리 필요
- 메모리 사용량 모니터링

### Stream 주의사항
- 오래된 메시지는 XTRIM으로 정리
- Consumer Group 장애 시 재처리 로직 구현
- 대량 메시지 처리 시 배치 처리 권장

### Queue 주의사항
- 메시지 유실 방지를 위한 안전한 소비 패턴 사용
- 큐 길이 모니터링 및 백프레셔 처리 
    - (cf. 백프레셔? 생산자가 메세지를 큐에 넣는 속도가 소비자가 처리하는 속도보다 빠를 때 발생하는 압박을 의미. 해결 방법: 큐 길이를 모니터링하고 만약 생산 속도가 너무 빠르면 생산 속도를 조절하는 또는 소비자/워커를 확장하는 방식 또는 배치 처리로 해결 가능)
- 장애 시 재처리 로직 수동 구현 필요

### 실무 적용 전략
- **Pub/Sub**: 실시간 알림, 이벤트 브로드캐스트
- **Stream**: 이벤트 스트리밍, 메시지 큐, 로그 수집
- **Queue**: 단순한 작업 큐, 순서가 중요한 처리
- **하이브리드**: Pub/Sub으로 실시간 전달 + Stream으로 영속성 보장

---
---
<details>
<summary>cf. reference</summary>

- https://inpa.tistory.com/entry/REDIS-%F0%9F%93%9A-PUBSUB-%EA%B8%80%EA%B8%B0%EB%8A%A5-%EC%86%8C%EA%B0%9C-%EC%B1%84%ED%8C%85-%EA%B5%AC%EB%8F%85-%EC%95%8C%EB%A6%BC
- https://lucas-owner.tistory.com/60
- https://redis.io/docs/latest/develop/data-types/streams/
- https://kingjakeu.github.io/page2/
- https://splendidlolli.tistory.com/762
</details> 