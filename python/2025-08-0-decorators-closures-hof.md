---
title: "Python 클로저, 데코레이터, 고차 함수(HOF)"
date: 2025-08-19
categories:
  - python
tags:
  - closure
  - decorator
  - higher-order-function
  - python-advanced
  - backend-development
---

# Python 클로저, 데코레이터, 고차 함수(HOF)

## 1. 개념 및 관계

### 1.1 세 개념의 연결고리

클로저, HOF, 데코레이터는 서로 밀접하게 연결된 개념이다. 

| 개념 | 설명 | 관계 |
|------|------|------|
| **클로저 (Closure)** | 외부 함수의 변수를 내부 함수가 기억하는 구조 | 데코레이터와 HOF의 기초가 되는 개념 |
| **HOF (Higher-Order Function)** | 함수를 인자로 받거나, 함수를 리턴하는 함수 | 데코레이터도 결국 HOF의 한 형태 |
| **데코레이터 (Decorator)** | 기존 함수를 감싸서 기능을 확장하는 문법적 슈가 | 보통 클로저 + HOF 조합으로 구현 |

### 1.2 클로저 (Closure) - 기초 개념

**클로저는 내부 함수가 외부 함수의 지역변수를 기억하고 있는 상태입니다.**

```python
def outer_function(x):
    """외부 함수"""
    def inner_function(y):
        """내부 함수 - 클로저"""
        return x + y  # 외부 함수의 변수 x를 기억
    return inner_function

# 클로저 생성
add_five = outer_function(5)
add_ten = outer_function(10)

print(add_five(3))   # 8 (5 + 3)
print(add_ten(3))    # 13 (10 + 3)

# 클로저의 상태 확인
print(f"add_five.__closure__: {add_five.__closure__}")
print(f"add_five.__closure__[0].cell_contents: {add_five.__closure__[0].cell_contents}")
```

**클로저의 핵심 포인트:**
- 외부 함수의 변수는 `__closure__` 속성에 저장됨
- 각 클로저는 자신만의 독립적인 상태를 가짐
- 메모리에 변수 값이 계속 유지됨

### 1.3 HOF (Higher-Order Function) - 고차 함수

**HOF는 함수를 인자로 받거나, 함수를 반환하는 함수입니다.**

```python
def apply_operation(func, a, b):
    """함수를 인자로 받는 HOF"""
    return func(a, b)

def multiply(x, y):
    return x * y

def divide(x, y):
    return x / y if y != 0 else None

# HOF 사용
result1 = apply_operation(multiply, 10, 5)  # 50
result2 = apply_operation(divide, 10, 2)    # 5.0

# 함수를 반환하는 HOF
def create_power_function(exponent):
    """함수를 반환하는 HOF"""
    def power_function(base):
        return base ** exponent
    return power_function

# 사용 예시
square = create_power_function(2)
cube = create_power_function(3)

print(square(5))  # 25
print(cube(3))    # 27
```

### 1.4 데코레이터 (Decorator) - 실무의 핵심

**데코레이터는 함수를 인자로 받아서, 기능을 확장한 후 다시 함수로 반환하는 구조입니다.**

```python
def simple_decorator(func):
    """가장 기본적인 데코레이터"""
    def wrapper(*args, **kwargs):
        print(f"함수 {func.__name__} 실행 전")
        result = func(*args, **kwargs)
        print(f"함수 {func.__name__} 실행 후")
        return result
    return wrapper

@simple_decorator
def greet(name):
    print(f"안녕하세요, {name}님!")

# 사용
greet("홍길동")
```

## 2. 실무 활용 사례

### 2.1 로깅 데코레이터

실무에서 가장 많이 사용되는 로깅 데코레이터를 구현해보겠습니다.

```python
import logging
import time
from functools import wraps
from typing import Callable, Any

def logging_decorator(level: str = "INFO"):
    """로깅 데코레이터 - 실무에서 자주 사용"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)  # 원본 함수 메타데이터 유지
        def wrapper(*args, **kwargs) -> Any:
            logger = logging.getLogger(func.__module__)
            logger.setLevel(getattr(logging, level.upper()))
            
            # 함수 실행 전 로깅
            logger.info(f"함수 {func.__name__} 실행 시작 - 인자: {args}, {kwargs}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # 성공 시 로깅
                logger.info(f"함수 {func.__name__} 실행 완료 - 소요시간: {execution_time:.3f}초")
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # 실패 시 로깅
                logger.error(f"함수 {func.__name__} 실행 실패 - 에러: {e}, 소요시간: {execution_time:.3f}초")
                raise
        
        return wrapper
    return decorator

# 사용 예시
@logging_decorator(level="DEBUG")
def process_user_data(user_id: int, data: dict) -> dict:
    """사용자 데이터 처리 함수"""
    time.sleep(0.1)  # 처리 시간 시뮬레이션
    return {"user_id": user_id, "processed": True, "data": data}

# 실행
result = process_user_data(123, {"name": "홍길동", "age": 30})
```

