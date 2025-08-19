---
title: "Python 예외 처리와 컨텍스트 관리"
date: 2025-08-19
categories:
  - python
tags:
  - exception-handling
  - context-manager
  - logging
  - resource-management
  - error-handling
  - with-statement
---

# Python 예외 처리와 컨텍스트 관리

## 📋 목차
1. **예외 처리 (Exception Handling)** - try-except-else-finally 구조
2. **커스텀 예외 클래스** - 도메인별 예외 정의
3. **컨텍스트 관리자 (with 구문)** - 리소스 자동 관리
4. **contextlib 모듈** - 실무형 컨텍스트 매니저
5. **실무 사용 사례** - 예외 처리와 컨텍스트 관리 조합
6. **면접 질문 예시** - 핵심 포인트와 답변

---

## 1. 예외 처리 (Exception Handling)

### 1.1 기본 구조

Python의 예외 처리는 `try-except-else-finally` 블록으로 구성됩니다.

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

### 1.2 실무 필수 포인트

| 항목 | 설명 | 예시 |
|------|------|------|
| **구체적인 예외 클래스 사용** | ❌ `except Exception:` 사용 금지<br>✅ `except ValueError:` 구체적 예외 처리 | `except (ValueError, TypeError):` |
| **finally 사용 이유** | 파일 닫기, DB 커넥션 종료 등 리소스 정리 목적 | `finally: file.close()` |
| **raise 키워드** | 예외 재발생 / 커스텀 예외 전달 시 사용 | `raise CustomError("상세 메시지")` |
| **except as e 활용** | 로깅 시 e에 예외 메시지 저장 가능 | `logger.error(f"에러 발생: {e}")` |

### 1.3 실무 예시

```python
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def process_user_data(user_id: int, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """사용자 데이터 처리 함수"""
    try:
        # 사용자 ID 검증
        if user_id <= 0:
            raise ValueError(f"잘못된 사용자 ID: {user_id}")
        
        # 필수 필드 검증
        required_fields = ['name', 'email']
        for field in required_fields:
            if field not in user_data:
                raise KeyError(f"필수 필드 누락: {field}")
        
        # 데이터 처리 로직
        processed_data = transform_user_data(user_data)
        logger.info(f"사용자 {user_id} 데이터 처리 완료")
        
        return processed_data
        
    except ValueError as e:
        logger.error(f"사용자 ID 검증 실패: {e}")
        raise  # 예외 다시 던지기
        
    except KeyError as e:
        logger.error(f"데이터 필드 누락: {e}")
        raise
        
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        raise CustomUserProcessingError(f"사용자 데이터 처리 중 오류: {e}")
        
    finally:
        # 리소스 정리
        cleanup_temp_data()
        logger.debug("임시 데이터 정리 완료")

def transform_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """사용자 데이터 변환"""
    # 실제 변환 로직
    return data

def cleanup_temp_data():
    """임시 데이터 정리"""
    pass
```

## 2. 커스텀 예외 클래스

### 2.1 왜 필요한가?

- **도메인/비즈니스 로직 오류 구분**: 일반적인 시스템 오류와 구분
- **서비스 계층에서 의미있는 예외 전달**: 클라이언트에게 명확한 오류 정보 제공

### 2.2 커스텀 예외 구현

```python
class BaseCustomException(Exception):
    """기본 커스텀 예외 클래스"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        return f"{self.__class__.__name__}: {self.message} (코드: {self.error_code})"

class InvalidUserInputError(BaseCustomException):
    """사용자 입력 오류"""
    pass

class DatabaseConnectionError(BaseCustomException):
    """데이터베이스 연결 오류"""
    pass

class ExternalApiError(BaseCustomException):
    """외부 API 호출 오류"""
    pass

class BusinessLogicError(BaseCustomException):
    """비즈니스 로직 오류"""
    pass

# 사용 예시
def validate_user_input(user_data: Dict[str, Any]) -> None:
    """사용자 입력 검증"""
    if not user_data.get('email'):
        raise InvalidUserInputError(
            message="이메일은 필수 입력 항목입니다",
            error_code="EMAIL_REQUIRED",
            details={"field": "email", "value": user_data.get('email')}
        )
    
    if not user_data.get('age') or user_data['age'] < 0:
        raise InvalidUserInputError(
            message="나이는 0 이상이어야 합니다",
            error_code="INVALID_AGE",
            details={"field": "age", "value": user_data.get('age')}
        )
```

## 3. 컨텍스트 관리자 (with 구문)

### 3.1 기본 구조

컨텍스트 관리자는 `__enter__()`와 `__exit__()` 메서드를 사용하여 리소스를 자동으로 관리합니다.

