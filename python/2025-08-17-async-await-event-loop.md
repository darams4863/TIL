---
title: "파이썬의 동기 vs 비동기"
date: 2025-08-17
categories:
  - python
tags:
  - python
  - async
  - asyncio
  - backend
  - performance
---

# 파이썬의 동기 vs 비동기

## 1. async / await

### 기본 개념
- `async def`: 비동기 함수를 정의하는 키워드
- `await`: 비동기 함수의 결과를 기다리는 키워드
- 코루틴(coroutine): `async def`로 정의된 함수

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
```

### 면접 포인트
- `async def`는 함수를 코루틴 객체로 만듦
- `await`는 코루틴이 완료될 때까지 기다림
- `await`는 `async def` 함수 내에서만 사용 가능

## 2. asyncio

### 이벤트 루프
```python
import asyncio

async def task1():
    await asyncio.sleep(1)
    print("Task 1 완료")

async def task2():
    await asyncio.sleep(1)
    print("Task 2 완료")

async def main():
    # 동시 실행
    await asyncio.gather(task1(), task2())
    
    # 또는
    task1_obj = asyncio.create_task(task1())
    task2_obj = asyncio.create_task(task2())
    await task1_obj
    await task2_obj

asyncio.run(main())
```

### 면접 포인트
- `asyncio.run()`: 이벤트 루프를 생성하고 관리
- `asyncio.create_task()`: 코루틴을 Task로 래핑하여 스케줄링
- `asyncio.gather()`: 여러 코루틴을 동시에 실행

## 3. 블로킹 / 논블로킹

### 블로킹 vs 논블로킹
```python
# 블로킹 (동기)
import time
import requests

def blocking_function():
    start = time.time()
    response = requests.get("https://api.example.com/data")  # 블로킹
    print(f"소요시간: {time.time() - start}초")
    return response.json()

# 논블로킹 (비동기)
import aiohttp
import asyncio

async def nonblocking_function():
    start = time.time()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com/data") as response:
            data = await response.json()
    print(f"소요시간: {time.time() - start}초")
    return data
```

### 면접 포인트
- **블로킹**: 함수가 완료될 때까지 다른 작업을 할 수 없음
- **논블로킹**: 함수가 완료되기를 기다리지 않고 다른 작업 수행 가능
- I/O 바운드 작업에서 비동기가 효과적

## 4. aiohttp

### 비동기 HTTP 클라이언트
```python
import aiohttp
import asyncio