### 2.2 인증 데코레이터

API 인증을 위한 데코레이터를 구현해보겠습니다.

```python
from functools import wraps
from typing import Callable, Any
import jwt
from datetime import datetime, timedelta

def require_auth(required_roles: list = None):
    """인증 및 권한 체크 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 실제로는 request 객체에서 토큰을 추출
            # 여기서는 간단한 예시로 구현
            token = kwargs.get('token') or (args[0] if args else None)
            
            if not token:
                raise ValueError("인증 토큰이 필요합니다")
            
            try:
                # JWT 토큰 검증 (실제로는 SECRET_KEY 사용)
                payload = jwt.decode(token, "secret", algorithms=["HS256"])
                user_id = payload.get('user_id')
                user_roles = payload.get('roles', [])
                
                # 권한 체크
                if required_roles and not any(role in user_roles for role in required_roles):
                    raise PermissionError(f"필요한 권한: {required_roles}, 현재 권한: {user_roles}")
                
                # 원본 함수에 사용자 정보 추가
                kwargs['user_id'] = user_id
                kwargs['user_roles'] = user_roles
                
                return func(*args, **kwargs)
                
            except jwt.ExpiredSignatureError:
                raise ValueError("토큰이 만료되었습니다")
            except jwt.InvalidTokenError:
                raise ValueError("유효하지 않은 토큰입니다")
        
        return wrapper
    return decorator

# 사용 예시
@require_auth(required_roles=["admin"])
def delete_user(user_id: int, token: str = None) -> dict:
    """사용자 삭제 함수 - admin 권한 필요"""
    return {"message": f"사용자 {user_id} 삭제 완료", "deleted_by": user_id}

# 테스트용 토큰 생성
def create_test_token(user_id: int, roles: list):
    payload = {
        'user_id': user_id,
        'roles': roles,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, "secret", algorithm="HS256")

# 테스트
admin_token = create_test_token(1, ["admin", "user"])
user_token = create_test_token(2, ["user"])

try:
    # admin 권한으로 실행
    result = delete_user(123, admin_token)
    print(result)
    
    # 일반 사용자 권한으로 실행 (실패)
    result = delete_user(123, user_token)
except Exception as e:
    print(f"권한 부족: {e}")
```

### 2.3 캐싱 데코레이터

메모리 효율적인 캐싱 데코레이터를 구현해보겠습니다.

```python
import time
from functools import wraps
from typing import Callable, Any, Dict, Tuple
import weakref

def cache_with_ttl(ttl_seconds: int = 300):
    """TTL이 있는 캐싱 데코레이터"""
    def decorator(func: Callable) -> Callable:
        # 캐시 저장소 (함수별로 독립적)
        cache: Dict[Tuple, Tuple[Any, float]] = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 캐시 키 생성 (인자 기반)
            cache_key = (args, tuple(sorted(kwargs.items())))
            current_time = time.time()
            
            # 캐시에서 결과 확인
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < ttl_seconds:
                    return result
                else:
                    # TTL 만료된 캐시 제거
                    del cache[cache_key]
            
            # 함수 실행 및 결과 캐싱
            result = func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            
            return result
        
        # 캐시 통계 메서드 추가
        wrapper.cache_info = lambda: {
            'size': len(cache),
            'keys': list(cache.keys())
        }
        
        wrapper.clear_cache = lambda: cache.clear()
        
        return wrapper
    return decorator

# 사용 예시
@cache_with_ttl(ttl_seconds=10)
def expensive_calculation(n: int) -> int:
    """비용이 큰 계산 함수"""
    time.sleep(1)  # 계산 시간 시뮬레이션
    return n * n

# 첫 번째 실행 (캐시 없음)
start_time = time.time()
result1 = expensive_calculation(5)
first_execution_time = time.time() - start_time

# 두 번째 실행 (캐시 사용)
start_time = time.time()
result2 = expensive_calculation(5)
second_execution_time = time.time() - start_time

print(f"첫 번째 실행: {first_execution_time:.3f}초")
print(f"두 번째 실행: {second_execution_time:.3f}초")
print(f"캐시 정보: {expensive_calculation.cache_info()}")
```

### 2.4 재시도 로직 데코레이터

네트워크 요청 등에서 자주 사용되는 재시도 로직을 구현해보겠습니다.

