---
title: "Redis 소개 및 기본 개념"
date: 2025-07-29
categories:
  - redis
tags:
  - redis
  - database
  - cache
---

# Redis 소개
- Redis는 (Remote Dictionary Server의 약자로) 키(Key) : 값(Value) 해시 맵과 같은 구조를 가진 In-Memory 기반의 NoSQL 데이터베이스입니다. 
- 여기서 인메모리 데이터 구조이다라는 뜻은 하드디스크(일반 MySql이나 Oracle과는 다르게, SSD, HDD)에서 데이터를 처리하는 것이 아니라 RAM에 저장된다는 말이고 -> 이는 속도가 밀리초에서 마이크로 초 단위로 향상된다는 의미이다. 대신 서버가 꺼지면 데이터가 날아갈 수 있다는 단점이 있고, 이로 인해 RDB/AOF로 백업하는 것이 필수이다. 추후 다룰 예정.
- Redis는 다양한 데이터 타입을 지원합니다
- 또한 그저 key-value로만 저장하는 것이 아니라, String, List, Set, Hash, Sorted Set와 같은 여러 자료구조를 지원한다. 
    - String → 단순 값
    - List → 큐, 스택
    - Set / Sorted Set → 중복 없는 집합, 랭킹 시스템
    - Hash → JSON 비슷한 구조 (user: {name: "A", age: 20})
    - Stream → 이벤트 로그, 카프카 비슷하게 사용 가능
=> 이 자료구조 덕분에 캐시 + 큐 + 랭킹 + pub/sub까지 다 가능  
- redis가 NoSQL이라는 말은, key-value 기반으로 일반적인 RDB와는 다르게 테이블도 없고 스키마도 없어서 e.g. alter table을 해줄 필요가 없고, key -> value 형태로 다양한 자료구조를 저장할 수 있기 때문에, RDB처럼 JOIN, 복잡한 트랜잭션은 불가능 하지만 대신 속도와 단순성을 최적화 했다는 특징이 있다. 


## 주요 특징
- **인메모리 저장**: 빠른 읽기/쓰기 성능
- **다양한 데이터 타입**: String, List, Set, Hash, Sorted Set, Stream, Geospatial, HyperLogLog, Bitmap, Bitfield
- **영속성**: RDB, AOF 방식으로 데이터 영속성 보장
- **클러스터링**: 수평적 확장 가능

- 여기서 영속성에 대하여..
  - Redis는 휘발성인 인메모리에 데이터를 저장하기 때문에 데이터를 영구적으로 저장할 수 없다. cache 용도로만 사용한다면 상관없겠지만, 캐시 이외의 용도로 사용한다면 데이터 백업이 필수다. 
  - 이에 Redis는 데이터를 영속화하기 위한 `RDB(Redis Database)`와 `AOF(Append Only File)` 2가지 방법을 제공한다. 
  - RDB: 
    - 설정한 일정 시간 단위로 레디스 DB의 스냅샷을 백업하고, 필요시 특정한 시점의 스냅샷으로 롤백할 수 있다.
  - AOF:
    - 모든 쓰기 작업을 로그 파일에 기록하여 데이터 복구를 보장한다.

## 기본 명령어
- 맥북에서
```bash
// Homebrew로 설치
brew install redis

//  Redis 서버 실행
redis-server

// 다른 터미널에서 클라이언트 접속
redis-cli
```

- Ubuntu에서
```bash 
sudo apt update
sudo apt install redis-server -y

// Redis 서버 시작
sudo systemctl start redis-server

// 부팅 시 자동 시작 설정
sudo systemctl enable redis-server

// 동작 확인
redis-cli ping
// → PONG
``` 

- Docker에서
```bash 
// 단일 컨테이너 실행 (-d 백그라운드 실행, -p 6379:6379 : 호스트 6379 포트와 컨테이너 6379 포트 연결)
docker run -d --name my-redis -p 6379:6379 redis

// 컨테이너 내부에서 redis-cli 실행
docker exec -it my-redis redis-cli
``` 


## 레디스가 싱글 스레드 모델임에도 높은 성능을 보장하는 이유 (I/O Multiplexing)
### 1. 싱글 스레드 이벤트 루프 → 락(lock) 비용, 문맥 전환 없음 
- 요약:
    - Redis는 한 번에 하나의 명령만 처리하기 때문에 락(lock) 경합이 전혀 없고, 멀티스레드에서 발생하는 문맥 전환 비용도 발생하지 않습니다. 이 덕분에 CPU 캐시 효율이 높아져 요청을 매우 빠르게 처리할 수 있습니다.
    ```
    멀티 스레드: 
    스레드1 실행 → 캐시 적재 → 전환 → 캐시 Flush → 스레드2 적재 (반복)

    싱글 스레드:
    스레드1 계속 실행 → 캐시 유지 → 반복 접근 속도 빠름
    ```
