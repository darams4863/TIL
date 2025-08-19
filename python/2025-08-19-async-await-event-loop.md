---
title: "파이썬의 동기 vs 비동기"
date: 2025-08-19
categories:
  - python
tags:
  - python
  - async
  - asyncio
---

# 파이썬의 동기 vs 비동기
- 개발자라면 한 번씩 듣게되는 동기(Synchronous), 비동기
(Asynchronous), 블럭(Block), 넌블럭(Non-block)을 
Python코드를 통해 알아보자. 

## 📋 목차
1. **개념 및 문법** - async/await, asyncio, 이벤트 루프
2. **실무 활용** - FastAPI, aiohttp, asyncpg, DB 연결
3. **면접 대비** - 차이점, 원리 설명, 예시 질문

---

## 1. 개념 및 문법

### 1.1 async / await란?
- 비동기는 I/O 대기시간이 많은 작업에서 CPU를 놀리지 않고, 다른 작업을 처리할 수 있게해서 "기다림이 많은 프로그램"에서 적은 자원으로 성능을 극대화 하는 전략이다. 
- 파이썬에서 비동기를 어떻게 지원하는지 알아보자. 

#### 기본 개념
- `async def`: 
    - 파이썬에서 비동기 함수를 정의할 떄 사용하는 키워드로, 이 키워드를 붙이면 해당 함수는 일반 함수처럼 실행되지 않고, `코루틴 객체`를 반환한다 
        - 예: 하단 예시에서의 fetch_data()라는 async def 키워드를 사용해서 정의한 함수는 **즉시 실행되지 않으며**, 코루택 객체를 반환하게 된다. 즉, result = fetch_data()만 해서는 "data"가 반환되지 않고, 이 코루틴을 스케줄링 하거나 await로 대기해야 진짜 실행이 된다 
- `await`: 
    - await는 코루틴의 실행을 잠시 멈추고, 해당 작업이 완료될 떄까지 기다리겠다는 의미로 사용되는 키워드이다 
    - 단, **async def 안에서만 사용 가능하다** (await는 단독으로 쓸 수 없다)
        - 예: 하단에서 fetch_data()는 코루틴 객체라, await를 만나야 비로소 실행되는데, 실행 중 다른 I/O 작업이 끝날 수 있도록 `이벤트 루프`가 컨트롤 해준다.
        즉, **블로킹 없이 다른 작업을 진행 가능하게 해주는 핵심 도구**이다. (cf. 추후 더 설명 예정)
- 코루틴(coroutine): 
    - 비동기 함수(async def)를 실행하면 만들어지는 특수한 객체이다.
    - 이 코루틴 객체는 일반 함수처럼 즉시 결과를 반환하지 않고, 나중에 결과를 받을 수 있도록 "중단 가능함 함수"처럼 작동한다. 
    - await를 통해 코루틴의 실행을 중단하고 재개할 수 있기 때문에
여러 작업을 비동기적으로 동시에 처리할 수 있게 해준다 

```python
import asyncio

async def fetch_data():
    await asyncio.sleep(1)  # 비동기 대기
    return "data"

async def main():
    result = await fetch_data()  # 결과를 기다림
    print(result)

# 실행
asyncio.run(main())

# 요약: 
# • async def: “예약된 작업을 등록하는 계약서” 작성
# • await: “그 작업이 끝날 때까지 잠시 대기” (다른 작업 가능)
# • coroutine: “예약된 작업 자체”, 아직 실행되지 않았지만 조건에 따라 실행될 준비가 된 객체
```

### 1.2 왜 asyncio를 써야 하나요?
- 파이썬에서 async def와 await를 사용해서 비동기 함수를 작성했으면, 이 비동기 함수는 단독으로는 동작하지 않는다. 
정의된 비동기 함수는 "코루틴 객체"일 뿐이기 때문에, 이걸 실제로 실행하려면 `asyncio`의 도움이 필요하다. 
- **asyncio**: 이벤트 루프를 생성, Task/Queue 관리, 타이머, 스케줄링 등 전체 비동기 실행 환경을 제공하는 라이브러리 

