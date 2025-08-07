---
title: "Redis 면접용 질문 - advanced"
date: 2025-08-04
categories:
  - redis
tags:
  - redis
  - interview
  - questions
  - answers
---

# Redis Advanced Interview (심화)

3년차 백엔드 개발자 기준, 중견 이상/대기업 면접에서 자주 나오는 심화 질문과 꼬리 질문 및 답변 모음입니다.

---

## 1️⃣ 성능/운영 심화

### Q1. Redis는 싱글 스레드인데도 왜 빠른가요?

* **꼬리 질문:**

  1. epoll 기반 I/O 멀티플렉싱 구조를 설명해주세요.
  2. 싱글 스레드 구조에서 CPU 병목이 걸릴 수 있는 시점은 언제인가요?
* **답변:**

```text
- Context switching 비용이 없음
- epoll 기반 I/O 멀티플렉싱 이벤트 루프 구조
- 대부분 연산이 O(1)~O(logN)
- CPU 연산 많은 Lua Script, Big Key 처리 시 병목 발생 가능
```

* **꼬리 답변:**

  * epoll은 다수의 소켓 이벤트를 비동기적으로 처리하며, 싱글 스레드 이벤트 루프가 차례대로 이벤트를 실행합니다.
  * CPU 병목은 대형 Lua Script 실행, 대량 데이터 serialization, Big Key 처리 시 발생할 수 있습니다.

### Q2. Pipeline과 Lua Script의 차이와 선택 기준은?

* **꼬리 질문:**

  1. Pipeline으로도 원자성 보장되나요?
  2. Lua Script 사용 시 서버에 부하가 생길 수 있는 이유는?
* **답변:**

```text
- Pipeline: 네트워크 왕복 최소화, 원자성 보장 없음
- Lua Script: 원자성 보장, 서버 CPU 사용량 높음
```

* **꼬리 답변:**

  * Pipeline은 단순히 요청을 모아 한번에 전송하지만, 중간 실패 시 롤백 없음 → 원자성 X
  * Lua Script는 Redis 서버에서 직접 실행되며, 싱글 스레드에서 CPU 점유율을 높임

### Q3. Redis에서 O(N) 명령어가 위험한 이유는?

* **꼬리 질문:**

  1. KEYS, LRANGE, SMEMBERS 대신 어떤 명령어를 사용해야 하나요?
  2. SCAN 사용 시 주의할 점은?
* **답변:**

```text
- 싱글 스레드 특성상 O(N) 명령어는 서버를 블로킹
- SCAN/SSCAN/HSCAN/ZSCAN 등 점진적 처리 필요
```

* **꼬리 답변:**

  * SCAN 계열 명령어 사용
  * SCAN은 반복 호출 필요, 중복 키 가능, snapshot 아님 주의

---

## 2️⃣ TTL & 메모리 관리 심화

### Q4. Redis의 TTL 만료 정책을 설명해보세요.

* **꼬리 질문:**

  1. Lazy Expiration과 Active Expiration 차이는?
  2. TTL Storm 문제와 대응 방법은?
* **답변:**

```text
- Lazy: 키 접근 시 만료 확인
- Active: 백그라운드 샘플링 후 만료
- TTL Storm: 대량 만료 시 성능 스파이크 → TTL 분산(Randomized TTL)
```

### Q5. Eviction 정책과 상황별 선택 기준은?

* **꼬리 질문:**

  1. volatile-lru와 allkeys-lru 차이?
  2. LFU 정책은 언제 유리한가요?
* **답변:**

```text
- maxmemory 도달 시 Eviction
- volatile-lru: TTL 있는 키 중 LRU
- allkeys-lru: 전체 키 중 LRU
- LFU: Hot Key 환경에서 유리
```

### Q6. Big Key/Hot Key 문제와 대응 방법은?

* **꼬리 질문:**

  1. Big Key 의미는?
  2. Hot Key 문제 해결 방법 2가지는?
* **답변:**

```text
- Big Key: 단일 키에 수 MB 이상 데이터 저장
- Hot Key: 특정 키에 트래픽 집중
- 해결: Key Sharding, Local Cache, Lua Script, 분산 처리
```

---

## 3️⃣ Persistence & Replication 심화

### Q7. RDB와 AOF의 차이점과 장단점은?

* **꼬리 질문:**

  1. RDB Fork 시 성능 저하 이유는?
  2. AOF fsync everysec 의미는?
* **답변:**

```text
- RDB: 스냅샷, 빠름, 일부 데이터 유실 가능
- AOF: Append Only, 안정적, 느림
- Mixed Mode: RDB 부팅 + AOF 운영
```

* **꼬리 답변:**

  * Fork 시 Copy-on-Write 발생 → 메모리 복사 비용
  * everysec: 1초 단위 fsync, 성능과 안정성 균형

### Q8. Redis replication 구조와 지연 문제 설명

* **꼬리 질문:**

  1. Master-Slave vs Cluster 복제 차이?
  2. WAIT 명령어의 용도?
* **답변:**

