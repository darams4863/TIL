---
title: "파이썬 필수 문법"
date: 2025-08-15
categories:
  - python
tags:
  - python-basics
  - classes
  - generators
  - context-managers
  - decorators
  - async-await
---

# 파이썬 필수 문법

## 1. 핵심 키워드와 문법

### with 구문 (Context Manager)
- **핵심 개념**: 자동 리소스 관리
- **실무 활용**: 파일 열기, DB 연결, 락 처리 등 리소스 관리가 필요한 작업
- **면접 포인트**: `__enter__`, `__exit__` 메서드 구현 방법과 `contextlib` 활용

```python
# 기본 with 구문
with open('file.txt', 'r') as f:
    content = f.read()

# 커스텀 컨텍스트 매니저
class DatabaseConnection:
    def __enter__(self):
        print("DB 연결")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("DB 연결 해제")
        if exc_type:
            print(f"에러 발생: {exc_val}")
        return False

# contextlib 활용
from contextlib import contextmanager
@contextmanager
def timer():
    import time
    start = time.time()
    yield
    print(f"실행 시간: {time.time() - start:.2f}초")
```

### yield, yield from (제너레이터)
- **핵심 개념**: 메모리 효율적인 데이터 생성
- **실무 활용**: 대용량 데이터 처리, 스트리밍 응답, 메모리 절약
- **면접 포인트**: 일반 함수와의 차이점, 언제 사용하는지

```python
def number_generator(n):
    for i in range(n):
        yield i

def nested_generator():
    yield from number_generator(3)
    yield from number_generator(2)

# 사용
for num in nested_generator():
    print(num)  # 0, 1, 2, 0, 1

# 제너레이터 표현식 (메모리 효율적)
squares = (x**2 for x in range(1000000))
```

### @staticmethod, @classmethod, @property
- **핵심 개념**: 클래스 메서드의 종류와 차이점
- **실무 활용**: 설계 관점에서 클래스나 인스턴스 조작 시 중요
- **면접 포인트**: 각각의 사용 시기와 차이점

```python
class User:
    user_count = 0
    
    def __init__(self, name):
        self.name = name
        User.user_count += 1
    
    @classmethod
    def get_user_count(cls):
        return cls.user_count
    
    @staticmethod
    def is_valid_name(name):
        return len(name) > 0
    
    @property
    def display_name(self):
        return f"User: {self.name}"
    
    @display_name.setter
    def display_name(self, value):
        if not self.is_valid_name(value):
            raise ValueError("Invalid name")
        self.name = value
```

### *args, **kwargs
- **핵심 개념**: 가변 인자 처리
- **실무 활용**: 래퍼 함수, 데코레이터, 일반 함수 정의에서 자주 사용
- **면접 포인트**: 언패킹과 패킹의 개념

```python
def wrapper_function(*args, **kwargs):
    print(f"Positional args: {args}")
    print(f"Keyword args: {kwargs}")
    return args, kwargs

# 사용
result = wrapper_function(1, 2, name="Alice", age=25)

# 언패킹
numbers = [1, 2, 3]
kwargs = {"name": "Bob", "age": 30}
wrapper_function(*numbers, **kwargs)
```

### lambda (익명 함수)
- **핵심 개념**: 간단한 일회성 함수
- **실무 활용**: 정렬 키, filter(), map() 등과 함께 사용
- **면접 포인트**: 언제 사용하고 언제 사용하지 말아야 하는지

```python
# 정렬
users = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
sorted_users = sorted(users, key=lambda x: x["age"])

# filter, map
numbers = [1, 2, 3, 4, 5]
evens = list(filter(lambda x: x % 2 == 0, numbers))
squares = list(map(lambda x: x**2, numbers))

# 주의: 복잡한 로직은 일반 함수로 작성
# 좋지 않은 예
bad_lambda = lambda x: x**2 if x > 0 else 0 if x == 0 else -x**2
```

### enumerate, zip
- **핵심 개념**: 인덱스+값 반복, 여러 리스트 동시 반복
- **실무 활용**: for 루프에서 인덱스와 값이 모두 필요할 때, 병렬 처리
- **면접 포인트**: 언제 사용하는지, 메모리 효율성

```python
# enumerate: 인덱스와 값 동시 접근
fruits = ["apple", "banana", "cherry"]
for index, fruit in enumerate(fruits, start=1):
    print(f"{index}. {fruit}")

# zip: 여러 리스트 병렬 처리
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]
for name, age in zip(names, ages):
    print(f"{name} is {age} years old")

# zip_longest (itertools)
from itertools import zip_longest
for name, age in zip_longest(names, ages, fillvalue="Unknown"):
    print(f"{name}: {age}")
```

### is vs ==, copy vs deepcopy
- **핵심 개념**: 객체 식별 vs 값 비교, 얕은 복사 vs 깊은 복사
- **실무 활용**: None 체크, 사이드 이펙트 방지
- **면접 포인트**: 언제 어떤 것을 사용해야 하는지

```python
# is vs ==
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)  # True (값 비교)
print(a is b)  # False (객체 식별)

# None 체크는 is 사용
x = None
if x is None:  # 권장
    print("x is None")

# copy vs deepcopy
import copy
original = [1, [2, 3], {"a": 4}]

shallow = copy.copy(original)
deep = copy.deepcopy(original)

original[1][0] = 999
print(shallow[1][0])  # 999 (참조 공유)
print(deep[1][0])     # 2 (독립적)
```

### 예외 처리 (try/except/finally, raise, assert)
- **핵심 개념**: 에러 처리와 검증
- **실무 활용**: 네트워크 작업, 파일 I/O, DB 상호작용에서 필수
- **면접 포인트**: 예외 처리 전략과 커스텀 예외

```python
# 기본 예외 처리
def divide(a, b):
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("0으로 나눌 수 없습니다")
        return None
    except TypeError:
        print("숫자가 아닌 값입니다")
        return None
    finally:
        print("연산 완료")

# 커스텀 예외
class ValidationError(Exception):
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(self.message)

# raise로 예외 발생
def validate_age(age):
    if age < 0:
        raise ValidationError("나이는 음수일 수 없습니다", "age")
    return True

# assert (테스트/디버깅용)
def process_data(data):
    assert len(data) > 0, "데이터가 비어있습니다"
    assert all(isinstance(x, (int, float)) for x in data), "모든 요소는 숫자여야 합니다"
    return sum(data)
```

### 변수 스코프 (global, nonlocal)
- **핵심 개념**: 변수 접근 범위
- **실무 활용**: 클로저 함수에서 중첩 스코프 수정 시
- **면접 포인트**: 스코프 규칙과 사용 시기

```python
# global
counter = 0

def increment():
    global counter
    counter += 1
    return counter

# nonlocal
def outer():
    count = 0
    
    def inner():
        nonlocal count
        count += 1
        return count
    
    return inner

# 사용
func = outer()
print(func())  # 1
print(func())  # 2
```

### __name__ == "__main__"
- **핵심 개념**: 모듈 실행 진입점
- **실무 활용**: 스크립트가 직접 실행될 때와 임포트될 때 구분
- **면접 포인트**: 모듈 시스템 이해

```python
def main():
    print("메인 함수 실행")

if __name__ == "__main__":
    main()
else:
    print("모듈로 임포트됨")
```

## 2. 클래스와 객체 심화

### 상속과 다형성
```python
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return f"{self.name}가 멍멍!"

class Cat(Animal):
    def speak(self):
        return f"{self.name}가 야옹!"

# 다형성
animals = [Dog("멍멍이"), Cat("야옹이")]
for animal in animals:
    print(animal.speak())
```

### 추상 클래스와 인터페이스
```python
from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def disconnect(self):
        pass
    
    @abstractmethod
    def execute(self, query: str):
        pass

class PostgreSQL(DatabaseInterface):
    def connect(self):
        return "PostgreSQL 연결됨"
    
    def disconnect(self):
        return "PostgreSQL 연결 해제됨"
    
    def execute(self, query: str):
        return f"PostgreSQL에서 실행: {query}"

# 추상 클래스는 직접 인스턴스화 불가
# db = DatabaseInterface()  # TypeError
```