```python
# 기본 사용법
with open("file.txt") as f:
    data = f.read()

# 장점:
# - 파일 자동 닫힘 (close 자동 호출)
# - __enter__() / __exit__() 메서드 사용
# - 예외 발생 시에도 안전한 리소스 정리
```

### 3.2 직접 구현 예시

```python
class DatabaseConnection:
    """데이터베이스 연결 컨텍스트 매니저"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
    
    def __enter__(self):
        """컨텍스트 진입 시 실행"""
        print(f"데이터베이스 연결 시도: {self.connection_string}")
        self.connection = self._create_connection()
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 종료 시 실행"""
        if self.connection:
            self.connection.close()
            print("데이터베이스 연결 종료")
        
        # 예외가 발생한 경우 로깅
        if exc_type:
            print(f"데이터베이스 작업 중 오류 발생: {exc_val}")
            # False를 반환하면 예외를 다시 발생시킴
            # True를 반환하면 예외를 억제함
            return False
        
        return True
    
    def _create_connection(self):
        """실제 연결 생성 로직"""
        # 시뮬레이션
        return type('Connection', (), {'close': lambda: None})()

# 사용 예시
def process_database_operation():
    """데이터베이스 작업 처리"""
    try:
        with DatabaseConnection("postgresql://localhost:5432/mydb") as conn:
            # 데이터베이스 작업 수행
            result = conn.execute("SELECT * FROM users")
            print("데이터베이스 작업 완료")
            return result
    except Exception as e:
        print(f"데이터베이스 작업 실패: {e}")
        raise

# 실행
process_database_operation()
```

## 4. contextlib 모듈

### 4.1 실무에서 자주 쓰는 컨텍스트 매니저

`@contextmanager` 데코레이터를 사용하면 함수 기반으로 컨텍스트 매니저를 더 간단하게 구현할 수 있습니다.

```python
from contextlib import contextmanager
import time
import logging

logger = logging.getLogger(__name__)

@contextmanager
def connect_to_database(connection_string: str):
    """데이터베이스 연결 컨텍스트 매니저"""
    db = None
    try:
        logger.info(f"데이터베이스 연결 시도: {connection_string}")
        db = create_database_connection(connection_string)
        yield db  # 컨텍스트 내부에서 사용할 객체 반환
    except Exception as e:
        logger.error(f"데이터베이스 연결 실패: {e}")
        raise
    finally:
        if db:
            db.close()
            logger.info("데이터베이스 연결 종료")

@contextmanager
def performance_monitor(operation_name: str):
    """성능 모니터링 컨텍스트 매니저"""
    start_time = time.time()
    try:
        yield
    finally:
        execution_time = time.time() - start_time
        logger.info(f"{operation_name} 실행 시간: {execution_time:.3f}초")

@contextmanager
def error_handler(operation_name: str, fallback_value=None):
    """에러 처리 컨텍스트 매니저"""
    try:
        yield
    except Exception as e:
        logger.error(f"{operation_name} 실행 중 오류: {e}")
        if fallback_value is not None:
            logger.info(f"폴백 값 사용: {fallback_value}")
            return fallback_value
        raise

# 사용 예시
def process_user_data_with_context():
    """컨텍스트 매니저를 활용한 사용자 데이터 처리"""
    with performance_monitor("사용자 데이터 처리"):
        with error_handler("데이터베이스 조회", fallback_value=[]):
            with connect_to_database("postgresql://localhost:5432/mydb") as db:
                users = db.query("SELECT * FROM users")
                return users

# 실제 사용
try:
    users = process_user_data_with_context()
    print(f"처리된 사용자 수: {len(users)}")
except Exception as e:
    print(f"사용자 데이터 처리 실패: {e}")
```

## 5. 실무 사용 사례

### 5.1 예외 처리와 컨텍스트 관리 조합

실무에서는 예외 처리와 컨텍스트 관리를 조합하여 안전하고 효율적인 코드를 작성합니다.

