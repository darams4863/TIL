---
title: "Python 예외 처리와 컨텍스트 관리자"
date: 2025-08-22
categories:
  - python
tags:
  - exception-handling
  - context-manager
  - resource-management
  - error-handling
  - with-statement
---

# Python 예외 처리와 컨텍스트 관리자

## 1. 예외 처리 (Exception Handling)

### 1.1 기본 구조
- Python의 예외 처리는 `try-except-else-finally` 블록으로 구성된다.

```python
try:
    # 예외 발생 가능 코드
    result = risky_operation()
except ValueError:
    # ValueError 예외 처리
    print("잘못된 값이 입력되었습니다")
except KeyError as e:
    # KeyError 예외 처리 (예외 객체를 e로 받음)
    print(f"키를 찾을 수 없습니다: {e}")
else:
    # 예외가 발생하지 않은 경우 실행
    print(f"성공적으로 완료: {result}")
finally:
    # 항상 실행 (리소스 정리 등)
    cleanup_resources()
```


## 2. 커스텀 예외 클래스

### 2.1 왜 필요한가?

- **도메인/비즈니스 로직 오류 구분**: 일반적인 시스템 오류와 구분
- **서비스 계층에서 의미있는 예외 전달**: 클라이언트에게 명확한 오류 정보 제공

### 2.2 커스텀 예외 구현
- `exception.py`

```python
from typing import Any, Dict


class BaseCustomException(Exception):
    """기본 커스텀 예외 클래스 (JSend 스타일)"""
    
    status: str = "fail"

    def __init__(self, code: str, message: str, details: Dict[str, Any] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message} (코드: {self.code})"


# 세부 예외 유형 정의
class InvalidUserInputError(BaseCustomException):
    """사용자 입력 오류"""
    pass

class DatabaseConnectionError(BaseCustomException):
    """DB 연결 오류"""
    pass

class ExternalApiError(BaseCustomException):
    """외부 API 호출 실패"""
    pass

class BusinessLogicError(BaseCustomException):
    """비즈니스 로직 오류"""
    pass
```

- `error_code.py`

```python
class ErrorCode:
    class User:
        INVALID_EMAIL = ("U1001", "유효하지 않은 이메일입니다")
        INVALID_AGE = ("U1002", "나이는 0 이상이어야 합니다")

    class DB:
        CONNECTION_FAILED = ("D1001", "데이터베이스 연결에 실패했습니다")

    class API:
        CALL_FAILED = ("A1001", "외부 API 호출에 실패했습니다")
```

- 사용 예시:

```python
from exception import InvalidUserInputError
from error_code import ErrorCode


def validate_user_input(user_data: dict):
    """사용자 입력 검증"""
    if not user_data.get('email'):
        raise InvalidUserInputError(
            code=ErrorCode.User.INVALID_EMAIL[0],
            message=ErrorCode.User.INVALID_EMAIL[1],
            details={"field": "email", "value": user_data.get("email")}
        )
    
    if not isinstance(user_data.get('age'), int) or user_data['age'] < 0:
        raise InvalidUserInputError(
            code=ErrorCode.User.INVALID_AGE[0],
            message=ErrorCode.User.INVALID_AGE[1],
            details={"field": "age", "value": user_data.get("age")}
        )

# 또는 FastAPI 예외 핸들러 연동시 
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from exception import BaseCustomException

app = FastAPI()

@app.exception_handler(BaseCustomException)
async def custom_exception_handler(request: Request, exc: BaseCustomException):
    return JSONResponse(
        status_code=400,
        content={
            "status": "fail",
            "code": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )

# cf. @app.exception_handler는 FastAPI에서 특정 예외가 발생했을 때 실행할 핸들러(처리 함수)를 등록하는 데 사용하는 데코레이터로, 처리하고자 하는 예외 클래스에 따라 실행된 함수를 지정한다. 
# 단, @app.exception_handler는 라우터 레벨 / 비즈니스 로직 레벨의 try-except를 통과하지 못하고 "FastAPI 레벨까지 bubble-up된 예외를 잡아서 처리하는 최종 예외 핸들러"이란 점 알고가기!
```

## 3. 컨텍스트 관리자 (with 구문)
- 컨텍스트 관리자는 with 문 안에서 **리소스를 열고 자동으로 정리(cleanup)**하는 구조를 의미한다. 
- 컨텍스트 관리자는 두 개의 메서드로 구성된다:  
    - `__enter__()`와 `__exit__()` 메서드를 사용하여 리소스를 자동으로 관리