```python
import time
from functools import wraps
from typing import Callable, Any, Type, Tuple
import random

def retry_on_exception(
    max_attempts: int = 3,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    delay: float = 1.0,
    backoff_factor: float = 2.0
):
    """예외 발생 시 재시도하는 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        raise last_exception
                    
                    # 지수 백오프 + 지터 (jitter) 적용
                    wait_time = delay * (backoff_factor ** (attempt - 1))
                    jitter = random.uniform(0, 0.1 * wait_time)
                    total_wait = wait_time + jitter
                    
                    print(f"시도 {attempt} 실패: {e}. {total_wait:.2f}초 후 재시도...")
                    time.sleep(total_wait)
            
            raise last_exception
        
        return wrapper
    return decorator

# 사용 예시
@retry_on_exception(max_attempts=3, exceptions=(ValueError,), delay=0.5)
def unreliable_function():
    """불안정한 함수 - 가끔 실패"""
    if random.random() < 0.7:  # 70% 확률로 실패
        raise ValueError("임시 오류 발생")
    return "성공!"

# 테스트
for i in range(3):
    try:
        result = unreliable_function()
        print(f"시도 {i+1}: {result}")
        break
    except Exception as e:
        print(f"시도 {i+1}: 최종 실패 - {e}")
```

## 3. 면접 대비

### 3.1 핵심 면접 질문과 답변

#### Q1: "파이썬 클로저가 뭐고, 어떤 상황에서 쓸 수 있나요?"

**A1:**
```python
# 클로저 정의
def create_counter():
    count = 0  # 외부 함수의 지역변수
    
    def counter():
        nonlocal count  # nonlocal 키워드로 외부 변수 수정
        count += 1
        return count
    
    return counter

# 사용 예시
counter1 = create_counter()
counter2 = create_counter()

print(counter1())  # 1
print(counter1())  # 2
print(counter2())  # 1 (독립적인 상태)
```

**상황별 활용:**
- **상태 유지**: 카운터, 설정 관리
- **데이터 은닉**: 클래스 대신 간단한 상태 관리
- **콜백 함수**: 이벤트 핸들러에서 상태 보존

#### Q2: "그럼 외부 변수는 어디에 저장되나요?"

**A2:**
```python
def outer(x):
    def inner(y):
        return x + y
    return inner

closure_func = outer(10)
print(f"__closure__: {closure_func.__closure__}")
print(f"cell_contents: {closure_func.__closure__[0].cell_contents}")

# 출력:
# __closure__: (<cell at 0x...: int object at 0x...>,)
# cell_contents: 10
```

**핵심 포인트:**
- `__closure__` 속성에 `cell` 객체로 저장
- 각 클로저마다 독립적인 `cell` 객체
- 메모리에 변수 값이 계속 유지됨

#### Q3: "파이썬 데코레이터를 직접 구현해보세요."

**A3:**
```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"함수 {func.__name__} 실행 전")
        result = func(*args, **kwargs)
        print(f"함수 {func.__name__} 실행 후")
        return result
    return wrapper

@my_decorator
def hello(name):
    print(f"안녕하세요, {name}님!")

# @my_decorator는 다음과 동일:
# hello = my_decorator(hello)
```

### 3.2 고급 면접 꼬리 질문

#### Q4: "인자가 있는 데코레이터는 어떻게 만들어요?"

**A4:**
```python
def decorator_with_args(arg1, arg2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"데코레이터 인자: {arg1}, {arg2}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@decorator_with_args("hello", "world")
def test_func():
    print("테스트 함수 실행")

# @decorator_with_args("hello", "world")는 다음과 동일:
# test_func = decorator_with_args("hello", "world")(test_func)
```

#### Q5: "클래스에 데코레이터 쓸 때 주의할 점은?"

**A5:**
```python
def method_decorator(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print(f"메서드 {func.__name__} 실행")
        return func(self, *args, **kwargs)
    return wrapper

class MyClass:
    @method_decorator
    def my_method(self, x):
        return x * 2

# 주의사항:
# 1. self 인자 처리
# 2. @wraps 사용으로 메서드 정보 유지
# 3. 정적 메서드와 클래스 메서드 구분
```

#### Q6: "functools.wraps()의 역할은?"

**A6:**
```python
from functools import wraps

def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def good_decorator(func):
    @wraps(func)  # 원본 함수 메타데이터 유지
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@bad_decorator
def original_func():
    """이 함수는 원본 함수입니다."""
    pass

@good_decorator
def original_func2():
    """이 함수는 원본 함수입니다."""
    pass

print(f"bad_decorator: {original_func.__name__}")      # wrapper
print(f"good_decorator: {original_func2.__name__}")    # original_func2
print(f"bad_decorator doc: {original_func.__doc__}")   # None
print(f"good_decorator doc: {original_func2.__doc__}") # 이 함수는 원본 함수입니다.
```

## 4. 고급 기법

### 4.1 클래스 데코레이터

클래스 자체를 데코레이션하는 고급 기법입니다.