```python
import redis
import requests
from contextlib import contextmanager
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class RedisLockContext:
    """Redis 분산 락 컨텍스트 매니저"""
    
    def __init__(self, redis_client: redis.Redis, lock_key: str, timeout: int = 10):
        self.redis_client = redis_client
        self.lock_key = lock_key
        self.timeout = timeout
        self.lock_acquired = False
    
    def __enter__(self):
        """락 획득 시도"""
        self.lock_acquired = self.redis_client.set(
            self.lock_key, 
            "locked", 
            ex=self.timeout, 
            nx=True
        )
        if not self.lock_acquired:
            raise RuntimeError(f"락 획득 실패: {self.lock_key}")
        logger.info(f"락 획득 성공: {self.lock_key}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """락 해제"""
        if self.lock_acquired:
            self.redis_client.delete(self.lock_key)
            logger.info(f"락 해제 완료: {self.lock_key}")

@contextmanager
def api_request_with_retry(
    url: str, 
    max_retries: int = 3, 
    retry_delay: float = 1.0
):
    """재시도 로직이 포함된 API 요청 컨텍스트"""
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            yield response
            return
        except requests.RequestException as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.warning(f"API 요청 실패 (시도 {attempt + 1}/{max_retries}): {e}")
                time.sleep(retry_delay * (2 ** attempt))  # 지수 백오프
            else:
                logger.error(f"API 요청 최종 실패: {e}")
                raise last_exception

# 실무 활용 예시
def process_critical_operation(user_id: int, data: Dict[str, Any]) -> bool:
    """중요한 작업 처리 (락 + 재시도 + 로깅)"""
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    lock_key = f"user_operation:{user_id}"
    
    try:
        with RedisLockContext(redis_client, lock_key):
            with performance_monitor(f"사용자 {user_id} 작업 처리"):
                # 외부 API 호출 (재시도 로직 포함)
                with api_request_with_retry(f"https://api.example.com/users/{user_id}"):
                    # 실제 작업 수행
                    result = perform_user_operation(user_id, data)
                    logger.info(f"사용자 {user_id} 작업 완료: {result}")
                    return True
                    
    except Exception as e:
        logger.error(f"사용자 {user_id} 작업 실패: {e}")
        return False

def perform_user_operation(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """실제 사용자 작업 수행"""
    # 작업 로직 시뮬레이션
    return {"status": "success", "user_id": user_id, "processed_data": data}
```

### 5.2 고급 로깅과 예외 처리 통합

사용자가 제공한 로깅 시스템을 활용한 고급 예외 처리 예시:

```python
import logging
import time
from functools import wraps
from typing import Callable, Any

# 사용자 로깅 시스템 활용
def set_logger(pkg: str) -> logging.Logger:
    """로거 설정 (사용자 코드 기반)"""
    logger = logging.getLogger(pkg)
    if not logger.handlers:
        # 기본 핸들러 설정
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] | %(levelname)-8s | %(name)s >> %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger

def exception_logger(pkg: str):
    """예외 로깅 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = set_logger(pkg)
            try:
                logger.debug(f"함수 {func.__name__} 실행 시작")
                result = func(*args, **kwargs)
                logger.debug(f"함수 {func.__name__} 실행 완료")
                return result
            except Exception as e:
                logger.error(
                    f"함수 {func.__name__} 실행 중 예외 발생: {e}",
                    exc_info=True  # 스택 트레이스 포함
                )
                raise
        return wrapper
    return decorator

def async_exception_logger(pkg: str):
    """비동기 함수 예외 로깅 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger = set_logger(pkg)
            try:
                logger.debug(f"비동기 함수 {func.__name__} 실행 시작")
                result = await func(*args, **kwargs)
                logger.debug(f"비동기 함수 {func.__name__} 실행 완료")
                return result
            except Exception as e:
                logger.error(
                    f"비동기 함수 {func.__name__} 실행 중 예외 발생: {e}",
                    exc_info=True
                )
                raise
        return wrapper
    return decorator

# 사용 예시
@exception_logger("user_service")
def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """사용자 생성 함수"""
    if not user_data.get('email'):
        raise ValueError("이메일은 필수 입력 항목입니다")
    
    # 사용자 생성 로직
    user = {"id": 1, "email": user_data['email'], "created_at": time.time()}
    return user

@async_exception_logger("user_service")
async def update_user_async(user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """비동기 사용자 업데이트 함수"""
    await asyncio.sleep(0.1)  # 비동기 작업 시뮬레이션
    
    if user_id <= 0:
        raise ValueError("잘못된 사용자 ID")
    
    # 사용자 업데이트 로직
    updated_user = {"id": user_id, "updated_data": user_data, "updated_at": time.time()}
    return updated_user

# 테스트
if __name__ == "__main__":
    try:
        # 정상 케이스
        user = create_user({"email": "test@example.com"})
        print(f"생성된 사용자: {user}")
        
        # 예외 케이스
        create_user({})
    except Exception as e:
        print(f"사용자 생성 실패: {e}")
```

## 6. 면접 질문 예시

### 6.1 핵심 질문과 답변

#### Q1: "Python에서 예외 처리를 할 때 `except Exception:`을 사용하지 않는 이유는?"

**A1:**
```python
# ❌ 나쁜 예시
try:
    result = process_data()
except Exception:  # 너무 광범위한 예외 처리
    print("오류 발생")

# ✅ 좋은 예시
try:
    result = process_data()
except ValueError as e:
    logger.error(f"값 오류: {e}")
    # ValueError에 대한 구체적 처리
except KeyError as e:
    logger.error(f"키 오류: {e}")
    # KeyError에 대한 구체적 처리
except Exception as e:
    logger.error(f"예상치 못한 오류: {e}")
    # 마지막 안전장치로만 사용
```