### 매직 메서드 활용
```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __str__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __repr__(self):
        return f"Vector(x={self.x}, y={self.y})"

# 연산자 오버로딩
v1 = Vector(1, 2)
v2 = Vector(3, 4)
v3 = v1 + v2  # Vector(4, 6)
print(v1 == v2)  # False
```

## 3. 제너레이터와 yield 심화

### 제너레이터 체이닝과 파이프라인
```python
def number_generator(n):
    for i in range(n):
        yield i

def filter_even(numbers):
    for num in numbers:
        if num % 2 == 0:
            yield num

def square_numbers(numbers):
    for num in numbers:
        yield num ** 2

# 제너레이터 체이닝
numbers = number_generator(10)
even_numbers = filter_even(numbers)
squared_even = square_numbers(even_numbers)

# 메모리 효율적인 파이프라인
for result in squared_even:
    print(result)  # 0, 4, 16, 36, 64
```

### 제너레이터와 코루틴
```python
def coroutine_example():
    while True:
        x = yield
        if x is None:
            break
        yield x * 2

# 코루틴 사용
coro = coroutine_example()
next(coro)  # 제너레이터 시작

print(coro.send(5))      # 10
print(coro.send(10))     # 20
coro.send(None)          # 종료
```

### 제너레이터 성능 최적화
```python
import time
import memory_profiler

# 메모리 사용량 비교
@memory_profiler.profile
def list_approach(n):
    return [i**2 for i in range(n)]

@memory_profiler.profile
def generator_approach(n):
    for i in range(n):
        yield i**2

# 대용량 데이터 처리 시 제너레이터가 유리
large_n = 10000000
# list_result = list_approach(large_n)  # 메모리 많이 사용
# gen_result = generator_approach(large_n)  # 메모리 효율적
```

## 4. 컨텍스트 매니저 심화

### 비동기 컨텍스트 매니저
```python
import asyncio

class AsyncDatabaseConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connection = None
    
    async def __aenter__(self):
        print(f"비동기 연결 시작: {self.host}:{self.port}")
        # 실제로는 비동기 연결 로직
        await asyncio.sleep(0.1)  # 연결 시뮬레이션
        self.connection = f"Async connected to {self.host}:{self.port}"
        return self.connection
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("비동기 연결 해제")
        self.connection = None

async def async_main():
    async with AsyncDatabaseConnection("localhost", 5432) as conn:
        print(f"연결됨: {conn}")
        await asyncio.sleep(1)  # 작업 시뮬레이션
```

### 커스텀 컨텍스트 매니저
```python
class DatabaseConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connection = None
    
    def __enter__(self):
        print(f"데이터베이스 연결: {self.host}:{self.port}")
        self.connection = f"Connected to {self.host}:{self.port}"
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("데이터베이스 연결 해제")
        self.connection = None
        if exc_type:
            print(f"에러 발생: {exc_val}")
        return False  # 예외를 다시 발생시킴

# 사용
with DatabaseConnection("localhost", 5432) as conn:
    print(f"연결됨: {conn}")
    # 작업 수행
```

### contextlib 사용
- 
```python
from contextlib import contextmanager

@contextmanager
def timer():
    import time
    start = time.time()
    yield                    # 👈 이 지점에서 with 블록 안으로 진입!
    end = time.time()
    print(f"실행 시간: {end - start:.2f}초")

# 사용 예시
with timer():               # 👈 이때 timer() 함수가 호출되고, yield에서 멈춤
    time.sleep(1)           # 👈 이 작업이 수행됨 (블록 내부 작업)
# 블록이 끝나면 yield 이후 코드 실행 (실행 시간 출력)
```

## 5. 데코레이터 심화

### 메타데코레이터와 체이닝
```python
def validate_input(*validators):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 입력 검증
            for validator in validators:
                validator(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_positive(*args):
    if any(arg <= 0 for arg in args if isinstance(arg, (int, float))):
        raise ValueError("모든 인자는 양수여야 합니다")

def check_string_length(max_length):
    def validator(*args):
        if any(len(str(arg)) > max_length for arg in args):
            raise ValueError(f"문자열 길이는 {max_length}를 초과할 수 없습니다")
    return validator

@validate_input(check_positive, check_string_length(10))
def process_data(value, name):
    return f"처리됨: {value}, {name}"

# 사용
try:
    result = process_data(5, "short")
    print(result)
    result = process_data(-1, "short")  # ValueError
except ValueError as e:
    print(f"검증 실패: {e}")
```

### 데코레이터 팩토리와 설정
```python
def configurable_decorator(**config):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 설정에 따른 동작 변경
            if config.get('log', False):
                print(f"함수 {func.__name__} 호출됨")
            
            if config.get('cache', False):
                # 간단한 캐싱 구현
                cache_key = str(args) + str(kwargs)
                if not hasattr(wrapper, '_cache'):
                    wrapper._cache = {}
                if cache_key in wrapper._cache:
                    return wrapper._cache[cache_key]
                
                result = func(*args, **kwargs)
                wrapper._cache[cache_key] = result
                return result
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

@configurable_decorator(log=True, cache=True)
def expensive_calculation(n):
    import time
    time.sleep(1)  # 비용이 큰 계산 시뮬레이션
    return n * n

# 첫 번째 호출: 로그 출력 + 계산
result1 = expensive_calculation(5)
# 두 번째 호출: 캐시된 결과 반환
result2 = expensive_calculation(5)
```

### 데코레이터와 타입 힌트
```python
from typing import Callable, TypeVar, Any
from functools import wraps

F = TypeVar('F', bound=Callable[..., Any])

def type_check(func: F) -> F:
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 타입 검사 로직 (실제로는 더 복잡)
        annotations = func.__annotations__
        for name, value in zip(func.__code__.co_varnames[1:], args):
            if name in annotations:
                expected_type = annotations[name]
                if not isinstance(value, expected_type):
                    raise TypeError(f"{name}은 {expected_type} 타입이어야 합니다")
        
        return func(*args, **kwargs)
    return wrapper

@type_check
def greet(name: str, age: int) -> str:
    return f"안녕하세요, {name}님! {age}살이시군요"

# 올바른 타입
print(greet("Alice", 25))

# 잘못된 타입
try:
    print(greet("Bob", "30"))
except TypeError as e:
    print(f"타입 에러: {e}")
```

## 6. 비동기 프로그래밍 심화

### 비동기 제너레이터와 스트리밍
```python
import asyncio
import aiofiles

async def async_file_reader(file_path):
    """비동기 파일 읽기 제너레이터"""
    async with aiofiles.open(file_path, 'r') as file:
        async for line in file:
            yield line.strip()

async def process_large_file():
    async for line in async_file_reader('large_file.txt'):
        # 각 라인을 비동기로 처리
        processed = await process_line_async(line)
        yield processed

async def process_line_async(line):
    # 실제로는 복잡한 비동기 처리
    await asyncio.sleep(0.01)
    return f"처리됨: {line}"
```

### 비동기 작업 처리 (실무 스타일)
```python
import asyncio
import aiohttp

async def fetch_user_data(user_id: int) -> dict:
    """사용자 데이터를 비동기로 가져오기"""
    async with aiohttp.ClientSession() as session:
        url = f"https://api.example.com/users/{user_id}"
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"API 호출 실패: {response.status}")

async def process_multiple_users(user_ids: list[int]) -> list[dict]:
    """여러 사용자 데이터를 동시에 처리"""
    tasks = [fetch_user_data(user_id) for user_id in user_ids]
    
    # 모든 요청을 동시에 실행
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 성공한 결과만 필터링
    successful_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"사용자 {user_ids[i]} 처리 실패: {result}")
        else:
            successful_results.append(result)
    
    return successful_results

# 사용 예시
async def main():
    user_ids = [1, 2, 3, 4, 5]
    users = await process_multiple_users(user_ids)
    print(f"성공적으로 처리된 사용자: {len(users)}명")

# 실행
# asyncio.run(main())
```