#### 1.2.1 asyncio의 주요 메서드 
1. asyncio.run(coro)
- 프로그램 진입점에서 사용 
- 이벤트 루프 생성 -> 실행 -> 종료까지 자동으로 처리 

```python
async def main():
    print("Hello, asyncio!")
    await asyncio.sleep(1)
    print("Goodbye!")

# 메인 프로그램에서 실행
if __name__ == "__main__": # cf. __name__ 은 파이썬 인터프리터가 자동으로 정의해주는 전역 변수 중 하나로, 해당 파일이 다른 모듈에서 임포트된 것이 아니고, 직접 해당 파일을 실행할 때 __name__ == "__main__"이 참이 된다
    asyncio.run(main())
```

2. asyncio.create_task(coro)
- 코루틴을 Task로 즉시 스케줄링 
- 병렬 실행하고 싶을 때 await 없이 먼저 등록 가능 
- 이후 await task로 결과 받음

```python
async def fetch_data(id):
    await asyncio.sleep(1)  # API 호출 시뮬레이션
    return f"Data {id}"

async def main():
    # 태스크들을 먼저 생성 (병렬로 실행 시작)
    task1 = asyncio.create_task(fetch_data(1))
    task2 = asyncio.create_task(fetch_data(2))
    
    # 나중에 결과를 받음
    result1 = await task1
    result2 = await task2
    
    print(result1, result2)  # Data 1 Data 2

""" 
[동작 흐름]
1. create_task()가 실행되면 
    - fetch_data(1)과 fetch_data(2) 코루틴이 각각 테스크로 등록된다.
    - 여기서부터 이벤트 루프가 두 작업을 병렬적으로 관리하기 시작. 
    단, 단일 스레드 내에서 "스케줄링"만 하는거지, 멀티스레드가 아니다.
2. await task1을 만나면 
    - task1이 실행되기 시작하고 fetch_data(1) 내부로 들어간다. 
    - await asyncio.sleep(1)을 만나면 -> "지금은 1초 기다려야 하니까, 이 작업은 잠깐 스탑할게요." 하고 이벤트 루프에 제어권을 반환한다. 
    - 이떄, 이벤트 루프는 다음 실행 가능한 테스크린 task2로 전환한다. 
    (즉, 컨텍스트 스위칭)
3. 이제 task2가 실행된다
    - task2도 fetch_data(2) -> await asyncio.sleep(1) 까지 실행되고, 똑같이 이벤트 루프에 제어권을 넘긴다 
4. 이벤트 루프는 등록된 sleep(1) 작업이 끝나기를 기다린다 
    - 두 작업 모두 비동기적으로 1초 뒤에 동시에 깨어난다 
    - 그러면 순서대로 다시 실행, 각각 return문을 실행 
    - 결과적으로 task1, task2는 거의 동시에 끝나게 된다 
-> await을 만나면 해당 태스크는 일시정지되고, 이벤트 루프가 다른 태스크로 컨텍스트를 전환하여 효율적으로 CPU를 사용하게 해줍니다
"""
```

3. asyncio.gather(*coros)
- 여러 코루틴을 병렬 실행 
- 결과는 리스트로 반환됨 ([결과 1, 결과 2, 결과 3])
- 하나라도 예외가 나면 전체 중단 -> return_exception = True 옵션 사용하면 전체 중단은 아니고 결과에 에러가 포함되어 나옴 

```python
async def fetch_user(id):
    await asyncio.sleep(0.5)
    return {"id": id, "name": f"User{id}"}

async def fetch_post(id):
    await asyncio.sleep(0.3)
    return {"id": id, "title": f"Post{id}"}

async def main():
    # 여러 코루틴을 병렬로 실행
    users, posts = await asyncio.gather(
        fetch_user(1),
        fetch_post(1)
    )
    print(f"User: {users}, Post: {posts}")
    
    # 예외 처리 예시
    try:
        results = await asyncio.gather(
            fetch_user(1),
            fetch_user(2),
            return_exceptions=True
        )
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Task {i} failed: {result}")
            else:
                print(f"Task {i} succeeded: {result}")
    except Exception as e:
        print(f"Gather failed: {e}")
```

