---
title: "Redis TTL & Eviction 정리 (이론)"
date: 2025-07-30
categories:
  - redis
tags:
  - redis
  - ttl
  - eviction
  - big-key
  - hot-key
---

# Redis TTL & Eviction (이론 정리)
- Redis는 인메모리 기반의 Key-Value 데이터 저장소로, **만료(Expiration)**와 **메모리 관리(Eviction)** 정책을 이해하는 것이 중요하다.  
- TTL 설정, Eviction 정책, big key/hot key 문제에 대해서 알아보자.

---

## 1️⃣ TTL (Time To Live) & Expiration
Redis는 키에 유효기간(Time To Live, TTL)을 설정할 수 있으며, 만료된 키는 두 가지 정책으로 제거된다.

### TTL 설정
- `EXPIRE key seconds`  
- `SET key value EX seconds` (생성 시 TTL 부여)
- `TTL key` (남은 TTL 조회)
- `PERSIST key` (TTL 제거)

### 만료 정책
Redis는 **Lazy Expiration**과 **Active Expiration**을 혼합 사용한다.

1. **Lazy Expiration (지연 삭제)**  
   - 클라이언트가 키에 접근할 때 만료 여부 확인 후 삭제  
   - CPU 부하가 적음  
   - 단점: 접근하지 않는 만료 키는 메모리에 남아있음

2. **Active Expiration (주기적 스캔)**  
   - 백그라운드에서 주기적으로 만료 키를 샘플링 기반으로 삭제  
   - CPU 사용량과 삭제 빈도 사이 트레이드오프 존재

### TTL Storm
- 다수의 키가 같은 시점에 만료될 경우 발생
- Active Expiration이 대량의 키를 동시에 제거 → CPU Spike / Latency 증가
- **해결책**
  - TTL 값에 랜덤 offset 추가
  - 만료 시간 분산 (Expiration spread)

---

## 2️⃣ Eviction (메모리 관리 정책)

Redis에서 `maxmemory`를 설정하면 메모리 초과 시 **Eviction** 정책에 따라 키를 제거한다.

### 조건
1. `maxmemory` 설정 필요
2. `maxmemory-policy` 설정

### Eviction 정책

| 정책             | 설명                                |
|-----------------|-----------------------------------|
| **noeviction**   | 메모리 초과 시 쓰기 명령 실패 (기본값) |
| **volatile-lru** | TTL 있는 키 중 LRU 제거             |
| **volatile-lfu** | TTL 있는 키 중 LFU 제거             |
| **volatile-ttl** | TTL 있는 키 중 만료 가까운 순 제거   |
| **volatile-random** | TTL 있는 키 중 랜덤 제거         |
| **allkeys-lru**  | 전체 키 중 LRU 제거                 |
| **allkeys-lfu**  | 전체 키 중 LFU 제거                 |
| **allkeys-random** | 전체 키 중 랜덤 제거             |

- **LRU (Least Recently Used)**: 가장 오래 사용되지 않은 키 제거
- **LFU (Least Frequently Used)**: 사용 빈도 낮은 키 제거
- **volatile-***: TTL 있는 키만 대상
- **allkeys-***: 전체 키 대상

---

## 3️⃣ Big Key & Hot Key 문제

### Big Key
- 단일 키의 값이 매우 큰 경우 (수 MB 이상)
- **문제점**
  - DEL 시 O(N) → 블로킹 가능
  - RDB/AOF 저장 시 Fork Latency 증가
- **대응**
  - 데이터 분할 저장 (샤딩)
  - Lazy deletion (`UNLINK`) 활용

### Hot Key
- 트래픽이 특정 키에 집중되는 경우
- **문제점**
  - 싱글 스레드 구조라 해당 키 처리로 CPU 편중
  - 클러스터 환경에서는 특정 노드 부하 집중
- **대응**
  - Key sharding (`user:{id}%N`)
  - Local cache (Caffeine, Guava 등)
  - Lua script를 통한 원자적 처리

---

## 4️⃣ 핵심 요약

- TTL은 Lazy + Active Expiration 혼합
- TTL Storm → 대량 만료 시점 분산 필요
- Eviction 정책은 LRU/LFU, volatile/allkeys 조합
- big key → 삭제/저장 시 성능 저하
- hot key → 트래픽 집중으로 단일 노드 병목 발생