### 비동기 성능 최적화
```python
import asyncio
import time

async def optimized_fetch(urls):
    """비동기 성능 최적화된 URL 페칭"""
    semaphore = asyncio.Semaphore(10)  # 동시 요청 제한
    
    async def fetch_with_semaphore(url):
        async with semaphore:
            # 실제로는 aiohttp 사용
            await asyncio.sleep(0.1)
            return f"결과: {url}"
    
    # 모든 URL을 동시에 처리
    tasks = [fetch_with_semaphore(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 에러 처리
    successful_results = [r for r in results if not isinstance(r, Exception)]
    failed_results = [r for r in results if isinstance(r, Exception)]
    
    return successful_results, failed_results

# 사용 예시
urls = [f"https://api.example.com/{i}" for i in range(100)]
# results, errors = await optimized_fetch(urls)
```

## 7. 예외 처리 심화

### 예외 체이닝과 컨텍스트
```python
def process_data(data):
    try:
        result = complex_calculation(data)
        return result
    except ValueError as e:
        # 예외 체이닝: 원본 예외 정보 보존
        raise RuntimeError(f"데이터 처리 실패: {data}") from e

def complex_calculation(data):
    if not isinstance(data, (int, float)):
        raise ValueError(f"숫자가 아닌 데이터: {type(data)}")
    return data * 2

# 사용
try:
    result = process_data("invalid")
except RuntimeError as e:
    print(f"런타임 에러: {e}")
    print(f"원인: {e.__cause__}")  # 원본 예외
```

### 다중 예외 처리 (실무 스타일)
```python
def process_multiple_items(items):
    """여러 항목을 처리하고 에러를 수집하는 함수"""
    errors = []
    results = []
    
    for item in items:
        try:
            result = process_item(item)
            results.append(result)
        except Exception as e:
            errors.append((item, e))
    
    if errors:
        # 에러 정보를 로깅하고 사용자에게 알림
        error_summary = f"{len(errors)}개 항목 처리 실패"
        print(f"경고: {error_summary}")
        
        # 에러 상세 정보는 로그에 기록
        for item, error in errors:
            print(f"  항목 {item}: {type(error).__name__}: {error}")
    
    return results

def process_item(item):
    """개별 항목 처리"""
    if item < 0:
        raise ValueError("음수는 처리할 수 없습니다")
    if item > 100:
        raise OverflowError("값이 너무 큽니다")
    return item * 2

# 사용
results = process_multiple_items([1, -5, 50, 200, 10])
print(f"성공적으로 처리된 항목: {len(results)}개")
```

### 예외 처리 전략과 로깅
```python
import logging
from functools import wraps

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def exception_handler(func):
    """예외 처리와 로깅을 위한 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 에러 로깅
            logger.error(f"함수 {func.__name__} 실행 중 에러 발생: {e}", 
                        exc_info=True)
            
            # 에러 타입에 따른 처리
            if isinstance(e, ValueError):
                logger.warning("사용자 입력 오류")
                raise ValueError("잘못된 입력입니다") from e
            elif isinstance(e, ConnectionError):
                logger.error("네트워크 연결 오류")
                raise RuntimeError("서비스 일시적 사용 불가") from e
            else:
                # 예상치 못한 에러는 재발생
                raise
    
    return wrapper

@exception_handler
def risky_operation(data):
    if data < 0:
        raise ValueError("음수는 허용되지 않습니다")
    return data * 2

# 사용
try:
    result = risky_operation(-5)
except ValueError as e:
    print(f"처리된 에러: {e}")
```

## 8. 프로젝트 구조와 모듈 관리

### 모듈과 패키지 구조
```python
# 프로젝트 구조 예시
my_project/
├── __init__.py          # 패키지 선언
├── main.py              # 메인 실행 파일
├── config/
│   ├── __init__.py
│   ├── settings.py      # 설정 파일
│   └── database.py      # DB 설정
├── models/
│   ├── __init__.py
│   ├── user.py          # 사용자 모델
│   └── product.py       # 상품 모델
├── services/
│   ├── __init__.py
│   ├── auth.py          # 인증 서비스
│   └── email.py         # 이메일 서비스
└── utils/
    ├── __init__.py
    ├── helpers.py        # 헬퍼 함수
    └── validators.py     # 검증 함수

# __init__.py의 역할
# 1. 디렉토리를 패키지로 인식
# 2. 패키지 초기화 코드
# 3. 외부에서 import할 항목들 정의
```

### Import 구문과 모듈 관리
```python
# 절대 import vs 상대 import
# 절대 import (권장)
from models.user import User
from services.auth import AuthService
from utils.helpers import format_date

# 상대 import (같은 패키지 내에서만)
from .models import User
from ..config import settings

# import 최적화
import os                    # 전체 모듈 import
from datetime import datetime, timedelta  # 특정 클래스만 import
from typing import List, Dict, Optional   # 타입 힌트만 import

# 순환 import 방지
# models/user.py
class User:
    def __init__(self):
        pass

# services/auth.py
from models.user import User  # 직접 import

# main.py
from models.user import User
from services.auth import AuthService
```

### 패키지 초기화와 설정
```python
# __init__.py에서 외부 노출 인터페이스 정의
# models/__init__.py
from .user import User
from .product import Product

__all__ = ['User', 'Product']  # 외부에서 import 가능한 항목들

# config/__init__.py
from .settings import Settings
from .database import DatabaseConfig

# 설정 객체 생성
settings = Settings()
db_config = DatabaseConfig()

# main.py에서 사용
from config import settings, db_config
print(f"데이터베이스: {db_config.host}:{db_config.port}")
```

## 9. 실무에서 자주 사용하는 컬렉션 관련 문법

### 리스트 컴프리헨션
- **핵심 개념**: 간결한 필터/변환 처리
- **실무 활용**: 데이터 전처리, 조건부 필터링
- **면접 포인트**: 가독성과 성능의 균형

```python
# 기본 리스트 컴프리헨션
numbers = [1, 2, 3, 4, 5]
squares = [x**2 for x in numbers if x % 2 == 0]
print(squares)  # [4, 16]

# 중첩 리스트 컴프리헨션
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flattened = [item for row in matrix for item in row]
print(flattened)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 복잡한 조건은 일반 for 루프가 더 읽기 쉬움
# 좋지 않은 예
bad_comprehension = [x for x in range(100) if x % 2 == 0 and x % 3 == 0 and x > 10]
```

### 딕셔너리 컴프리헨션
- **핵심 개념**: 설정 병합, 변환 처리
- **실무 활용**: 설정 파일 처리, 데이터 변환
- **면접 포인트**: 언제 사용하는지

```python
# 딕셔너리 컴프리헨션
words = ['apple', 'banana', 'cherry']
word_lengths = {word: len(word) for word in words}
print(word_lengths)  # {'apple': 5, 'banana': 6, 'cherry': 6}

# 조건부 딕셔너리 컴프리헨션
scores = {'Alice': 85, 'Bob': 92, 'Charlie': 78}
passed = {name: score for name, score in scores.items() if score >= 80}
print(passed)  # {'Alice': 85, 'Bob': 92}

# 설정 병합
default_config = {'host': 'localhost', 'port': 8080}
user_config = {'port': 9000, 'debug': True}
merged_config = {**default_config, **user_config}
print(merged_config)  # {'host': 'localhost', 'port': 9000, 'debug': True}
```

### set, dict 기본 메서드
- **핵심 개념**: 예외 없는 조회, 병합 시 중요
- **실무 활용**: 안전한 데이터 접근, 설정 관리
- **면접 포인트**: 각 메서드의 특징과 사용 시기

```python
# dict 메서드
config = {'host': 'localhost', 'port': 8080}

# get: 키가 없어도 에러 발생 안함
host = config.get('host', '127.0.0.1')  # 기본값 제공
database = config.get('database')        # None 반환

# setdefault: 키가 없으면 설정
config.setdefault('timeout', 30)
config.setdefault('host', 'new_host')    # 이미 있으면 변경 안함

# update: 여러 키-값 쌍 추가
config.update({'debug': True, 'log_level': 'INFO'})

# items: 키-값 쌍 반복
for key, value in config.items():
    print(f"{key}: {value}")

# set 메서드
set1 = {1, 2, 3}
set2 = {3, 4, 5}

union = set1.union(set2)        # 합집합
intersection = set1 & set2      # 교집합 (연산자 사용)
difference = set1 - set2        # 차집합
```