- 컨텍스트 관리자는 내부적으로 `__exit__()` 메서드를 통해, 예외 발생 여부를 감지하고, 예외 발생 시 처리하거나, 무시하거나, 재전파할 수 있다.
    - 즉, try/except/finally 구조를 with 문으로 감싸는 것과 같은 효과를 갖는다.
    - 비교: try/finally vs. with (동일한 결과)

    ```python
    # 1. 일반적인 예외 처리 구조
    f = open("test.txt")
    try:
        data = f.read()
    finally:
        f.close()  # 항상 실행됨

    # 2. 컨텍스트 관리자를 사용한 버전
    with open("test.txt") as f:
        data = f.read()
    # 여기서도 f.close()는 예외가 나도 실행됨

    # 3. with 문은 내부적으로 이렇게 동작
    # 내부 구조:
    f = open("test.txt")
    f.__enter__()
    try:
        data = f.read()
    finally:
        f.__exit__(*sys.exc_info())  # 예외 발생 여부 확인해서 처리
    ``` 

- 예외 처리를 이미 하고 있어도 `@asynccontextmanager/@contextmanager` 컨텍스트 매니저를 사용하면 with 또는 async with 블록의 진입/종료 시점을 자동으로 제어하면서, 자원의 획득과 해제를 명시적이고 안전하게 관리할 수 있기때문에 사용한다:
    - `__exit__()`로 자동으로 자원을 정리 
    - try: yield conn → except:, finally:처럼 긴 코드 대신, async with transaction() 한 줄이면 깔끔하게 트랜잭션 흐름이 보인다 -> 코드 가독성과 유지 보수 
    - 사람이 매번 .rollback() / .release() 등을 빠뜨릴 수 있는데, 컨텍스트 매니저는 블록을 빠져나갈 때 반드시 cleanup 동작을 수행 -> 실수 방지 

    ```python
    # (기존 방식)
    conn = await pool.acquire()
    tr = conn.transaction()
    await tr.start()
    try:
        # 작업
        await tr.commit()
    except:
        await tr.rollback()
    finally:
        await conn.release()

    # (컨텍스트 매니저 사용 시)
    async with transaction() as conn:
        # 작업 (자동 commit or rollback + conn 반환)
    ```

### 컨텍스트 관리자를 사용하는 이유 요약 
|이유|설명|
|-----------------|---------------------------------------------------|
|자원 자동 정리|with 또는 async with 블록이 끝날 때, rollback, release 등 자원 정리 로직이 자동 실행됨
|예외 발생 시 안전|예외가 발생해도 finally 없이 정리 코드가 무조건 실행되므로 누락 위험 없음|
|코드 간결화|try/except/finally 없이도 트랜잭션, 파일, DB 연결 등의 흐름을 짧고 명확하게 표현 가능
|에러에 강한 구조화된 처리|예외가 나더라도 자원 누수 없이 종료되도록 강제됨|
|비동기 환경 지원|@asynccontextmanager로 async with 사용 가능 → FastAPI, asyncpg 등에서 자주 활용됨|


### 컨텍스트 매니저 사용 하는 방법 
- 동기 컨텍스트 매니저 (`@contextmanager`)
- 비동기 컨텍스트 매니저 (`@asynccontextmanager`)
- `from contextlib import contextmanager, asynccontextmanager`로 임포트 

### 실무에서 자주 쓰는 컨텍스트 매니저
- 이때 컨텍스트 매니저는 with 구문을 통해 자원의 획득과 해제를 자동으로 처리할 수 있게 도와준다고 했는데, 구현하는 곳에선느 try ~ finally로 직접 구현해주고, 사용할 때 with 구문을 이용하면 알아서 `__enter__(), __exit__()` 메서드를 활용해서 "자원 해제"가 되는 구조로 사용할 수 있는 것이다.

- 실무 예시: 락(lock) 처리 (동기)

```python
from contextlib import contextmanager
import threading

lock = threading.Lock()

@contextmanager
def locked():
    lock.acquire()
    try:
        yield
    finally:
        lock.release()

# 사용 예시
with locked():
    do_something_critical()
```

- 실무 예시: DB 트랜젝션 처리 (비동기)

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def db_transaction(session):
    await session.begin()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

# 사용 예시
async with db_transaction(get_session()) as session:
    await session.execute(...)
```


---

<details>
<summary>참고 자료</summary>

- 

</details> 