4. await asyncio.sleep(seconds)
- 논블로킹으로 대기 
    - 예: API 호출 간 시간차, 디버깅 시 대기 등 

```python
async def rate_limited_api_call():
    print("API 호출 시작")
    await asyncio.sleep(1)  # 1초 대기 (논블로킹)
    print("API 호출 완료")

async def main():
    print("시작")
    await rate_limited_api_call()
    print("종료")
```

5. asyncio.wait_for(coro, timeout)
- 시간 내 완료되지 않으면 asyncio.TimeoutError 발생 
- 비동기 HTTP 요청이나 외부 API 호출에서 자주 사용 

```python
async def slow_operation():
    await asyncio.sleep(5)  # 5초 걸리는 작업
    return "완료!"

async def main():
    try:
        # 3초 타임아웃 설정
        result = await asyncio.wait_for(slow_operation(), timeout=3.0)
        print(result)
    except asyncio.TimeoutError:
        print("작업이 시간 내에 완료되지 않았습니다.")
```

6. asyncio.wait([...])
- 여러 작업 중 일부만 기다릴 때 사용 
- return_when 옵션: 
    - FIRST_COMPLETED
	- FIRST_EXCEPTION
	- ALL_COMPLETED

```python
async def worker(name, delay):
    await asyncio.sleep(delay)
    return f"{name} 완료"

async def main():
    tasks = [
        asyncio.create_task(worker("A", 3)),
        asyncio.create_task(worker("B", 1)),
        asyncio.create_task(worker("C", 2))
    ]
    
    # 첫 번째 완료된 작업만 기다림
    done, pending = await asyncio.wait(
        tasks, 
        return_when=asyncio.FIRST_COMPLETED
    )
    
    for task in done:
        result = await task
        print(f"완료된 작업: {result}")
    
    # 나머지 작업들도 완료될 때까지 기다림
    remaining_done, _ = await asyncio.wait(pending)
    for task in remaining_done:
        result = await task
        print(f"나머지 작업: {result}")
```

7. asyncio.Queue, Lock, Semaphore
- 공유 자원 보호 
- 생산자-소비자 구조 
- 동시에 실행 가능한 개수 제한 등 

```python
import asyncio
from asyncio import Queue, Lock, Semaphore

# Queue 예시 (생산자-소비자 패턴)
async def producer(queue: Queue):
    for i in range(5):
        await queue.put(f"Item {i}")
        await asyncio.sleep(0.5)
    await queue.put(None)  # 종료 신호

async def consumer(queue: Queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"소비: {item}")
        await asyncio.sleep(0.2)

# Lock 예시 (공유 자원 보호)
counter = 0
lock = Lock()

async def increment():
    global counter
    async with lock:
        temp = counter
        await asyncio.sleep(0.1)
        counter = temp + 1

# Semaphore 예시 (동시 실행 제한)
semaphore = Semaphore(2)  # 최대 2개 동시 실행

async def limited_worker(name):
    async with semaphore:
        print(f"{name} 시작")
        await asyncio.sleep(1)
        print(f"{name} 완료")

async def main():
    # Queue 예시
    queue = Queue()
    await asyncio.gather(
        producer(queue),
        consumer(queue)
    )
    
    # Lock 예시
    await asyncio.gather(*[increment() for _ in range(10)])
    print(f"최종 카운터: {counter}")
    
    # Semaphore 예시
    workers = [limited_worker(f"Worker{i}") for i in range(5)]
    await asyncio.gather(*workers)
```

8. 정리: 
```text 
파이썬의 asyncio는 코루틴을 실행하고 스케줄링하기 위한 런타임 도구입니다.
async def는 코루틴을 정의하는 문법이고, asyncio.run()은 그것을 실행하는 함수입니다.
asyncio.gather()로 여러 작업을 병렬 실행하고, create_task()는 백그라운드로 태스크를 미리 등록할 때 사용합니다.
또, Queue, Lock, Semaphore 같은 동기화 도구도 함께 제공돼서 비동기 환경에서도 안정적인 자원 관리가 가능합니다.
```