### any, all
- **핵심 개념**: 조건식 간소화
- **실무 활용**: 데이터 검증, 조건 확인
- **면접 포인트**: 성능과 가독성

```python
# any: 하나라도 True면 True
numbers = [1, 2, 3, 4, 5]
has_even = any(x % 2 == 0 for x in numbers)  # True
has_negative = any(x < 0 for x in numbers)    # False

# all: 모든 것이 True여야 True
all_positive = all(x > 0 for x in numbers)    # True
all_even = all(x % 2 == 0 for x in numbers)   # False

# 실무 활용: 데이터 검증
def validate_user_data(data):
    required_fields = ['name', 'email', 'age']
    return all(field in data for field in required_fields)

# 성능 최적화: 제너레이터 표현식 사용
# 리스트 컴프리헨션 대신 제너레이터 표현식으로 메모리 절약
```

### collections 모듈 활용
- **핵심 개념**: 빈도수 처리, 그룹핑
- **실무 활용**: 데이터 분석, 로그 처리
- **면접 포인트**: 각 클래스의 특징과 사용법

```python
from collections import defaultdict, Counter, namedtuple

# defaultdict: 기본값이 있는 딕셔너리
word_count = defaultdict(int)
words = ['apple', 'banana', 'apple', 'cherry', 'banana', 'apple']

for word in words:
    word_count[word] += 1  # KeyError 발생 안함

print(dict(word_count))  # {'apple': 3, 'banana': 2, 'cherry': 1}

# Counter: 빈도수 계산
word_counter = Counter(words)
print(word_counter.most_common(2))  # [('apple', 3), ('banana', 2)]

# namedtuple: 필드가 있는 튜플
User = namedtuple('User', ['name', 'age', 'email'])
user = User('Alice', 25, 'alice@example.com')
print(user.name)  # Alice
print(user.age)   # 25
```

## 10. 의존성 관리와 가상환경

### 가상환경 (Virtual Environment)
```python
# 가상환경 생성 및 활성화
# 1. 가상환경 생성
python -m venv myenv

# 2. 가상환경 활성화 (Windows)
myenv\Scripts\activate

# 3. 가상환경 활성화 (macOS/Linux)
source myenv/bin/activate

# 4. 가상환경 비활성화
deactivate

# 가상환경 확인
import sys
print(sys.executable)  # 가상환경의 Python 경로
print(sys.path)        # Python 경로 목록
```

### pip과 의존성 관리
```python
# 기본 패키지 설치
pip install requests
pip install fastapi[all]  # extra dependencies 포함

# 특정 버전 설치
pip install django==4.2.0
pip install "requests>=2.25.0,<3.0.0"

# 개발 의존성 설치
pip install pytest --dev
pip install black --dev

# requirements.txt 생성
pip freeze > requirements.txt

# requirements.txt에서 설치
pip install -r requirements.txt

# 의존성 업그레이드
pip install --upgrade requests
pip install --upgrade -r requirements.txt
```

### 고급 의존성 관리 도구
```python
# pip-tools 사용
# 1. requirements.in 파일 생성
# requirements.in
fastapi>=0.100.0
sqlalchemy>=2.0.0
pydantic>=2.0.0

# 2. requirements.txt 생성
pip-compile requirements.in

# 3. 설치
pip-sync requirements.txt

# Poetry 사용 (현대적인 의존성 관리)
# pyproject.toml
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = ""

[tool.poetry.dependencies]
python = "^3.8"
fastapi = "^0.100.0"
sqlalchemy = "^2.0.0"

[tool.poetry.dev-dependencies]
pytest = "^7.0.0"
black = "^23.0.0"

# Poetry 명령어
# poetry install          # 의존성 설치
# poetry add fastapi     # 패키지 추가
# poetry add --dev pytest # 개발 의존성 추가
# poetry update          # 의존성 업데이트
```

### 의존성 충돌 해결
```python
# 의존성 트리 확인
pip install pipdeptree
pipdeptree

# 특정 패키지의 의존성 확인
pipdeptree -p requests

# 의존성 충돌 해결 전략
# 1. 버전 범위 조정
# requirements.in
requests>=2.25.0,<3.0.0
urllib3<2.0.0  # requests와 호환되는 버전

# 2. 가상환경 분리
# 프로젝트별로 독립적인 가상환경 사용

# 3. Docker 사용
# FROM python:3.11-slim
# COPY requirements.txt .
# RUN pip install -r requirements.txt
```

## 11. 로깅과 모니터링

### 로깅 라이브러리 활용 (traceloggerx)

#### traceloggerx - 고급 추적 로깅 (PyPI 기반)
```python
# traceloggerx 설치: pip install traceloggerx
try:
    from traceloggerx import TraceLogger, TraceConfig
    from traceloggerx.handlers import FileHandler, ConsoleHandler
    from traceloggerx.formatters import JSONFormatter, TextFormatter
    
    # TraceLogger 설정
    config = TraceConfig(
        app_name="my_backend_app",
        version="1.0.0",
        environment="production",
        log_level="INFO"
    )
    
    # 로거 생성
    logger = TraceLogger("main", config)
    
    # 핸들러 추가
    console_handler = ConsoleHandler(
        formatter=TextFormatter(
            format_string="{timestamp} | {level} | {logger_name} | {message} | {extra_fields}"
        )
    )
    logger.add_handler(console_handler)
    
    # 파일 핸들러 (JSON 형식)
    file_handler = FileHandler(
        filename="logs/trace_{date}.log",
        formatter=JSONFormatter(),
        rotation="daily",
        retention=30
    )
    logger.add_handler(file_handler)
    
    # 추적 로깅 사용
    def process_payment(payment_id: str, amount: float, user_id: str):
        """결제 처리 함수"""
        # 트랜잭션 시작
        with logger.trace("payment_processing", 
                         payment_id=payment_id, 
                         amount=amount, 
                         user_id=user_id) as trace:
            
            logger.info("결제 처리 시작", 
                       payment_id=payment_id, 
                       amount=amount)
            
            try:
                # 결제 검증
                trace.add_event("payment_validation", status="started")
                if amount <= 0:
                    raise ValueError("결제 금액은 0보다 커야 합니다")
                
                # 결제 처리
                trace.add_event("payment_processing", status="started")
                # 실제 결제 로직...
                
                # 성공 로그
                trace.add_event("payment_success", status="completed")
                logger.info("결제 처리 완료", 
                           payment_id=payment_id, 
                           status="success")
                
                return True
                
            except Exception as e:
                # 에러 로그
                trace.add_event("payment_failed", 
                               error=str(e), 
                               status="failed")
                logger.error("결제 처리 실패", 
                            payment_id=payment_id, 
                            error=str(e), 
                            exc_info=True)
                return False
    
    # 사용 예시
    process_payment("PAY-001", 50000, "USER-456")
    
except ImportError:
    # traceloggerx가 설치되지 않은 경우 대체 구현
    import logging
    import json
    from datetime import datetime
    
    class TraceLogger:
        """간단한 추적 로거 구현"""
        
        def __init__(self, name, config=None):
            self.logger = logging.getLogger(name)
            self.config = config or {}
        
        def info(self, message, **kwargs):
            self.logger.info(f"{message} | {json.dumps(kwargs)}")
        
        def error(self, message, **kwargs):
            self.logger.error(f"{message} | {json.dumps(kwargs)}")
        
        def trace(self, operation, **kwargs):
            return TraceContext(self, operation, **kwargs)
    
    class TraceContext:
        """트랜잭션 컨텍스트 매니저"""
        
        def __init__(self, logger, operation, **kwargs):
            self.logger = logger
            self.operation = operation
            self.kwargs = kwargs
            self.events = []
        
        def __enter__(self):
            self.logger.info(f"트랜잭션 시작: {self.operation}", **self.kwargs)
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                self.logger.error(f"트랜잭션 실패: {self.operation}", 
                                 error=str(exc_val), **self.kwargs)
            else:
                self.logger.info(f"트랜잭션 완료: {self.operation}", **self.kwargs)
        
        def add_event(self, event_name, **kwargs):
            self.events.append({"event": event_name, "timestamp": datetime.now().isoformat(), **kwargs})
    
    # 대체 구현 사용
    logger = TraceLogger("main")
    
    def process_payment(payment_id: str, amount: float, user_id: str):
        """결제 처리 함수 (대체 구현)"""
        with logger.trace("payment_processing", 
                         payment_id=payment_id, 
                         amount=amount, 
                         user_id=user_id):
            
            logger.info("결제 처리 시작", 
                       payment_id=payment_id, 
                       amount=amount)
            
            try:
                if amount <= 0:
                    raise ValueError("결제 금액은 0보다 커야 합니다")
                
                logger.info("결제 처리 완료", 
                           payment_id=payment_id, 
                           status="success")
                return True
                
            except Exception as e:
                logger.error("결제 처리 실패", 
                            payment_id=payment_id, 
                            error=str(e))
                return False
    
    # 사용 예시
    process_payment("PAY-001", 50000, "USER-456")
```