```python
def singleton(cls):
    """싱글톤 패턴을 위한 클래스 데코레이터"""
    instances = {}
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class DatabaseConnection:
    def __init__(self):
        self.connection_string = "postgresql://..."
        print("데이터베이스 연결 생성")
    
    def query(self, sql):
        return f"실행된 쿼리: {sql}"

# 테스트
db1 = DatabaseConnection()
db2 = DatabaseConnection()
print(f"db1 is db2: {db1 is db2}")  # True
```

### 4.2 체이닝 데코레이터

여러 데코레이터를 조합해서 사용하는 방법입니다.

```python
def validate_input(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 입력 검증 로직
        if not args or not isinstance(args[0], (int, float)):
            raise ValueError("숫자 입력이 필요합니다")
        return func(*args, **kwargs)
    return wrapper

def log_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"함수 {func.__name__} 실행")
        result = func(*args, **kwargs)
        print(f"함수 {func.__name__} 완료")
        return result
    return wrapper

@log_execution
@validate_input
def calculate_square(x):
    return x ** 2

# 체이닝 순서: validate_input -> log_execution -> calculate_square
# 실제로는: calculate_square = log_execution(validate_input(calculate_square))
```

### 4.3 매개변수화된 데코레이터 팩토리

더 유연한 데코레이터를 만드는 고급 패턴입니다.

```python
def retry_factory(
    max_attempts: int = 3,
    exceptions: tuple = (Exception,),
    delay: float = 1.0
):
    """재시도 로직을 위한 데코레이터 팩토리"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise e
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

# 사용 예시
@retry_factory(max_attempts=5, exceptions=(ValueError,), delay=0.5)
def risky_operation():
    if random.random() < 0.8:
        raise ValueError("위험한 작업 실패")
    return "성공!"
```

## 5. 실무 적용 시 주의사항

### 5.1 성능 고려사항

```python
import time
from functools import wraps

def performance_monitor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        execution_time = (end_time - start_time) * 1000  # ms
        if execution_time > 100:  # 100ms 이상 걸리는 함수 경고
            print(f"⚠️  {func.__name__}: {execution_time:.2f}ms")
        
        return result
    return wrapper

@performance_monitor
def slow_function():
    time.sleep(0.2)  # 200ms
    return "완료"
```

### 5.2 디버깅과 테스트

```python
def debug_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"🔍 {func.__name__} 호출")
        print(f"   인자: {args}")
        print(f"   키워드 인자: {kwargs}")
        
        try:
            result = func(*args, **kwargs)
            print(f"✅ {func.__name__} 성공: {result}")
            return result
        except Exception as e:
            print(f"❌ {func.__name__} 실패: {e}")
            raise
    
    return wrapper

@debug_decorator
def test_function(x, y, operation="add"):
    if operation == "add":
        return x + y
    elif operation == "multiply":
        return x * y
    else:
        raise ValueError(f"알 수 없는 연산: {operation}")
```

## 🎯 실전용 요약 문장 (이력서/면접/블로그용)

**"파이썬의 클로저와 고차 함수 개념을 기반으로, 데코레이터를 직접 구현해 공통 처리 로직(로깅, 예외 처리, 인증 등)을 추상화해 사용한 경험이 있습니다. 특히 functools.wraps를 통한 원래 함수 메타데이터 유지, 인자를 받는 데코레이터 구조 등 실무에 적용 가능한 형태로 구성했습니다."**

## ✨ 예시 코드 (세 개를 모두 담은 실무형 예시)

```python
from functools import wraps
import time
import logging
from typing import Callable, Any

# ✅ 고차함수 + 클로저 + 데코레이터
def timing_decorator(label=""):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            
            print(f"[{label}] {func.__name__} took {end - start:.3f}s")
            return result
        return wrapper
    return decorator

@timing_decorator(label="Test")
def slow_add(a, b):
    time.sleep(1)
    return a + b

print(slow_add(1, 2))
```

## 📚 학습 우선순위 (3년차 기준)

| 우선순위 | 주제 | 익혀야 할 내용 |
|----------|------|----------------|
| **필수** | 클로저 | `nonlocal`, `__closure__`, 내부 함수에서 외부 변수 캡처 구조 |
| **필수** | 데코레이터 | 기본, 인자 있는 데코레이터, 클래스 데코레이터 구현 |
| **필수** | wraps | `functools.wraps`와 데코레이터 체이닝 시 문제 해결 |
| **추천** | 실전 적용 | API 인증, 재시도 데코레이터, 슬랙 알림 자동화 |
| **블로그용** | 개념 관계 | 세 개념의 관계 시각화 및 실전 적용 예시 정리 |

---

<details>
<summary>참고 자료</summary>

- Python 공식 문서: [Decorators](https://docs.python.org/3/glossary.html#term-decorator)
- Python 공식 문서: [Closures](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces)
- Real Python: [Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/)
- Python Tricks: The Book - Dan Bader

</details> 