```text
- 비동기 복제, 네트워크 지연 시 유실 가능
- Replica eventual consistency
- WAIT: 최소 n개 replica 동기화 보장
```

### Q9. Redis Cluster 동작 원리

* **꼬리 질문:**

  1. 16384 Hash Slot 이유?
  2. MGET/MSET 시 주의할 점?
* **답변:**

```text
- Consistent Hashing 기반 16384 Slot
- Slot 기반 샤딩, 키별 Slot 지정
- MGET/MSET은 같은 Slot만 가능 → Hash Tag 사용
```

---

## 4️⃣ Pub/Sub, Stream, Queue 심화

### Q10. Redis Pub/Sub 단점

* **꼬리 질문:**

  1. 메시지 유실 이유?
  2. Stream 선택 시 장점?
* **답변:**

```text
- Pub/Sub은 메시지 저장 없음 → 구독 전 유실
- Stream은 메시지 보관, Consumer Group, Ack 지원
```

### Q11. Stream과 Consumer Group 구조

* **꼬리 질문:**

  1. PEL(Pending Entry List)이란?
  2. 메시지 재처리 방법?
* **답변:**

```text
- Stream: 로그 기반 큐
- Consumer Group별 offset 관리
- Ack 전 메시지는 PEL에 저장 → 재처리 가능
```

### Q12. Redis를 Queue로 사용할 때 주의점

* **꼬리 질문:**

  1. BLPOP과 BRPOP 차이?
  2. 메시지 유실 방지 전략?
* **답변:**

```text
- List 기반 FIFO, durability 없음
- BLPOP/BRPOP은 blocking 처리
- 메시지 보장 필요 시 Stream 사용 또는 DB 보조 로깅
```

---

## 5️⃣ 분산 락 & 트러블슈팅 심화

### Q13. Redis 분산 락 원리와 Race Condition 대응

* **꼬리 질문:**

  1. SET NX EX + Lua Script 장점?
  2. TTL 없이 락 시 문제점?
* **답변:**

```text
- SET NX EX로 락 획득, Lua Script로 해제
- 원자성 보장, Race Condition 방지
- TTL 없으면 Deadlock 발생
```

### Q14. Redlock 알고리즘 동작과 한계

* **꼬리 질문:**

  1. 멀티 인스턴스에서 Redlock 성공 조건?
  2. 완전한 보장 어려운 이유?
* **답변:**

```text
- N개 Redis 중 과반수 락 획득 시 성공
- 네트워크 분리 시 double acquire 가능
- 완전한 분산 락 보장 어려움 → 보조 검증 필요
```

### Q15. Redis Latency Spike 원인 3가지

* **꼬리 질문:**

  1. Fork/Save/AOF Rewrite 영향?
  2. Big Key 처리 시 문제점?
* **답변:**

```text
- O(N) 명령어 실행
- Fork 시 Copy-on-Write 지연
- AOF rewrite I/O 부하
- Big Key/TTL Storm으로 이벤트 루프 지연
```

---

## 6️⃣ 모니터링 & 운영 심화

### Q16. Redis 성능 모니터링 방법

* **꼬리 질문:**

  1. SLOWLOG vs MONITOR 차이?
  2. 메모리 사용량/히트율 확인 방법?
* **답변:**

```text
- INFO memory/stats
- SLOWLOG GET / MONITOR
- keyspace_hits / misses로 캐시 효율 확인
```

### Q17. Big Key 탐지와 처리 전략

* **꼬리 질문:**

  1. redis-cli --bigkeys 역할?
  2. Big Key 삭제 시 주의점?
* **답변:**

```text
- Big Key는 메모리/latency spike 원인
- --bigkeys로 탐지
- UNLINK로 비동기 삭제, 데이터 샤딩 권장
```

### Q18. Redis 장애 대응 경험

* **꼬리 질문:**

  1. OOM/데이터 유실 시 대응 절차?
  2. 사전 예방 모니터링 방법?
* **답변:**

```text
- maxmemory + eviction 설정
- TTL과 만료 전략 적용
- Slowlog/BigKey 모니터링
- SCAN + UNLINK로 안전한 정리
```


--- 
<details>
<summary>cf. reference</summary>

- https://jaehyuuk.tistory.com/216
- https://sunro1994.tistory.com/333#Redis%EB%A5%BC%20%ED%99%9C%EC%9A%A9%ED%95%98%EC%97%AC%20%EC%84%B8%EC%85%98%20%EC%A0%80%EC%9E%A5%EC%86%8C%EB%A1%9C%20%EC%82%AC%EC%9A%A9%ED%95%A0%20%EA%B2%BD%EC%9A%B0%EC%9D%98%20%EC%9E%A5%EC%A0%90%EA%B3%BC%20%EB%8B%A8%EC%A0%90%EC%9D%80%20%EB%AC%B4%EC%97%87%EC%9D%B8%EA%B0%80%EC%9A%94%3F-1-33

- [NHN FORWARD 2021](https://www.youtube.com/watch?v=92NizoBL4uA)
</details>