### 구조화된 로깅과 모니터링

#### 표준 로깅 모듈 고급 활용
```python
import json
import logging
import logging.handlers
from typing import Any, Dict
from datetime import datetime
import os

class StructuredFormatter(logging.Formatter):
    """구조화된 JSON 로그 포맷터"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.logger_name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': record.process,
            'thread_id': record.thread
        }
        
        # 추가 필드가 있으면 포함
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # 예외 정보가 있으면 포함
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

# 고급 로깅 설정
def setup_advanced_logging(log_level=logging.INFO, log_dir="logs"):
    """고급 로깅 설정"""
    
    # 로그 디렉토리 생성
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 1. 콘솔 핸들러 (컬러 출력)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 2. 일반 로그 파일 (일별 로테이션)
    general_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    general_handler.setLevel(log_level)
    general_handler.setFormatter(console_formatter)
    root_logger.addHandler(general_handler)
    
    # 3. 에러 로그 파일 (에러만)
    error_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(log_dir, "error.log"),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(console_formatter)
    root_logger.addHandler(error_handler)
    
    # 4. JSON 로그 파일 (구조화된 로그)
    json_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(log_dir, "structured.log"),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    json_handler.setLevel(log_level)
    json_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(json_handler)
    
    return root_logger

# 컨텍스트 로깅
def log_with_context(message: str, level: str = "INFO", **extra_fields):
    """컨텍스트 정보와 함께 로깅"""
    logger = logging.getLogger()
    
    # 로그 레코드에 추가 필드 설정
    record = logger.makeRecord(
        logger.name, getattr(logging, level), 
        "", 0, message, (), None
    )
    record.extra_fields = extra_fields
    
    logger.handle(record)

# 로깅 데코레이터 (표준 로깅)
def advanced_logger(func):
    """고급 로깅 데코레이터"""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        # 함수 시작 로그
        start_time = datetime.now()
        logger.info(
            f"함수 시작: {func.__name__}",
            extra={
                'extra_fields': {
                    'function_name': func.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys()),
                    'start_time': start_time.isoformat()
                }
            }
        )
        
        try:
            result = func(*args, **kwargs)
            
            # 함수 완료 로그
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            logger.info(
                f"함수 완료: {func.__name__}",
                extra={
                    'extra_fields': {
                        'function_name': func.__name__,
                        'execution_time': execution_time,
                        'end_time': end_time.isoformat(),
                        'result_type': type(result).__name__
                    }
                }
            )
            return result
            
        except Exception as e:
            # 에러 로그
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            logger.error(
                f"함수 에러: {func.__name__}",
                extra={
                    'extra_fields': {
                        'function_name': func.__name__,
                        'execution_time': execution_time,
                        'end_time': end_time.isoformat(),
                        'error_type': type(e).__name__,
                        'error_message': str(e)
                    }
                },
                exc_info=True
            )
            raise
    
    return wrapper

# 사용 예시
@advanced_logger
def process_user_registration(user_data: dict) -> bool:
    """사용자 등록 처리"""
    logger = logging.getLogger(__name__)
    
    logger.info("사용자 등록 시작", 
                extra={'extra_fields': {'user_email': user_data.get('email')}})
    
    try:
        # 사용자 데이터 검증
        if not user_data.get('email'):
            raise ValueError("이메일은 필수입니다")
        
        # 사용자 등록 로직...
        logger.info("사용자 등록 완료", 
                    extra={'extra_fields': {'user_email': user_data.get('email')}})
        return True
        
    except Exception as e:
        logger.error("사용자 등록 실패", 
                     extra={'extra_fields': {'user_email': user_data.get('email')}})
        return False

# 로깅 설정 및 테스트
if __name__ == "__main__":
    # 고급 로깅 설정
    setup_advanced_logging(log_level=logging.DEBUG)
    
    # 컨텍스트 로깅 테스트
    log_with_context(
        "사용자 로그인 시도",
        level="INFO",
        user_id=123,
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0...",
        session_id="sess_abc123"
    )
    
    # 함수 로깅 테스트
    process_user_registration({"email": "test@example.com", "name": "테스트"})
    process_user_registration({"name": "테스트"})  # 에러 케이스
```

## 12. 날짜/시간 처리와 표준 라이브러리

### datetime 모듈 실무 활용
```python
from datetime import datetime, timedelta, timezone
import pytz

# 현재 시간과 시간대 처리
def get_current_time():
    """현재 시간을 여러 형식으로 반환"""
    # UTC 시간
    utc_now = datetime.utcnow()
    
    # 한국 시간 (pytz 사용)
    korea_tz = pytz.timezone('Asia/Seoul')
    korea_now = datetime.now(korea_tz)
    
    # 시스템 로컬 시간
    local_now = datetime.now()
    
    return {
        'utc': utc_now,
        'korea': korea_now,
        'local': local_now
    }

# 시간 파싱과 포맷팅
def parse_and_format_dates():
    """다양한 날짜 형식 파싱과 포맷팅"""
    
    # 문자열에서 날짜 파싱
    date_str = "2024-01-15 14:30:00"
    parsed_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    
    # ISO 형식으로 포맷팅
    iso_format = parsed_date.isoformat()
    
    # 사용자 정의 형식
    custom_format = parsed_date.strftime("%Y년 %m월 %d일 %H시 %M분")
    
    # 상대적 시간 표현
    now = datetime.now()
    time_diff = now - parsed_date
    
    return {
        'parsed': parsed_date,
        'iso': iso_format,
        'custom': custom_format,
        'diff_days': time_diff.days,
        'diff_seconds': time_diff.total_seconds()
    }

# 시간 계산과 조작
def time_calculations():
    """시간 계산과 조작 예시"""
    
    now = datetime.now()
    
    # 미래/과거 시간 계산
    tomorrow = now + timedelta(days=1)
    next_week = now + timedelta(weeks=1)
    last_month = now - timedelta(days=30)
    
    # 시간 범위 생성
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1) - timedelta(microseconds=1)
    
    # 주의 시작 (월요일)
    days_since_monday = now.weekday()
    start_of_week = now - timedelta(days=days_since_monday)
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    
    return {
        'tomorrow': tomorrow,
        'next_week': next_week,
        'last_month': last_month,
        'start_of_day': start_of_day,
        'end_of_day': end_of_day,
        'start_of_week': start_of_week
    }

# 실무 활용 예시
def schedule_reminder(user_id: int, reminder_time: datetime, message: str):
    """사용자에게 리마인더를 스케줄링"""
    
    now = datetime.now()
    
    if reminder_time <= now:
        raise ValueError("리마인더 시간은 현재 시간보다 미래여야 합니다")
    
    # 리마인더까지 남은 시간 계산
    time_until_reminder = reminder_time - now
    
    # 시간 단위별 분해
    days = time_until_reminder.days
    hours, remainder = divmod(time_until_reminder.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    print(f"리마인더 스케줄됨: {message}")
    print(f"남은 시간: {days}일 {hours}시간 {minutes}분")
    
    return {
        'user_id': user_id,
        'reminder_time': reminder_time,
        'message': message,
        'time_until': time_until_reminder
    }

# 사용 예시
if __name__ == "__main__":
    # 현재 시간 확인
    times = get_current_time()
    print(f"한국 시간: {times['korea']}")
    
    # 날짜 파싱 테스트
    date_info = parse_and_format_dates()
    print(f"사용자 형식: {date_info['custom']}")
    
    # 시간 계산 테스트
    calc_info = time_calculations()
    print(f"내일: {calc_info['tomorrow']}")
    
    # 리마인더 스케줄링
    tomorrow_9am = datetime.now() + timedelta(days=1)
    tomorrow_9am = tomorrow_9am.replace(hour=9, minute=0, second=0, microsecond=0)
    
    reminder = schedule_reminder(1, tomorrow_9am, "회의 준비하세요!")
```