- 싱글 스레드란? 
    - 한번에 하나의 스레드(=작업 흐름)만 실행하는 구조 
    - Redis는 명령을 처리하는 메인 스레드가 하나뿐이다 -> 동시에 여러 명령을 처리하는 것처럼 보이지만, 사실은 한 줄로 처리됨 
    - 비유: 
        - 싱글 스레드 = 계산대 1개 있는 편의점
	    - 멀티 스레드 = 계산대 여러 개 있는 대형 마트
- 이벤트 루프란? 
    - 싱글 스레드가 여러 클라이언트 요청을 빠르게 처리할 수 있도록 I/O 이벤트를 기다렸다가 처리하는 반복 구조를 말한다 
    - Redis의 이벤트 루프는 아래와 같이 동작한다: 
        1. I/O Multiplexing (epoll, kqueue 같은 OS 기능)으로 여러 소켓 상태 감시
        2. 읽을 게 있는 소켓이 생기면 이벤트 루프가 처리
        3. 결과를 쓰고 다시 감시 상태로 돌아감
    - 비유:
	    - 계산대 직원(싱글 스레드)이 한 명이지만, 여러 손님이 줄 서 있는 게 아니라 손님이 물건 꺼냈을 때만 알림을 받고 처리하는 구조        
- 락 경합(Lock contention)이 없다는 의미? 
    - 멀티 스레드 환경에서는 공유 자원(예: 메모리, 데이터 구조)을 여러 스레드가 동시에 접근함
    ```
    → 그래서 뮤텍스/락으로 동기화해야 함
    → 동시에 접근하려고 하면 락 경합 발생 (대기 시간 ↑, 성능 ↓)
        •	싱글 스레드는 어차피 한 번에 하나의 명령만 실행
    → 락이 필요 없음 → 락 경합 0%
    ```
    - 정리: 
        - 락 경합 없음 = 동시에 자원 접근할 경쟁이 없으니 대기 시간도 없음
- 문맥 전환(Context Switch) 비용? 
    - 멀티 스레드/멀티 프로세스에서는 CPU가 스레드를 번갈아 실행함
        ```
        → 실행 중이던 스레드 상태 저장 + 새 스레드 상태 불러오기 필요
        → 이게 문맥 전환(Context Switch)
        ```
    - 하지만 싱글 스레드에서는 스레드가 하나라서
        ```
        → 스위칭할 필요가 없음 → 문맥 전환 비용 0
        ```
- CPU 캐시 효율이 높아지는 이유
    - CPU는 자주 쓰는 데이터를 L1/L2 캐시에 저장해두고 빠르게 접근함
    - 멀티 스레드에서는 스레드 전환할 때 **캐시가 무효화(Flush)**됨 → 새 스레드 데이터 로딩 → 캐시 미스 ↑
    - 싱글 스레드는 한 스레드만 계속 돌아가므로 → 캐시가 유지되어 연속적 접근 효율 ↑


### 2. I/O Multiplexing(epoll/kqueue) - Event Loop & 내부 구조
- 요약:
    - I/O Multiplexing 기법: 
        - Redis는 싱글 스레드지만 I/O Multiplexing으로 높은 성능을 냅니다.
        구체적으로, Redis는 내부적으로 epoll(리눅스)이나 kqueue(맥) 같은 OS 이벤트 감시 시스템을 사용합니다.
        OS 이벤트 감시 시스템을 사용해서 수천, 수만 개 클라이언트 연결/소켓의 연결을 동시에 유지해도, 읽기·쓰기 준비가 된 소켓만 이벤트 큐에 등록해 처리하므로 불필요한 CPU 낭비가 없습니다. 네트워크 I/O는 디스크 I/O보다 훨씬 빠르기 때문에 싱글 스레드임에도 비효율 없이 네트워크 I/O를 처리할 수 있습니다.
    - e.g. 
    ```
    [클라이언트1]   [클라이언트2]   [클라이언트3]
        ↓               ↓               ↓
    TCP 소켓        TCP 소켓        TCP 소켓
        ↓               ↓               ↓
    ───────────── OS 커널 (epoll) ─────────────
        ↳ 읽기/쓰기 준비된 소켓만 알려줌
                        ↓
            [이벤트 큐 + 이벤트 루프]
            1. 소켓 이벤트 꺼내 처리
            2. 응답 보내기
    ```