async def fetch_multiple_urls():
    urls = [
        "https://api.example.com/1",
        "https://api.example.com/2",
        "https://api.example.com/3"
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.create_task(fetch_url(session, url))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.json()
```

### 면접 포인트
- `aiohttp.ClientSession`: 연결 풀링과 재사용
- `asyncio.create_task()`: 비동기 작업을 동시에 실행
- 동기 `requests`와 달리 비동기로 여러 요청을 병렬 처리

## 5. FastAPI에서 비동기 처리

### 기본 구조
```python
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/sync")
def sync_endpoint():
    # 동기 처리 - 블로킹
    time.sleep(1)
    return {"message": "동기 응답"}

@app.get("/async")
async def async_endpoint():
    # 비동기 처리 - 논블로킹
    await asyncio.sleep(1)
    return {"message": "비동기 응답"}

@app.get("/async-db")
async def async_db_endpoint():
    # 비동기 DB 쿼리
    result = await database.fetch("SELECT * FROM users")
    return {"users": result}
```

### 면접 포인트
- FastAPI는 기본적으로 ASGI 기반으로 비동기 지원
- 동기 함수는 별도 스레드 풀에서 실행
- 비동기 함수는 이벤트 루프에서 직접 실행

## 6. 동기/비동기 DB 예시

### PostgreSQL 연결 비교

#### 동기 (psycopg2)
```python
import psycopg2
from psycopg2.pool import SimpleConnectionPool

# 연결 풀 생성
pool = SimpleConnectionPool(1, 20, 
    host="localhost",
    database="testdb",
    user="user",
    password="password"
)

def sync_query():
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users")
            return cur.fetchall()
    finally:
        pool.putconn(conn)
```

#### 비동기 (asyncpg)
```python
import asyncpg
import asyncio

async def create_pool():
    return await asyncpg.create_pool(
        host="localhost",
        database="testdb",
        user="user",
        password="password",
        min_size=5,
        max_size=20
    )

async def async_query(pool):
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM users")

# 사용
async def main():
    pool = await create_pool()
    users = await async_query(pool)
    await pool.close()
```

#### databases 라이브러리
```python
from databases import Database

database = Database("postgresql://user:password@localhost/testdb")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/users")
async def get_users():
    query = "SELECT * FROM users"
    return await database.fetch_all(query)
```

### 면접 포인트
- **psycopg2**: 동기, 스레드 안전, 연결 풀링 지원
- **asyncpg**: 비동기, 높은 성능, 네이티브 C 구현
- **databases**: SQLAlchemy와 유사한 인터페이스, 여러 DB 지원

## 7. 동시성 (웹소켓, 채팅)

### 웹소켓 예시
```python
from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
import json

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await manager.broadcast(f"Client {client_id}: {message['message']}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client {client_id} left the chat")
```

### 면접 포인트
- 웹소켓은 지속적인 연결을 유지하여 실시간 통신
- 비동기로 여러 클라이언트 연결을 동시에 처리
- 연결 관리와 메시지 브로드캐스팅이 핵심

## 8. 외부 API/DB 연결에서의 대기 시간

### 동기 vs 비동기 처리 비교

#### 동기 처리 (순차 실행)
```python
import time
import requests

def sync_fetch_all():
    start = time.time()
    
    # 순차적으로 실행 - 총 3초 소요
    data1 = requests.get("https://api1.com").json()  # 1초
    data2 = requests.get("https://api2.com").json()  # 1초  
    data3 = requests.get("https://api3.com").json()  # 1초
    
    print(f"총 소요시간: {time.time() - start}초")
    return [data1, data2, data3]
```

#### 비동기 처리 (병렬 실행)
```python
import aiohttp
import asyncio

async def async_fetch_all():
    start = time.time()
    
    async with aiohttp.ClientSession() as session:
        # 동시에 실행 - 총 1초 소요
        tasks = [
            fetch_url(session, "https://api1.com"),
            fetch_url(session, "https://api2.com"),
            fetch_url(session, "https://api3.com")
        ]
        results = await asyncio.gather(*tasks)
    
    print(f"총 소요시간: {time.time() - start}초")
    return results

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.json()
```

### 면접 포인트
- **동기**: N개 API 호출 시 N × (각 API 응답시간) 소요
- **비동기**: N개 API 호출 시 max(각 API 응답시간) 소요
- I/O 바운드 작업에서 비동기가 압도적으로 효율적

## 9. 이벤트 루프 내부 동작

### 이벤트 루프 구조
```python
import asyncio

async def cpu_bound_task():
    # CPU 집약적 작업
    result = sum(i * i for i in range(10**6))
    return result

async def io_bound_task():
    # I/O 바운드 작업
    await asyncio.sleep(1)
    return "I/O 완료"

async def main():
    # 이벤트 루프가 작업을 스케줄링
    task1 = asyncio.create_task(cpu_bound_task())
    task2 = asyncio.create_task(io_bound_task())
    
    # 모든 작업 완료 대기
    results = await asyncio.gather(task1, task2)
    return results
```

### 면접 포인트
- **이벤트 루프**: 단일 스레드에서 여러 코루틴을 스케줄링
- **작업 큐**: 실행 대기 중인 코루틴들을 관리
- **I/O 완료 큐**: I/O 작업이 완료된 코루틴들을 관리
- **CPU 바운드 작업**: 이벤트 루프를 블로킹하므로 주의 필요

## 10. 동시성 컨트롤

### await, Task, Future의 차이

#### await
```python
async def simple_await():
    result = await some_coroutine()  # 코루틴 완료까지 대기
    return result
```

#### Task
```python
async def task_example():
    # 코루틴을 Task로 래핑하여 스케줄링
    task = asyncio.create_task(some_coroutine())
    
    # 다른 작업 수행 가능
    other_result = await other_coroutine()
    
    # Task 완료 대기
    result = await task
    return result
```

#### Future
```python
async def future_example():
    # Future 객체 생성
    future = asyncio.Future()
    
    # Future에 결과 설정
    future.set_result("완료!")
    
    # Future 완료 대기
    result = await future
    return result
```

### 비동기 동기화 기법

#### asyncio.Queue
```python
import asyncio

async def producer(queue):
    for i in range(5):
        await queue.put(f"item {i}")
        await asyncio.sleep(1)
    await queue.put(None)  # 종료 신호

async def consumer(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"처리: {item}")
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    
    # 생산자와 소비자 동시 실행
    await asyncio.gather(
        producer(queue),
        consumer(queue)
    )
```

#### asyncio.Lock
```python
import asyncio

class SharedResource:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.data = []

    async def add_data(self, item):
        async with self.lock:  # 락 획득
            self.data.append(item)
            await asyncio.sleep(0.1)  # 임계 구역 보호
        # 락 자동 해제

async def worker(resource, name):
    for i in range(3):
        await resource.add_data(f"{name}-{i}")
        await asyncio.sleep(0.1)
```

#### asyncio.Semaphore
```python
import asyncio

# 최대 3개 동시 실행
semaphore = asyncio.Semaphore(3)

async def limited_worker(name):
    async with semaphore:
        print(f"{name} 시작")
        await asyncio.sleep(2)  # 작업 시뮬레이션
        print(f"{name} 완료")

async def main():
    workers = [limited_worker(f"Worker-{i}") for i in range(10)]
    await asyncio.gather(*workers)
```

### Celery vs Dramatiq vs asyncio.Queue

#### asyncio.Queue (인메모리)
```python
# 단일 프로세스 내에서만 사용
queue = asyncio.Queue()
```

#### Celery (분산 작업 큐)
```python
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def long_running_task(x, y):
    return x + y

# 비동기로 작업 제출
result = long_running_task.delay(4, 4)
```

#### Dramatiq (Redis 기반)
```python
import dramatiq

@dramatiq.actor
def long_running_task(x, y):
    return x + y

# 작업 제출
long_running_task.send(4, 4)
```

### Thread vs AsyncIO 비교

```python
import threading
import asyncio
import time

# 스레드 기반
def thread_worker():
    time.sleep(1)
    print("스레드 작업 완료")

def run_with_threads():
    threads = []
    for i in range(5):
        t = threading.Thread(target=thread_worker)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

# AsyncIO 기반
async def async_worker():
    await asyncio.sleep(1)
    print("비동기 작업 완료")

async def run_with_asyncio():
    tasks = [async_worker() for _ in range(5)]
    await asyncio.gather(*tasks)

# 실행 시간 비교
start = time.time()
run_with_threads()
print(f"스레드: {time.time() - start}초")

start = time.time()
asyncio.run(run_with_asyncio())
print(f"AsyncIO: {time.time() - start}초")
```

### 면접 포인트
- **Thread**: OS 레벨 스케줄링, GIL 영향, 컨텍스트 스위칭 오버헤드
- **AsyncIO**: 사용자 레벨 스케줄링, 단일 스레드, I/O 바운드에 최적
- **Celery**: 분산 환경, 백그라운드 작업, 워커 프로세스 관리

## 11. 비동기 테스트 (pytest-asyncio)

### 테스트 예시
```python
import pytest
import asyncio
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/async")
        assert response.status_code == 200
        assert response.json()["message"] == "비동기 응답"

@pytest.mark.asyncio
async def test_database_connection():
    # DB 연결 테스트
    pool = await create_test_pool()
    try:
        result = await pool.fetch("SELECT 1")
        assert result[0][0] == 1
    finally:
        await pool.close()

# 모킹 예시
@pytest.mark.asyncio
async def test_with_mock(monkeypatch):
    async def mock_fetch():
        return {"mocked": "data"}
    
    monkeypatch.setattr("module.fetch_data", mock_fetch)
    result = await some_function()
    assert result["mocked"] == "data"
```

### 면접 포인트
- `@pytest.mark.asyncio`: 비동기 테스트 함수 표시
- `AsyncClient`: 비동기 HTTP 클라이언트로 테스트
- 모킹과 의존성 주입으로 격리된 테스트 환경 구성

## 12. Uvicorn, Gunicorn, ASGI 이해

### WSGI vs ASGI

#### WSGI (동기)
```python
# WSGI 애플리케이션
def wsgi_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    return [b'Hello World']

# Gunicorn으로 실행
# gunicorn wsgi_app:app
```

#### ASGI (비동기)
```python
# ASGI 애플리케이션
async def asgi_app(scope, receive, send):
    if scope['type'] == 'http':
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [(b'content-type', b'text/plain')]
        })
        await send({
            'type': 'http.response.body',
            'body': b'Hello World'
        })