### 표준 라이브러리 모듈들
```python
import os
import pathlib
import itertools
import re
import math
import json
import uuid
from collections import defaultdict, Counter, namedtuple

# os 모듈 - 운영체제 인터페이스
def os_operations():
    """운영체제 관련 작업들"""
    
    # 환경 변수
    home_dir = os.environ.get('HOME', os.environ.get('USERPROFILE'))
    python_path = os.environ.get('PYTHONPATH')
    
    # 파일/디렉토리 작업
    current_dir = os.getcwd()
    files = os.listdir(current_dir)
    
    # 경로 조작
    file_path = os.path.join(current_dir, 'test.txt')
    file_exists = os.path.exists(file_path)
    
    return {
        'home': home_dir,
        'python_path': python_path,
        'current_dir': current_dir,
        'files': files,
        'file_path': file_path,
        'exists': file_exists
    }

# pathlib - 현대적인 경로 처리
def pathlib_operations():
    """pathlib을 사용한 경로 처리"""
    
    # 경로 객체 생성
    current_path = pathlib.Path.cwd()
    home_path = pathlib.Path.home()
    
    # 경로 조작
    config_dir = current_path / 'config'
    config_file = config_dir / 'settings.yaml'
    
    # 경로 정보
    path_info = {
        'current': str(current_path),
        'home': str(home_path),
        'config_dir': str(config_dir),
        'config_file': str(config_file),
        'is_file': config_file.is_file(),
        'is_dir': config_dir.is_dir(),
        'parent': str(current_path.parent),
        'name': current_path.name,
        'suffix': current_path.suffix
    }
    
    return path_info

# itertools - 이터레이터 도구
def itertools_examples():
    """itertools 모듈 활용 예시"""
    
    numbers = [1, 2, 3, 4, 5]
    
    # 무한 이터레이터
    from itertools import count, cycle, repeat
    
    # 카운터 (무한 증가)
    counter = count(1, 2)  # 1부터 2씩 증가
    first_five = list(itertools.islice(counter, 5))  # [1, 3, 5, 7, 9]
    
    # 순환
    cycler = cycle(['A', 'B', 'C'])
    cycle_five = list(itertools.islice(cycler, 5))  # ['A', 'B', 'C', 'A', 'B']
    
    # 반복
    repeater = repeat('Hello', 3)  # 'Hello'를 3번 반복
    repeat_list = list(repeater)  # ['Hello', 'Hello', 'Hello']
    
    # 조합과 순열
    from itertools import combinations, permutations
    
    combos = list(combinations(numbers, 2))  # 2개 조합
    perms = list(permutations(numbers, 2))   # 2개 순열
    
    return {
        'counter': first_five,
        'cycle': cycle_five,
        'repeat': repeat_list,
        'combinations': combos,
        'permutations': perms
    }

# re 모듈 - 정규표현식
def regex_examples():
    """정규표현식 활용 예시"""
    
    # 이메일 검증
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    email_regex = re.compile(email_pattern)
    
    test_emails = [
        'user@example.com',
        'invalid-email',
        'test.email@domain.co.kr'
    ]
    
    email_results = {
        email: bool(email_regex.match(email)) 
        for email in test_emails
    }
    
    # 전화번호 검증 (한국)
    phone_pattern = r'^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$'
    phone_regex = re.compile(phone_pattern)
    
    test_phones = [
        '010-1234-5678',
        '01012345678',
        '02-123-4567'  # 일반전화
    ]
    
    phone_results = {
        phone: bool(phone_regex.match(phone)) 
        for phone in test_phones
    }
    
    # 문자열 치환
    text = "Hello World! This is a test."
    replaced = re.sub(r'\b\w+', lambda m: m.group().upper(), text)
    
    return {
        'emails': email_results,
        'phones': phone_results,
        'replaced_text': replaced
    }

# math 모듈 - 수학 함수
def math_examples():
    """수학 함수 활용 예시"""
    
    import math
    
    # 기본 수학 함수
    pi = math.pi
    e = math.e
    
    # 제곱근과 거듭제곱
    sqrt_16 = math.sqrt(16)
    pow_2_8 = math.pow(2, 8)
    
    # 삼각함수
    sin_30 = math.sin(math.radians(30))
    cos_60 = math.cos(math.radians(60))
    
    # 로그함수
    log_100 = math.log10(100)
    ln_e = math.log(math.e)
    
    # 올림/내림/반올림
    ceil_3_7 = math.ceil(3.7)
    floor_3_7 = math.floor(3.7)
    
    return {
        'pi': pi,
        'e': e,
        'sqrt_16': sqrt_16,
        'pow_2_8': pow_2_8,
        'sin_30': sin_30,
        'cos_60': cos_60,
        'log_100': log_100,
        'ln_e': ln_e,
        'ceil_3_7': ceil_3_7,
        'floor_3_7': floor_3_7
    }

# json 모듈 - JSON 처리
def json_examples():
    """JSON 처리 예시"""
    
    # Python 객체를 JSON으로 직렬화
    data = {
        'name': '김철수',
        'age': 25,
        'skills': ['Python', 'Django', 'PostgreSQL'],
        'active': True,
        'score': 95.5
    }
    
    json_string = json.dumps(data, ensure_ascii=False, indent=2)
    
    # JSON 파일로 저장
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # JSON 파일에서 읽기
    with open('data.json', 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    
    # JSON 문자열에서 파싱
    parsed_data = json.loads(json_string)
    
    return {
        'original': data,
        'json_string': json_string,
        'loaded': loaded_data,
        'parsed': parsed_data
    }

# uuid 모듈 - 고유 식별자
def uuid_examples():
    """UUID 생성 예시"""
    
    import uuid
    
    # 다양한 UUID 생성
    uuid1 = uuid.uuid1()  # 호스트 ID, 시퀀스 번호, 현재 시간 기반
    uuid4 = uuid.uuid4()  # 랜덤 생성
    uuid5 = uuid.uuid5(uuid.NAMESPACE_DNS, 'example.com')  # 네임스페이스 기반
    
    # 문자열 변환
    uuid_str = str(uuid4)
    uuid_from_str = uuid.UUID(uuid_str)
    
    return {
        'uuid1': str(uuid1),
        'uuid4': str(uuid4),
        'uuid5': str(uuid5),
        'uuid_str': uuid_str,
        'uuid_from_str': str(uuid_from_str)
    }

# 사용 예시
if __name__ == "__main__":
    print("=== OS 작업 ===")
    os_info = os_operations()
    print(f"현재 디렉토리: {os_info['current_dir']}")
    
    print("\n=== Pathlib 작업 ===")
    path_info = pathlib_operations()
    print(f"설정 파일 경로: {path_info['config_file']}")
    
    print("\n=== Itertools 예시 ===")
    itertools_info = itertools_examples()
    print(f"조합: {itertools_info['combinations']}")
    
    print("\n=== 정규표현식 예시 ===")
    regex_info = regex_examples()
    print(f"이메일 검증: {regex_info['emails']}")
    
    print("\n=== 수학 함수 예시 ===")
    math_info = math_examples()
    print(f"π: {math_info['pi']}")
    
    print("\n=== JSON 처리 예시 ===")
    json_info = json_examples()
    print(f"JSON 문자열: {json_info['json_string'][:50]}...")
    
    print("\n=== UUID 예시 ===")
    uuid_info = uuid_examples()
    print(f"UUID4: {uuid_info['uuid4']}")
```

