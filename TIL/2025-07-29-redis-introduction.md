---
title: "Redis 소개 및 기본 개념"
date: 2025-01-27
categories:
  - redis
tags:
  - redis
  - database
  - cache
---

# Redis 소개
- Redis는 Remote Dictionary Server의 약자로 키(Key) : 값(Value) 해시 맵과 같은 구조를 가진 NoSQL 데이터베이스입니다. 

- Redis는 인메모리 데이터 구조 저장소로, 다양한 데이터 타입을 지원하는 NoSQL 데이터베이스입니다.
- 여기서 인메모리 데이터 구조이다라는 뜻은 데이터가 하드디스크(일반 MySql이나 Oracle과는 다르게, SSD, HDD)에서 데이터를 처리하는 것이 아니라 RAM에 저장된다는 말이고 -> 이는 속도가 마이크로 초에서 밀리초 단위로 향상된다느 의미이다. 대신 서버가 꺼지면 데이터가 날아갈 수 있다는 단점이 있고, 이로 인해 RDB/AOF로 백업하는 것이 필수이다. 추후 다룰 예정.
- 또한 그저 key-value로만 저장하는 것이 아니라, String, List, Set, Hash, Sorted Set와 같은 여러 자료구조를 지원한다. 
	•	String → 단순 값
	•	List → 큐, 스택
	•	Set / Sorted Set → 중복 없는 집합, 랭킹 시스템
	•	Hash → JSON 비슷한 구조 (user: {name: “A”, age: 20})
	•	Stream → 이벤트 로그, 카프카 비슷하게 사용 가능
=> 이 자료구조 덕분에 캐시 + 큐 + 랭킹 + pub/sub까지 다 가능  
- redis가 NoSQL이라는 말은, key-value 기반으로 일반적인 RDB와는 다르게 테이블도 없고 스키마도 없어서 e.g. alter table을 해줄 필요가 없고, key -> value 형태로 다양한 자료구조를 저장할 수 있기 때문에, RDB처럼 JOIN, 복잡한 트랜젝션은 불가능 하지만 대신 속도와 단순성을 최적화 했다는 특징이 있다. 


## 주요 특징
- **인메모리 저장**: 빠른 읽기/쓰기 성능
- **다양한 데이터 타입**: String, List, Set, Hash, Sorted Set
- **영속성**: RDB, AOF 방식으로 데이터 영속성 보장
- **클러스터링**: 수평적 확장 가능

- 여기서 영속성에 대하여..
  - Redis는 휘발성인 인메모리에 데이터를 저장하기 때문에 데이털르 영구적으로 저장할 수 없다. cache 용도로만 사용한다면 상관없겠지만, 캐시 이외의 용도로 사용한다면 데이터 백업이 필수다. 
  - 이에 Redis는 데이터를 영속화하기 위한 `RDB(Redis Database)`와 `AOF(Append Only File)` 2가지 방법을 제공한다. 
  - RDB: 
    - 설정한 일정 시간 단위로 레디스 DB의 스냅샷을 백업하고, 필요시 특정한 시점의 스냅샷으로 롤업할 수 있다.

## 기본 명령어

```bash
# Redis 서버 시작
redis-server

# Redis 클라이언트 연결
redis-cli

# 기본적인 키-값 저장
SET key value
GET key
```

## 사용 사례

- 캐싱
- 세션 저장소
- 실시간 분석
- 메시지 큐

이 포스트에서는 Redis의 기본 개념과 사용법에 대해 알아보겠습니다. 