# Uvicorn으로 실행
# uvicorn asgi_app:app
```

### 서버 설정

#### Uvicorn (ASGI 전용)
```bash
# 개발 서버
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Gunicorn + Uvicorn (ASGI)
```bash
# Gunicorn으로 프로세스 관리, Uvicorn으로 ASGI 처리
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 면접 포인트
- **WSGI**: 동기만 지원, Flask, Django 전통 방식
- **ASGI**: 동기/비동기 모두 지원, FastAPI, Starlette
- **Uvicorn**: ASGI 전용, 개발/프로덕션 모두 지원
- **Gunicorn**: 프로세스 관리, 워커 프로세스 생성

## 13. FastAPI + async 설계 베스트 프랙티스

### 구조적 설계
```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

app = FastAPI()

# 의존성 주입
async def get_db():
    async with async_session() as session:
        yield session

# 서비스 레이어
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_users(self) -> List[User]:
        result = await self.db.execute(select(User))
        return result.scalars().all()

# API 레이어
@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.get_users()

# 백그라운드 작업
@app.post("/users")
async def create_user(user: UserCreate, background_tasks: BackgroundTasks):
    # 즉시 응답
    user_id = await save_user(user)
    
    # 백그라운드에서 처리
    background_tasks.add_task(send_welcome_email, user_id)
    
    return {"id": user_id, "status": "created"}