## 13. 보너스: 실무에 자주 나오는 고급 문법

### contextlib.contextmanager
- **핵심 개념**: with 구문을 커스터마이징할 때
- **실무 활용**: 복잡한 컨텍스트 매니저 구현
- **면접 포인트**: 언제 사용하는지

```python
from contextlib import contextmanager
import time

@contextmanager
def performance_timer(name):
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print(f"{name} 실행 시간: {end - start:.2f}초")

# 사용
with performance_timer("데이터 처리"):
    # 시간을 측정할 작업
    time.sleep(1)
```

### dataclasses.dataclass
- **핵심 개념**: 설정 객체, DTO 만들 때 매우 유용
- **실무 활용**: API 응답, 설정 관리
- **면접 포인트**: 기존 클래스와의 차이점

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class User:
    name: str
    age: int
    email: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def is_adult(self) -> bool:
        return self.age >= 18

# 자동으로 __init__, __repr__, __eq__ 등 생성
user = User("Alice", 25, "alice@example.com", ["vip", "active"])
print(user)  # User(name='Alice', age=25, email='alice@example.com', tags=['vip', 'active'])
```

### functools 모듈
- **핵심 개념**: 캐싱, 데코레이터 작성할 때
- **실무 활용**: 성능 최적화, 함수 조합
- **면접 포인트**: 각 함수의 특징과 사용법

```python
from functools import lru_cache, wraps, partial

# lru_cache: 함수 결과 캐싱
@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# wraps: 데코레이터에서 원본 함수 정보 보존
def log_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"함수 {func.__name__} 호출")
        return func(*args, **kwargs)
    return wrapper

# partial: 함수의 일부 인자 고정
from functools import partial
def greet(greeting, name):
    return f"{greeting}, {name}!"

hello = partial(greet, "Hello")
print(hello("Alice"))  # Hello, Alice!
```

### typing 모듈
- **핵심 개념**: 타입 힌트, 문서화, 테스트 시 명확성
- **실무 활용**: 코드 가독성, IDE 지원, 타입 검사
- **면접 포인트**: 각 타입의 특징과 사용법

```python
from typing import List, Dict, Optional, Union, Callable, TypeVar, Generic

# 기본 타입 힌트
def process_users(users: List[Dict[str, Union[str, int]]]) -> List[str]:
    return [user['name'] for user in users if user.get('age', 0) >= 18]

# Optional: None 가능한 값
def get_user(user_id: int) -> Optional[Dict[str, str]]:
    # 사용자를 찾지 못하면 None 반환
    pass

# Callable: 함수 타입
def apply_operation(func: Callable[[int], int], value: int) -> int:
    return func(value)

# Generic: 제네릭 타입
T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: List[T] = []
    
    def push(self, item: T) -> None:
        self.items.append(item)
    
    def pop(self) -> T:
        return self.items.pop()

# TypedDict: 구조화된 딕셔너리
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int
    email: Optional[str]
```

### __slots__
- **핵심 개념**: 메모리 절감 (많은 객체 생성 시 유리)
- **실무 활용**: 대량 객체 생성, 메모리 최적화
- **면접 포인트**: 언제 사용하고 언제 사용하지 말아야 하는지

```python
class UserWithSlots:
    __slots__ = ['name', 'age', 'email']
    
    def __init__(self, name: str, age: int, email: str):
        self.name = name
        self.age = age
        self.email = email

class UserWithoutSlots:
    def __init__(self, name: str, age: int, email: str):
        self.name = name
        self.age = age
        self.email = email

# 메모리 사용량 비교
import sys
user1 = UserWithSlots("Alice", 25, "alice@example.com")
user2 = UserWithoutSlots("Bob", 30, "bob@example.com")

print(f"With slots: {sys.getsizeof(user1)} bytes")
print(f"Without slots: {sys.getsizeof(user2)} bytes")

# 주의: 동적 속성 추가 불가
# user1.new_field = "value"  # AttributeError 발생
```

## 10. 이터러블과 이터레이터 심화

### 커스텀 이터러블 구현
```python
class NumberRange:
    def __init__(self, start, end, step=1):
        self.start = start
        self.end = end
        self.step = step
    
    def __iter__(self):
        return NumberIterator(self.start, self.end, self.step)

class NumberIterator:
    def __init__(self, start, end, step):
        self.current = start
        self.end = end
        self.step = step
    
    def __next__(self):
        if self.current >= self.end:
            raise StopIteration
        result = self.current
        self.current += self.step
        return result

# 사용
for num in NumberRange(1, 10, 2):
    print(num)  # 1, 3, 5, 7, 9
```

### 제너레이터와 이터러블의 조합
```python
def fibonacci_generator(n):
    """피보나치 수열 제너레이터"""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

class FibonacciIterable:
    def __init__(self, n):
        self.n = n
    
    def __iter__(self):
        return fibonacci_generator(self.n)

# 제너레이터와 이터러블 클래스 모두 사용 가능
fib_gen = fibonacci_generator(10)
fib_iter = FibonacciIterable(10)

print(list(fib_gen))   # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
print(list(fib_iter))  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### 딕셔너리 컴프리헨션
```python
# 딕셔너리 컴프리헨션
words = ['apple', 'banana', 'cherry']
word_lengths = {word: len(word) for word in words}
print(word_lengths)  # {'apple': 5, 'banana': 6, 'cherry': 6}

# 조건부 딕셔너리 컴프리헨션
scores = {'Alice': 85, 'Bob': 92, 'Charlie': 78}
passed = {name: score for name, score in scores.items() if score >= 80}
print(passed)  # {'Alice': 85, 'Bob': 92}
```

### 이터레이터와 이터러블
```python
class NumberRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end
    
    def __iter__(self):
        return NumberIterator(self.start, self.end)

class NumberIterator:
    def __init__(self, start, end):
        self.current = start
        self.end = end
    
    def __next__(self):
        if self.current >= self.end:
            raise StopIteration
        result = self.current
        self.current += 1
        return result

# 사용
for num in NumberRange(1, 5):
    print(num)  # 1, 2, 3, 4
```

## 11. 함수형 프로그래밍 심화

### 고차 함수와 함수 조합
```python
from functools import reduce
from typing import Callable, TypeVar, List

T = TypeVar('T')
U = TypeVar('U')

def compose(*functions: Callable) -> Callable:
    """함수들을 조합하는 고차 함수"""
    def inner(arg):
        result = arg
        for func in reversed(functions):
            result = func(result)
        return result
    return inner

def pipe(*functions: Callable) -> Callable:
    """함수들을 파이프라인으로 연결"""
    def inner(arg):
        result = arg
        for func in functions:
            result = func(result)
        return result
    return inner

# 사용 예시
def add_one(x: int) -> int:
    return x + 1

def multiply_by_two(x: int) -> int:
    return x * 2

def square(x: int) -> int:
    return x ** 2

# 함수 조합
combined = compose(square, multiply_by_two, add_one)
piped = pipe(add_one, multiply_by_two, square)

print(combined(3))  # ((3 + 1) * 2)² = 64
print(piped(3))     # ((3 + 1) * 2)² = 64
```