#### Redis Event Loop 상세 구조
**핵심 구성 요소:**
1. **File Descriptor (파일 디스크립터)**
   - 네트워크 소켓, 파일, 파이프 등을 추상화한 정수
   - Redis에서는 주로 TCP 소켓을 의미
   - 예: 클라이언트 연결마다 고유한 fd 할당

2. **epoll (Linux) / kqueue (macOS)**
   - OS 커널이 제공하는 이벤트 감시 시스템
   - 수천 개 fd를 효율적으로 모니터링
   - "데이터가 준비된 fd"만 알려줌

3. **Event Loop (이벤트 루프)**
   - 무한 루프로 이벤트를 처리하는 redis의 메인 로직
   - epoll에서 준비된 이벤트를 가져와서 처리

#### File Descriptor 처리 흐름
```bash
# 1. 클라이언트 연결 수락
accept() → 새로운 fd 생성 (예: fd=5)

# 2. epoll에 fd 등록
epoll_ctl(EPOLL_CTL_ADD, fd=5, EPOLLIN)  # 읽기 이벤트 감시

# 3. 이벤트 루프에서 대기
epoll_wait() → 준비된 fd 목록 반환

# 4. 준비된 fd 처리
for fd in ready_fds:
    if fd == 5:  # 클라이언트 요청
        data = read(fd=5)  # 데이터 읽기
        result = process_command(data)  # Redis 명령 처리
        write(fd=5, result)  # 응답 전송
```

#### Event Loop 상세 동작 과정
```python
# Redis 이벤트 루프 의사 코드
def redis_event_loop():
    # 1. epoll 인스턴스 생성
    epoll_fd = epoll_create()
    
    # 2. 서버 소켓을 epoll에 등록
    server_fd = create_server_socket()
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, server_fd, EPOLLIN)
    
    # 3. 무한 루프 - 이벤트 처리
    while True:
        # 3-1. 준비된 이벤트 대기 (블로킹)
        events = epoll_wait(epoll_fd, timeout=100ms)
        
        # 3-2. 각 이벤트 처리
        for fd, event_type in events:
            if fd == server_fd:
                # 새 클라이언트 연결
                client_fd = accept(server_fd)
                epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, EPOLLIN)
                
            else:
                # 클라이언트 요청 처리
                if event_type == EPOLLIN:  # 읽기 가능
                    data = read(fd)
                    if data:
                        result = process_redis_command(data)
                        write(fd, result)
                    else:
                        # 연결 종료
                        close(fd)
                        epoll_ctl(epoll_fd, EPOLL_CTL_DEL, fd)
```

#### epoll vs select/poll 비교
```bash
# select 방식 (구식)
select(fd_set, timeout)  # 모든 fd를 순회하며 확인
# 문제: fd 개수에 비례하여 성능 저하

# epoll 방식 (현대적)
epoll_wait()  # 준비된 fd만 반환
# 장점: fd 개수와 무관하게 O(1) 성능
```

#### 면접에서 epoll vs select/poll 설명해야 할 때
- **Q: "epoll과 select의 차이점을 설명해주세요"**
- **A: "네, 두 방식의 핵심 차이점은 '어떻게 준비된 소켓을 찾는가'입니다.**
- **select 방식 (구식):**
    - 모든 파일 디스크립터(fd)를 **순차적으로 하나씩 확인**합니다
    - 마치 1000명의 학생이 있는 교실에서 "숙제 다 했나?"라고 한 명씩 물어보는 것과 같습니다
    - 연결 수가 늘어날수록 성능이 선형적으로 저하됩니다 (O(n) 복잡도)
    - 예를 들어 10,000개 연결이 있으면 10,000번 확인해야 합니다
- **epoll 방식 (현대적):**
    - OS 커널이 **준비된 소켓만 알려줍니다**
    - 마치 교실에서 "숙제 다 한 사람만 손을 들어!"라고 하면 손 든 사람만 알 수 있는 것과 같습니다
    - 연결 수와 무관하게 일정한 성능을 유지합니다 (O(1) 복잡도)
    - 10,000개 연결이 있어도 실제로 데이터가 준비된 10개만 처리하면 됩니다
- **왜 이게 중요한가요?**
    - Redis는 수천, 수만 개의 클라이언트 연결을 동시에 처리해야 합니다
    - select 방식으로는 연결이 많아질수록 성능이 급격히 떨어집니다
    - epoll 덕분에 Redis는 싱글 스레드임에도 높은 동시성을 보장할 수 있습니다
- **면접 팁:**
    - "select는 모든 것을 확인하고, epoll은 준비된 것만 알려준다"가 핵심
    - 비유를 들어가며 설명하면 이해하기 쉽습니다
    - 실제 성능 차이(O(n) vs O(1))를 언급하면 좋습니다"