**이유:**
- 구체적인 예외 처리가 불가능
- 디버깅이 어려움
- 예외의 원인을 파악하기 어려움

#### Q2: "컨텍스트 매니저의 `__enter__`와 `__exit__` 메서드가 어떻게 동작하나요?"

**A2:**
```python
class CustomContextManager:
    def __enter__(self):
        """with 블록 진입 시 실행"""
        print("컨텍스트 진입")
        return self  # with 블록에서 사용할 객체 반환
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """with 블록 종료 시 실행"""
        if exc_type:
            print(f"예외 발생: {exc_val}")
            return False  # 예외를 다시 발생시킴
        print("컨텍스트 종료")
        return True  # 예외 억제

# 사용 예시
with CustomContextManager() as cm:
    print("컨텍스트 내부")
    # raise ValueError("테스트 예외")  # 예외 발생 시
```

**동작 원리:**
1. `with` 진입 시 `__enter__()` 호출
2. `with` 블록 실행
3. `with` 종료 시 `__exit__()` 호출
4. `__exit__()`에서 `False` 반환 시 예외 재발생, `True` 반환 시 예외 억제

#### Q3: "실무에서 예외 처리와 로깅을 어떻게 연계하나요?"

**A3:**
```python
import logging
from functools import wraps

def log_exceptions(logger_name: str):
    """예외 로깅 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name)
            try:
                logger.info(f"함수 {func.__name__} 실행 시작")
                result = func(*args, **kwargs)
                logger.info(f"함수 {func.__name__} 실행 완료")
                return result
            except Exception as e:
                logger.error(
                    f"함수 {func.__name__} 실행 중 예외 발생",
                    exc_info=True,  # 스택 트레이스 포함
                    extra={
                        'function_name': func.__name__,
                        'args': args,
                        'kwargs': kwargs,
                        'exception_type': type(e).__name__
                    }
                )
                raise
        return wrapper
    return decorator

# 사용 예시
@log_exceptions("user_service")
def process_user(user_id: int):
    if user_id <= 0:
        raise ValueError("잘못된 사용자 ID")
    return {"id": user_id, "status": "active"}

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 테스트
try:
    process_user(-1)
except Exception as e:
    print(f"예외 발생: {e}")
```

## 🎯 실전용 요약 문장 (이력서/면접/블로그용)

**"Python의 예외 처리와 컨텍스트 관리자를 활용하여 안전하고 효율적인 리소스 관리를 구현했습니다. 특히 커스텀 예외 클래스로 도메인별 오류를 체계적으로 분류하고, contextlib 모듈을 활용한 실무형 컨텍스트 매니저로 데이터베이스 연결, 분산 락, API 재시도 로직 등을 안전하게 처리했습니다."**

## 📚 학습 우선순위 (3년차 기준)

| 우선순위 | 주제 | 익혀야 할 내용 |
|----------|------|----------------|
| **필수** | 예외 처리 | try-except-else-finally 구조와 구체적 예외 처리 |
| **필수** | 커스텀 예외 | 도메인별 예외 클래스 정의와 계층 구조 |
| **필수** | 컨텍스트 매니저 | `__enter__`/`__exit__` 메서드와 with 구문 |
| **필수** | contextlib | `@contextmanager` 데코레이터 활용 |
| **추천** | 실무 적용 | 로깅과 연계한 예외 처리, 리소스 관리 |
| **추천** | 고급 패턴 | 분산 락, 재시도 로직, 성능 모니터링 |

## 🚀 실무 적용 체크리스트

### 예외 처리 설계
- [ ] 구체적인 예외 클래스 정의
- [ ] 예외 계층 구조 설계
- [ ] 로깅과 예외 처리 연계
- [ ] 사용자 친화적인 오류 메시지 작성

### 컨텍스트 매니저 구현
- [ ] 리소스 관리용 컨텍스트 매니저 구현
- [ ] `@contextmanager` 데코레이터 활용
- [ ] 예외 발생 시에도 안전한 리소스 정리
- [ ] 성능 모니터링과 에러 처리 통합

### 로깅 시스템 구축
- [ ] 구조화된 로깅 포맷 설계
- [ ] 로그 레벨별 처리 전략
- [ ] 예외 정보와 스택 트레이스 포함
- [ ] 로그 파일 관리 및 로테이션

---

<details>
<summary>참고 자료</summary>

- [Python Exception Handling](https://docs.python.org/3/tutorial/errors.html)
- [Context Managers](https://docs.python.org/3/reference/datamodel.html#context-managers)
- [contextlib — Utilities for with-statement contexts](https://docs.python.org/3/library/contextlib.html)
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [PEP 343 -- The "with" Statement](https://www.python.org/dev/peps/pep-0343/)

</details> 