### 모나드와 함수형 에러 처리
```python
from typing import TypeVar, Generic, Callable, Optional
from dataclasses import dataclass

T = TypeVar('T')
U = TypeVar('U')

@dataclass
class Result(Generic[T]):
    """함수형 에러 처리를 위한 Result 모나드"""
    value: Optional[T] = None
    error: Optional[Exception] = None
    
    def is_success(self) -> bool:
        return self.error is None
    
    def map(self, func: Callable[[T], U]) -> 'Result[U]':
        """성공 시에만 함수 적용"""
        if self.is_success():
            try:
                return Result(value=func(self.value))
            except Exception as e:
                return Result(error=e)
        return Result(error=self.error)
    
    def flat_map(self, func: Callable[[T], 'Result[U]']) -> 'Result[U]':
        """중첩된 Result를 평탄화"""
        if self.is_success():
            return func(self.value)
        return Result(error=self.error)
    
    def get_or_else(self, default: T) -> T:
        """값이 없으면 기본값 반환"""
        return self.value if self.is_success() else default

# 사용 예시
def safe_divide(a: float, b: float) -> Result[float]:
    try:
        return Result(value=a / b)
    except ZeroDivisionError as e:
        return Result(error=e)

def safe_sqrt(x: float) -> Result[float]:
    try:
        import math
        if x < 0:
            raise ValueError("음수는 제곱근을 가질 수 없습니다")
        return Result(value=math.sqrt(x))
    except Exception as e:
        return Result(error=e)

# 체이닝
result = (safe_divide(10, 2)
          .flat_map(safe_sqrt)
          .map(lambda x: x * 2))

if result.is_success():
    print(f"결과: {result.value}")
else:
    print(f"에러: {result.error}")
```

### 함수형 프로그래밍 실무 활용
```python
from typing import List, Callable
from functools import reduce

# 실무에서 자주 사용하는 함수형 패턴
def process_user_data(users: List[dict]) -> dict:
    """사용자 데이터를 함수형으로 처리"""
    
    # 1. 필터링: 활성 사용자만 선택
    active_users = list(filter(lambda u: u.get('active', False), users))
    
    # 2. 매핑: 필요한 정보만 추출
    user_summaries = list(map(lambda u: {
        'id': u['id'],
        'name': u['name'],
        'age': u.get('age', 0)
    }, active_users))
    
    # 3. 집계: 통계 계산
    total_age = reduce(lambda acc, u: acc + u['age'], user_summaries, 0)
    avg_age = total_age / len(user_summaries) if user_summaries else 0
    
    return {
        'total_users': len(user_summaries),
        'average_age': avg_age,
        'users': user_summaries
    }

# 사용 예시
users = [
    {'id': 1, 'name': '김철수', 'age': 25, 'active': True},
    {'id': 2, 'name': '이영희', 'age': 30, 'active': False},
    {'id': 3, 'name': '박민수', 'age': 28, 'active': True},
    {'id': 4, 'name': '최지영', 'age': 22, 'active': True}
]

result = process_user_data(users)
print(f"활성 사용자: {result['total_users']}명")
print(f"평균 나이: {result['average_age']:.1f}세")
```

## 12. 타입 힌트

### 기본 타입 힌트
```python
from typing import List, Dict, Optional, Union, Callable

def process_user(
    name: str,
    age: int,
    scores: List[float],
    metadata: Optional[Dict[str, str]] = None
) -> str:
    result = f"User: {name}, Age: {age}, Avg Score: {sum(scores)/len(scores):.2f}"
    if metadata:
        result += f", Metadata: {metadata}"
    return result

# 사용
user_info = process_user(
    name="Alice",
    age=25,
    scores=[85.5, 92.0, 78.5],
    metadata={"city": "Seoul"}
)
print(user_info)
```

### 제네릭 타입
```python
from typing import TypeVar, Generic

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self):
        self.items: List[T] = []
    
    def push(self, item: T) -> None:
        self.items.append(item)
    
    def pop(self) -> T:
        return self.items.pop()
    
    def is_empty(self) -> bool:
        return len(self.items) == 0

# 사용
int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)
print(int_stack.pop())  # 2
```

## 13. 실무에서 자주 사용하는 패턴

### 싱글톤 패턴
```python
class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.database_url = "localhost:5432"
            self.api_key = "secret_key"
            self._initialized = True

# 항상 같은 인스턴스
config1 = Config()
config2 = Config()
print(config1 is config2)  # True
```

### 팩토리 패턴
```python
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def connect(self):
        pass

class PostgreSQL(Database):
    def connect(self):
        return "PostgreSQL 연결됨"

class MySQL(Database):
    def connect(self):
        return "MySQL 연결됨"

class DatabaseFactory:
    @staticmethod
    def create_database(db_type: str) -> Database:
        if db_type == "postgresql":
            return PostgreSQL()
        elif db_type == "mysql":
            return MySQL()
        else:
            raise ValueError(f"지원하지 않는 데이터베이스: {db_type}")

# 사용
db = DatabaseFactory.create_database("postgresql")
print(db.connect())
```

## 15. 면접 준비 학습 순서

### 🎯 **권장 암기/복습 순서**

1. **1단계: 기본 문법 (1-2주)**
   - `with` 구문, `yield`, `@staticmethod/@classmethod/@property`
   - `*args`, `**kwargs`, `lambda`, `enumerate`, `zip`
   - `is` vs `==`, `copy` vs `deepcopy`
   - 예외 처리, 변수 스코프

2. **2단계: 객체지향 (1주)**
   - 클래스와 객체, 상속과 다형성
   - 매직 메서드 (`__init__`, `__new__`, `__str__`, `__repr__`)
   - 추상 클래스와 인터페이스

3. **3단계: 고급 문법 (1-2주)**
   - 제너레이터와 코루틴
   - 컨텍스트 매니저, 데코레이터
   - 비동기 프로그래밍 (`async/await`)

4. **4단계: 실무 활용 (1주)**
   - 컬렉션과 이터러블
   - 함수형 프로그래밍 (`map`, `filter`, `reduce`)
   - 타입 힌트와 제네릭

5. **5단계: 프로젝트 구조 (1주)**
   - 모듈과 패키지 구조
   - Import 구문과 의존성 관리
   - 가상환경과 pip/poetry

6. **6단계: 실무 도구 (1주)**
   - 로깅과 모니터링
   - 날짜/시간 처리
   - 표준 라이브러리 모듈들

7. **7단계: 심화 주제 (1주)**
   - 메모리 최적화 (`__slots__`)
   - 디자인 패턴 (Singleton, Factory)
   - 성능 최적화 기법

### 📝 **면접 질문 예시 (yield)**
```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

# → 언제 사용하나요?
# → 일반 함수와 어떻게 다른가요?
# → 실무에서 어디에 사용하나요?
# → 이것에 대해 물어보면 어떤 후속 질문이 나올까요?
```

### 🔍 **면접에서 자주 나오는 질문들**

**기본 문법**
- **yield**: "제너레이터를 언제 사용하나요? 메모리 효율성은 어떻게 되나요?"
- **with**: "컨텍스트 매니저를 직접 구현해본 적이 있나요?"
- **@property**: "getter/setter 대신 @property를 사용하는 이유는?"
- **copy vs deepcopy**: "얕은 복사와 깊은 복사의 차이점과 언제 사용하나요?"

**객체지향**
- **매직 메서드**: "`__init__`과 `__new__`의 차이점은? 언제 `__new__`를 오버라이드하나요?"
- **상속 vs 컴포지션**: "상속을 사용할 때 주의할 점은? 언제 컴포지션을 선택하나요?"
- **추상 클래스**: "추상 클래스와 인터페이스의 차이점은?"

**프로젝트 구조**
- **모듈/패키지**: "`__init__.py`의 역할은? 절대 import vs 상대 import의 차이점은?"
- **의존성 관리**: "requirements.txt와 poetry의 차이점은? 가상환경을 왜 사용하나요?"
- **로깅**: "print() 대신 로깅을 사용하는 이유는? 로그 레벨별로 어떻게 관리하나요?"

**실무 활용**
- **날짜/시간**: "시간대 처리는 어떻게 하나요? datetime vs pytz의 차이점은?"
- **표준 라이브러리**: "collections 모듈에서 자주 사용하는 것은? defaultdict vs dict의 차이점은?"
- **비동기**: "asyncio를 언제 사용하나요? 동기 vs 비동기 성능 차이는?"

### 💡 **실무 경험 연계 포인트**
- **성능 최적화**: 제너레이터, `__slots__`, 메모리 효율성
- **코드 품질**: 타입 힌트, 예외 처리, 가독성
- **설계 패턴**: 데코레이터, 컨텍스트 매니저, 팩토리 패턴
- **데이터 처리**: 컴프리헨션, collections 모듈, 함수형 프로그래밍

---

<details>
<summary>cf. reference</summary>

- 
</details> 