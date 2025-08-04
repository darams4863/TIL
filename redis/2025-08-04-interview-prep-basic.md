---
title: "Redis 면접용 질문 - basic"
date: 2025-08-04
categories:
  - redis
tags:
  - redis
  - interview
  - questions
  - answers
---

# Redis Basic 면접 질문 & 답변

3년차 파이썬 백엔드 개발자 기준, Redis 화이트보드/면접 대비용 기본 질문 18개

---

## 1️⃣ Redis 기본 개념

**Q1. Redis는 무엇이고, 어떤 특징을 가지나요?**

```text
Redis는 In-Memory 기반의 Key-Value NoSQL 데이터 저장소입니다.
RAM에 데이터를 저장해 마이크로초~밀리초 단위 접근 속도를 제공하며,
String, Hash, List, Set, Sorted Set, Stream 등 다양한 자료구조를 지원합니다.
캐시, 세션, 큐, 랭킹, Pub/Sub 등 다양한 용도로 활용됩니다.
```

**꼬리질문**

* Q1-1. 왜 메모리 기반인데도 안정적인가요?

```text
RDB Snapshot, AOF(Append Only File)로 영속성을 제공하고,
Master-Replica, Sentinel/Cluster 모드로 가용성을 높입니다.
```

* Q1-2. Redis는 싱글 스레드인데 왜 빠른가요?

```text
Context Switching 비용이 없고, epoll 기반 이벤트 루프로
I/O 멀티플렉싱을 수행해 수천 개 연결도 효율적으로 처리합니다.
```

---

## 2️⃣ 자료구조 & 활용

**Q2. Redis에서 지원하는 자료구조 5가지를 말하고 용도를 설명해주세요.**

```text
1. String: 단순 Key-Value, 카운터, 락
2. Hash: 객체 저장, 유저 프로필 관리
3. List: 큐(FIFO), 작업 대기열
4. Set: 중복 없는 집합, 팔로워 목록
5. Sorted Set: 점수 기반 정렬, 랭킹
추가: Stream – 메시징/로그 수집
```

**꼬리질문**

* Q2-1. Sorted Set과 List 차이와 활용 예시는?

```text
Sorted Set: score 기반 자동 정렬 → 랭킹, 일정 관리
List: 순차 자료구조 → 작업 큐, 스택/큐
```

* Q2-2. Stream과 Pub/Sub의 차이는?

```text
Pub/Sub: 실시간 브로드캐스트, 메시지 보관 안 됨
Stream: 메시지 보존, Consumer Group, ack/재처리 가능
```

---

## 3️⃣ TTL & 메모리 관리

**Q3. Redis에서 키 만료(TTL)는 어떻게 동작하나요?**

```text
Lazy Expiration + Active Expiration 혼합
1. Lazy: 키 접근 시 TTL 확인 후 만료 처리
2. Active: 주기적으로 샘플링해 만료된 키 삭제
```

**꼬리질문**

* Q3-1. TTL 수백만 개 시 어떤 문제가 발생하나요?

```text
동시에 많은 키 만료 → CPU spike, 응답 지연 (TTL Storm)
해결: TTL 분산, random offset, 만료 시간 분산
```

* Q3-2. 메모리 부족 시 Redis 동작은?

```text
maxmemory 정책에 따라 eviction
예: allkeys-lru, volatile-lru, allkeys-random 등
```

---

## 4️⃣ Persistence & 복제

**Q4. Redis의 영속성 방식에는 무엇이 있나요?**

```text
1. RDB(Snapshot): 특정 시점 전체 메모리 덤프
2. AOF(Append Only File): 모든 write 로그 저장
3. Mixed Mode: RDB + AOF 혼합
```

**꼬리질문**

* Q4-1. RDB와 AOF의 장단점 비교?

```text
RDB: 복구 빠름, 용량 적음 / 최신 데이터 일부 유실 가능
AOF: 데이터 유실 적음 / 파일 커짐, 복구 느림
```

* Q4-2. Redis 복제(Replication) 방식은?

```text
Master → Replica 비동기 복제
Replica 지연(lag) 발생 가능, WAIT 명령어로 동기 보장 가능
```

---

## 5️⃣ 성능 & 트러블슈팅

**Q5. Redis 성능 최적화를 위해 어떤 기법을 사용하나요?**

```text
1. Pipeline: 네트워크 왕복 최소화
2. Lua Script: 원자적 복잡 로직 처리
3. SCAN: KEYS 대신 비차단 탐색
4. TTL & Eviction으로 메모리 관리
5. Slowlog로 성능 모니터링
```

**꼬리질문**

* Q5-1. KEYS 명령어를 사용하면 어떤 문제가 발생하나요?

```text
O(N) 연산으로 전체 Redis를 블로킹할 수 있음 → SCAN으로 대체
```

* Q5-2. Cache Stampede 방지법은?

```text
1. 분산 락 (SETNX + TTL)
2. TTL 분산(random offset)
3. 백그라운드 리프레시
```

---

## 6️⃣ 분산 락

**Q6. Redis로 분산 락을 구현하는 방법을 설명해주세요.**

```text
1. SETNX + EX/PX 옵션으로 락 획득
2. Lua Script로 GET + DEL 원자적 해제
3. TTL 설정으로 Deadlock 방지
```

**꼬리질문**

* Q6-1. Race Condition 방지법은?

```text
Lua Script로 GET과 DEL을 원자적으로 수행해
다른 프로세스 락을 실수로 삭제하지 않도록 보장
```

* Q6-2. Redlock은 언제 필요한가요?

```text
단일 Redis 장애 대비나 멀티 인스턴스 환경에서
과반수 인스턴스 락 획득으로 안전성을 높일 때 사용
```


--- 
<details>
<summary>cf. reference</summary>

- https://jaehyuuk.tistory.com/216
- https://sunro1994.tistory.com/333#Redis%EB%A5%BC%20%ED%99%9C%EC%9A%A9%ED%95%98%EC%97%AC%20%EC%84%B8%EC%85%98%20%EC%A0%80%EC%9E%A5%EC%86%8C%EB%A1%9C%20%EC%82%AC%EC%9A%A9%ED%95%A0%20%EA%B2%BD%EC%9A%B0%EC%9D%98%20%EC%9E%A5%EC%A0%90%EA%B3%BC%20%EB%8B%A8%EC%A0%90%EC%9D%80%20%EB%AC%B4%EC%97%87%EC%9D%B8%EA%B0%80%EC%9A%94%3F-1-33

- [NHN FORWARD 2021](https://www.youtube.com/watch?v=92NizoBL4uA)
</details>