#### 1.2.2 이벤트 루프와 작업 제어
- 이벤트 루프라는 개념은? 
    - 비동기 시스템의 핵심 구조로, 이벤트가 발생하면 등록된 콜백/코루틴을 실행해주는 스케줄러 역할을 한다.
    - 파이썬에서는 이 "이벤트 루프"라는 개념을 asyncio가 구현한 것.

#### 1.2.3 asyncio.create_task() vs asyncio.gather() 

|항목|asyncio.create_task()|asyncio.gather()|    
|----------|--------------------|--------------------|
|무엇을 함?|코루틴을 Task로 등록해서 즉시 실행|여러 코루틴/태스크를 동시에 실행하고 결과를 모음|    
|리턴값|asyncio.Task 객체 (즉시 실행됨)|최종 결과 (코루틴이 끝날 때까지 await 필요)|    
|예시 비유|“예약만 먼저 해두고 나중에 결과 받기”|“한꺼번에 실행하고 결과도 한꺼번에 받기”|    
|결과 수집|나중에 await task 해서 받음|await asyncio.gather(...) 한 줄로 결과 받음|    
|사용 위치|비동기 작업을 분리해서 실행하고 싶을 때|비동기 작업을 묶어서 한꺼번에 실행할 때|

- create_task()만 사용해서 작업을 분리해서 등록하고, 이후 따로 await하는 방법으로 유연하게 비동기 처리할 수도 있고, gather()로 코루틴을 병렬로 실행하고 결과도 한번에 받는 처리도 가능하다. 또는 둘이 같이 쓰는 것도 가능하다. 

```python
async def main():
    task1 = asyncio.create_task(fetch_data(1))
    task2 = asyncio.create_task(fetch_data(2))
    task3 = asyncio.create_task(fetch_data(3))

    # 일부 태스크만 모아서 기다리기
    results = await asyncio.gather(task1, task2)
    print("task1, task2 결과:", results)

    # task3는 나중에 따로 기다림
    result3 = await task3
    print("task3 결과:", result3)
```


### 1.3 블로킹(Blocking) vs 논블로킹(Non-blocking)의 차이는?
- 블로킹은 "작업이 끝날 때까지 기다림", 논블로킹은 "기다리지 않고 바로 다음 작업으로 넘어감"을 의미한다. 
- I/O 작업(파일 읽기, 네트워크 요청, DB 쿼리 등), 멀티스레딩/멀티프로세싱, 이벤트 루프 기반 비동기 처리 (async/await)과 관련하여 등장하는 개념이며, 
이런 작업이 "기다릴지 말지"를 선택해야 할 때 사용된다.
- 항상 비동기 처리로 논블로킹으로 만들면 좋은거 아닌가? 
    - 항상 그렇다고 할 수 없음. 왜냐면 예를 들어 10000개의 비동기 작업이 있다고 가정하면, 그걸 스케줄링하고 관리하는 것도 CPU 자원과 메모리를 먹기 떄문. 
    - 또한 async/await, 이벤트 루프, 콜백 지옥, 타임아웃, 취소, 예외 처리 등 복잡성이 증가한다. 코드를 접하는 사람은 이해하기 어렵게 된다.
    - 또한, CPU 바운드 작업(예: 이미지 처리, 숫자 계싼, 압축 알고리즘 등)은 논블로킹이어도 실제로는 블로킹된다 -> 오히려 이벤트 루프가 멈추는 이슈. 
    이런 경우는 스레드나 프로세스 풀로 멀티 스레드/멀티 프로세스로 처리가 더 적합.
    - 결론: 논블로킹은 "무조건 좋은 것"이 아니라, "I/O" 바운드 상황에 효율적인 도구이다

---

<details>
<summary>cf. reference</summary>

- 
</details> 