#### Redis에서 I/O 처리 방식
**핵심 개념:**
- Redis는 **이벤트 기반**으로 동작
- OS가 "데이터가 준비된 소켓"만 알려줌
- Redis는 준비된 소켓만 처리 → CPU 낭비 없음

**실무에서 중요한 점:**
- Redis는 **I/O 바운드** 애플리케이션
- 네트워크 처리 성능이 전체 성능의 핵심
- 싱글 스레드지만 수천 개 연결 동시 처리 가능

- I/O 작업이란?
    - Input/Output의 줄임말, 데이터를 주고받는 행위 전반 
    - 종류: 
        - Disk I/O: 파일 읽기/쓰기 (DB에서 디스크 접근)
        - Network I/O: TCP 소켓을 통해 데이터 송수신
        - Memory I/O: CPU ↔ RAM ↔ Cache 간 데이터 이동
    - Redis는 디스크보다는 네트워크 I/O가 중요. 클라이언트와 데이터를 주고받아야 하니까.
- 소켓? 
    - 네트워크에서 데이터를 주고받기 위한 논리적 통로 (IP + Port를 기반으로 TCP/UDP 연결을 담당)
    - Redis 내부에서 클라이언트 요청을 처리할 때 항상 소켓 단위로 I/O를 수행한다 
- 이벤트 감시 시스템(epoll / kqueue)
    - 이벤트 감시 시스템 = OS 커널이 제공하는 네트워크 이벤트 감시 기능
    - 역할:
        - 수많은 소켓의 상태(읽기/쓰기 가능 여부)를 커널이 대신 감시
        - 준비된 소켓만 알려줌 → CPU 낭비 방지
    - OS별 구현: 
        - Linux → epoll
	    - macOS/BSD → kqueue
    - 즉, Redis는 스스로 1만 개 소켓을 매번 확인하지 않고 커널에게 "이 소켓들 상태 바뀌면 알려줘"라고 맡기는 것

#### 면접에서 실제로 물어보는 질문들
**Q: "Redis가 싱글 스레드인데 왜 빠른가요?"**
A: "세 가지 이유가 있습니다:
1. 락 경합이 없는 싱글 스레드 이벤트 루프
2. I/O 멀티플렉싱으로 네트워크 처리 최적화
3. 메모리 기반 처리로 디스크 I/O 최소화"

**Q: "Redis에서 대용량 트래픽 처리 시 병목은 어디일까요?"**
A: "주로 네트워크 I/O가 병목입니다. Redis는 I/O 바운드 애플리케이션이므로 네트워크 처리 성능이 중요합니다."

**Q: "Redis가 수천 개 연결을 어떻게 처리하나요?"**
A: "이벤트 기반으로 동작해서 데이터가 준비된 소켓만 처리합니다. OS가 준비된 소켓을 알려주므로 효율적으로 처리할 수 있습니다."

**Q: "epoll과 select의 차이점은?"**
A: "select는 모든 fd를 순회하지만, epoll은 준비된 fd만 반환합니다. 따라서 연결 수가 많을 때 epoll이 훨씬 효율적입니다."

**Q: "Redis 이벤트 루프에서 파일 디스크립터는 어떻게 처리되나요?"**
A: "클라이언트 연결마다 고유한 fd가 할당되고, epoll에 등록되어 이벤트를 감시합니다. 데이터가 준비되면 이벤트 루프에서 처리합니다."


### 3. 모든 데이터를 메모리에서 처리 → 디스크 I/O 최소화
- 요약: 
    - 마지막으로 내부적으로 최적화된 자료구조 덕분에 Redis는 대부분의 연산을 메모리 안에서 O(1) ~ O(log n)정도로 작업을 처리할 수 있게 해놨습니다. 이렇게 Redis의 내부적으로 최적화된 자료 구조 덕분에 디스크를 자주 안쓰고, CPU랑 메모리 만으로도 대부분의 동작이 가능하기 때문에 I/O 작업에서 빠른 속도를 보여줍니다.


---
<details>
<summary>cf. reference</summary>

- https://velog.io/@ohjinseo/Redis%EA%B0%80-%EC%8B%B1%EA%B8%80-%EC%8A%A4%EB%A0%88%EB%93%9C-%EB%AA%A8%EB%8D%B8%EC%9E%84%EC%97%90%EB%8F%84-%EB%86%92%EC%9D%80-%EC%84%B1%EB%8A%A5%EC%9D%84-%EB%B3%B4%EC%9E%A5%ED%95%98%EB%8A%94-%EC%9D%B4%EC%9C%A0-IO-Multiplexing

</details>