```

### 에러 처리
```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc), "error_code": exc.error_code}
    )

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### 성능 최적화
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

# 미들웨어 추가
app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 캐싱
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf8")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

@app.get("/users")
@cache(expire=60)  # 60초 캐시
async def get_users():
    return await fetch_users_from_db()
```

### 면접 포인트
- **의존성 주입**: 테스트 용이성과 코드 재사용성
- **서비스 레이어**: 비즈니스 로직과 API 로직 분리
- **백그라운드 작업**: 사용자 응답 지연 방지
- **에러 처리**: 일관된 에러 응답과 로깅
- **캐싱**: Redis를 활용한 성능 최적화

## 14. 실제 면접 질문과 답변

### Q1: 동기와 비동기의 차이점은?
**A**: 동기는 작업이 완료될 때까지 기다리는 방식이고, 비동기는 작업 완료를 기다리지 않고 다른 작업을 수행할 수 있는 방식입니다. I/O 바운드 작업에서는 비동기가 훨씬 효율적입니다.

### Q2: asyncio의 이벤트 루프는 어떻게 동작하나요?
**A**: 이벤트 루프는 단일 스레드에서 여러 코루틴을 스케줄링합니다. 작업 큐에서 실행 대기 중인 코루틴을 관리하고, I/O 완료 큐에서 완료된 작업을 처리합니다.

### Q3: Thread와 AsyncIO 중 언제 어떤 것을 사용하나요?
**A**: I/O 바운드 작업(네트워크, 파일, DB)에는 AsyncIO가, CPU 바운드 작업(복잡한 계산)에는 Thread가 적합합니다. AsyncIO는 단일 스레드에서 동작하므로 CPU 집약적 작업은 이벤트 루프를 블로킹할 수 있습니다.

### Q4: FastAPI에서 동기 함수를 사용하면 어떻게 되나요?
**A**: FastAPI는 동기 함수를 별도 스레드 풀에서 실행합니다. 하지만 I/O 바운드 작업이 많다면 비동기 함수를 사용하는 것이 성능상 유리합니다.

### Q5: 비동기 코드의 디버깅은 어떻게 하나요?
**A**: `pytest-asyncio`를 사용하여 비동기 테스트를 작성하고, 로깅과 모니터링 도구를 활용합니다. 또한 `asyncio.create_task()`로 생성된 Task의 상태를 추적할 수 있습니다.

---

<details>
<summary>cf. reference</summary>

- [Python asyncio 공식 문서](https://docs.python.org/3/library/asyncio.html)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [asyncpg 문서](https://magicstack.github.io/asyncpg/)
- [aiohttp 문서](https://docs.aiohttp.org/)
- [pytest-asyncio 문서](https://pytest-asyncio.readthedocs.io/)

</details> 


