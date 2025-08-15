---
title: "파이썬 고급 문법 심화"
date: 2025-08-15
tags: ["python", "advanced", "grammar", "interview"]
---

# 파이썬 고급 문법 심화

> 파이썬 3년차 백엔드 개발자를 위한 심화 문법 가이드
> 
> 기본 문법을 마스터한 후 학습하는 고급 주제들

## 📚 **학습 대상**

- 파이썬 기본 문법을 완벽히 이해한 개발자
- 기술면접에서 고급 질문에 대응하고 싶은 개발자
- 실무에서 고성능, 고품질 코드를 작성하고 싶은 개발자
- 파이썬의 내부 동작 원리를 이해하고 싶은 개발자

---

## 1. 메타클래스와 클래스 팩토리

### 메타클래스 기본 개념
```python
class MetaLogger(type):
    """로깅 기능을 자동으로 추가하는 메타클래스"""
    
    def __new__(cls, name, bases, namespace):
        # 클래스 생성 시 로깅 메서드 자동 추가
        for key, value in namespace.items():
            if callable(value) and not key.startswith('_'):
                # 모든 public 메서드에 로깅 추가
                namespace[key] = cls.add_logging(value, key)
        
        return super().__new__(cls, name, bases, namespace)
    
    @staticmethod
    def add_logging(func, func_name):
        """함수에 로깅 기능 추가"""
        def wrapper(*args, **kwargs):
            print(f"[LOG] {func_name} 호출됨 - args: {args}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                print(f"[LOG] {func_name} 완료됨 - 결과: {result}")
                return result
            except Exception as e:
                print(f"[LOG] {func_name} 에러 발생 - {e}")
                raise
        return wrapper

# 메타클래스 사용
class UserService(metaclass=MetaLogger):
    def create_user(self, name: str, email: str) -> dict:
        return {"id": 1, "name": name, "email": email}
    
    def delete_user(self, user_id: int) -> bool:
        return True

# 자동으로 로깅 기능이 추가됨
service = UserService()
service.create_user("김철수", "kim@example.com")
```

### 클래스 팩토리 패턴
```python
class ClassFactory:
    """동적으로 클래스를 생성하는 팩토리"""
    
    @staticmethod
    def create_model_class(table_name: str, fields: dict):
        """데이터베이스 테이블에 대응하는 모델 클래스 생성"""
        
        # 클래스 네임스페이스 생성
        namespace = {
            '__module__': '__main__',
            '__doc__': f'Model class for table: {table_name}',
            'table_name': table_name,
            'fields': fields
        }
        
        # 각 필드에 대한 프로퍼티 추가
        for field_name, field_type in fields.items():
            namespace[f'_{field_name}'] = None
            
            def make_property(field):
                def getter(self):
                    return getattr(self, f'_{field}')
                
                def setter(self, value):
                    if not isinstance(value, field_type):
                        raise TypeError(f"{field}은 {field_type} 타입이어야 합니다")
                    setattr(self, f'_{field}', value)
                
                return property(getter, setter)
            
            namespace[field_name] = make_property(field_name)
        
        # __init__ 메서드 추가
        def __init__(self, **kwargs):
            for field_name in fields:
                if field_name in kwargs:
                    setattr(self, field_name, kwargs[field_name])
        
        namespace['__init__'] = __init__
        
        # 클래스 생성
        return type(f'{table_name.title()}Model', (), namespace)

# 사용 예시
UserModel = ClassFactory.create_model_class('users', {
    'id': int,
    'name': str,
    'email': str,
    'age': int
})

# 동적으로 생성된 클래스 사용
user = UserModel(id=1, name="김철수", email="kim@example.com", age=25)
print(f"사용자: {user.name}, 나이: {user.age}")
```

---

## 2. 고급 데코레이터와 메타프로그래밍

### 메타데코레이터와 체이닝
```python
from typing import Callable, TypeVar, Any
from functools import wraps

F = TypeVar('F', bound=Callable[..., Any])

def validate_input(*validators):
    """입력 검증을 위한 메타데코레이터"""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 모든 검증기 실행
            for validator in validators:
                validator(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_positive(*args):
    """양수 검증"""
    if any(arg <= 0 for arg in args if isinstance(arg, (int, float))):
        raise ValueError("모든 인자는 양수여야 합니다")

def check_string_length(max_length):
    """문자열 길이 검증"""
    def validator(*args):
        if any(len(str(arg)) > max_length for arg in args):
            raise ValueError(f"문자열 길이는 {max_length}를 초과할 수 없습니다")
    return validator

def check_type(expected_type):
    """타입 검증"""
    def validator(*args):
        if any(not isinstance(arg, expected_type) for arg in args):
            raise TypeError(f"모든 인자는 {expected_type} 타입이어야 합니다")
    return validator

# 복합 검증 데코레이터
@validate_input(
    check_positive,
    check_string_length(10),
    check_type((int, str))
)
def process_data(value: int, name: str):
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
    """설정 가능한 데코레이터 팩토리"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 로깅 설정
            if config.get('log', False):
                print(f"함수 {func.__name__} 호출됨")
            
            # 캐싱 설정
            if config.get('cache', False):
                cache_key = str(args) + str(kwargs)
                if not hasattr(wrapper, '_cache'):
                    wrapper._cache = {}
                if cache_key in wrapper._cache:
                    return wrapper._cache[cache_key]
                
                result = func(*args, **kwargs)
                wrapper._cache[cache_key] = result
                return result
            
            # 성능 측정 설정
            if config.get('profile', False):
                import time
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                print(f"{func.__name__} 실행 시간: {end_time - start_time:.4f}초")
                return result
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

@configurable_decorator(log=True, cache=True, profile=True)
def expensive_calculation(n):
    """비용이 큰 계산"""
    import time
    time.sleep(0.1)  # 계산 시뮬레이션
    return n * n

# 첫 번째 호출: 로그 + 계산 + 성능 측정
result1 = expensive_calculation(5)
# 두 번째 호출: 캐시된 결과 반환
result2 = expensive_calculation(5)
```

---

## 3. 고급 함수형 프로그래밍

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
    
    def on_success(self, func: Callable[[T], None]) -> 'Result[T]':
        """성공 시 콜백 실행"""
        if self.is_success():
            func(self.value)
        return self
    
    def on_error(self, func: Callable[[Exception], None]) -> 'Result[T]':
        """에러 시 콜백 실행"""
        if not self.is_success():
            func(self.error)
        return self

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

# 체이닝과 에러 처리
result = (safe_divide(10, 2)
          .flat_map(safe_sqrt)
          .map(lambda x: x * 2)
          .on_success(lambda x: print(f"계산 성공: {x}"))
          .on_error(lambda e: print(f"계산 실패: {e}")))

if result.is_success():
    print(f"최종 결과: {result.value}")
else:
    print(f"에러: {result.error}")
```

### 함수형 데이터 처리 파이프라인
```python
from typing import List, Callable, TypeVar, Iterator
from functools import reduce

T = TypeVar('T')
U = TypeVar('U')

class Pipeline:
    """함수형 데이터 처리 파이프라인"""
    
    def __init__(self, data: Iterator[T]):
        self.data = data
    
    def map(self, func: Callable[[T], U]) -> 'Pipeline[U]':
        """각 요소에 함수 적용"""
        return Pipeline(map(func, self.data))
    
    def filter(self, predicate: Callable[[T], bool]) -> 'Pipeline[T]':
        """조건에 맞는 요소만 선택"""
        return Pipeline(filter(predicate, self.data))
    
    def take(self, n: int) -> 'Pipeline[T]':
        """처음 n개 요소만 선택"""
        return Pipeline(self._take(n))
    
    def skip(self, n: int) -> 'Pipeline[T]':
        """처음 n개 요소 건너뛰기"""
        return Pipeline(self._skip(n))
    
    def reduce(self, func: Callable, initial=None) -> T:
        """누적 연산"""
        if initial is None:
            return reduce(func, self.data)
        return reduce(func, self.data, initial)
    
    def collect(self) -> List[T]:
        """결과 수집"""
        return list(self.data)
    
    def _take(self, n: int) -> Iterator[T]:
        """처음 n개 요소 반환"""
        for i, item in enumerate(self.data):
            if i >= n:
                break
            yield item
    
    def _skip(self, n: int) -> Iterator[T]:
        """처음 n개 요소 건너뛰기"""
        for i, item in enumerate(self.data):
            if i >= n:
                yield item

# 사용 예시
def fibonacci():
    """피보나치 수열 제너레이터"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# 파이프라인으로 피보나치 수열 처리
result = (Pipeline(fibonacci())
          .filter(lambda x: x % 2 == 0)  # 짝수만 선택
          .map(lambda x: x ** 2)         # 제곱
          .take(10)                      # 처음 10개
          .reduce(lambda acc, x: acc + x, 0))  # 합계

print(f"피보나치 짝수의 제곱 합 (처음 10개): {result}")
```

---

## 4. 고급 비동기 프로그래밍

### 비동기 제너레이터와 스트리밍
```python
import asyncio
import aiofiles
from typing import AsyncIterator

async def async_file_reader(file_path: str) -> AsyncIterator[str]:
    """비동기 파일 읽기 제너레이터"""
    async with aiofiles.open(file_path, 'r') as file:
        async for line in file:
            yield line.strip()

async def process_large_file(file_path: str) -> AsyncIterator[str]:
    """대용량 파일을 비동기로 처리"""
    async for line in async_file_reader(file_path):
        # 각 라인을 비동기로 처리
        processed = await process_line_async(line)
        yield processed

async def process_line_async(line: str) -> str:
    """라인을 비동기로 처리"""
    # 실제로는 복잡한 비동기 처리
    await asyncio.sleep(0.01)
    return f"처리됨: {line}"

async def main():
    """메인 함수"""
    file_path = 'large_file.txt'
    
    # 파일 처리 결과를 리스트로 수집
    results = []
    async for result in process_large_file(file_path):
        results.append(result)
        if len(results) >= 100:  # 처음 100개만 처리
            break
    
    print(f"처리된 라인 수: {len(results)}")

# 실행
# asyncio.run(main())
```

### 비동기 큐와 워커 패턴
```python
import asyncio
from asyncio import Queue
from typing import List, Optional
import random

class AsyncWorker:
    """비동기 워커 클래스"""
    
    def __init__(self, name: str, queue: Queue):
        self.name = name
        self.queue = queue
        self.running = False
    
    async def start(self):
        """워커 시작"""
        self.running = True
        while self.running:
            try:
                # 큐에서 작업 가져오기
                task = await self.queue.get()
                if task is None:  # 종료 신호
                    break
                
                print(f"워커 {self.name}이 작업 처리 중: {task}")
                await self.process_task(task)
                
                # 작업 완료 표시
                self.queue.task_done()
                
            except Exception as e:
                print(f"워커 {self.name} 에러: {e}")
                self.queue.task_done()
    
    async def process_task(self, task: str):
        """작업 처리"""
        # 작업 처리 시뮬레이션
        processing_time = random.uniform(0.1, 0.5)
        await asyncio.sleep(processing_time)
        
        # 가끔 에러 발생
        if random.random() < 0.1:
            raise Exception("랜덤 에러 발생")
    
    def stop(self):
        """워커 중지"""
        self.running = False

class AsyncProducer:
    """비동기 작업 생산자"""
    
    def __init__(self, queue: Queue):
        self.queue = queue
    
    async def produce_tasks(self, task_count: int):
        """작업 생산"""
        for i in range(task_count):
            await self.queue.put(f"작업 {i}")
            await asyncio.sleep(0.05)  # 작업 생성 간격
        
        # 워커들에게 종료 신호 전송
        for _ in range(3):
            await self.queue.put(None)

class AsyncTaskManager:
    """비동기 작업 관리자"""
    
    def __init__(self, worker_count: int = 3, queue_size: int = 10):
        self.worker_count = worker_count
        self.queue = Queue(maxsize=queue_size)
        self.workers: List[AsyncWorker] = []
        self.producer: Optional[AsyncProducer] = None
    
    async def start(self, task_count: int):
        """작업 관리 시작"""
        # 워커들 생성 및 시작
        for i in range(self.worker_count):
            worker = AsyncWorker(f"Worker-{i}", self.queue)
            self.workers.append(worker)
        
        # 워커 태스크들 시작
        worker_tasks = [
            asyncio.create_task(worker.start())
            for worker in self.workers
        ]
        
        # 생산자 시작
        self.producer = AsyncProducer(self.queue)
        producer_task = asyncio.create_task(
            self.producer.produce_tasks(task_count)
        )
        
        # 모든 작업 완료 대기
        await self.queue.join()
        
        # 워커들 정리
        for worker in self.workers:
            worker.stop()
        
        # 태스크들 정리
        for worker_task in worker_tasks:
            worker_task.cancel()
        
        await producer_task
    
    def get_stats(self) -> dict:
        """통계 정보 반환"""
        return {
            'worker_count': self.worker_count,
            'queue_size': self.queue.qsize(),
            'workers': [w.name for w in self.workers]
        }

# 사용 예시
async def main():
    """메인 함수"""
    manager = AsyncTaskManager(worker_count=3, queue_size=10)
    
    print("작업 관리 시작...")
    print(f"초기 상태: {manager.get_stats()}")
    
    await manager.start(task_count=20)
    
    print("모든 작업 완료!")

# 실행
# asyncio.run(main())
```

---

## 5. 고급 예외 처리

### 예외 그룹과 다중 예외 처리
```python
def process_multiple_items(items: list) -> list:
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
        # Python 3.11+ ExceptionGroup 사용
        try:
            error_messages = [f"{item}: {str(e)}" for item, e in errors]
            raise ExceptionGroup("일부 항목 처리 실패", 
                               [e for _, e in errors])
        except NameError:
            # Python 3.10 이하에서는 일반 예외로 처리
            error_summary = f"{len(errors)}개 항목 처리 실패"
            raise Exception(f"{error_summary}: {[str(e) for _, e in errors]}")
    
    return results

def process_item(item):
    """개별 항목 처리"""
    if item < 0:
        raise ValueError("음수는 처리할 수 없습니다")
    if item > 100:
        raise OverflowError("값이 너무 큽니다")
    return item * 2

# 사용 예시
try:
    results = process_multiple_items([1, -5, 50, 200, 10])
    print(f"성공적으로 처리된 항목: {len(results)}개")
except ExceptionGroup as eg:
    print(f"그룹 에러: {len(eg.exceptions)}개 예외 발생")
    for i, exc in enumerate(eg.exceptions):
        print(f"  예외 {i+1}: {type(exc).__name__}: {exc}")
except Exception as e:
    print(f"일반 에러: {e}")
```

### 예외 처리 전략과 로깅
```python
import logging
from functools import wraps
from typing import Callable, TypeVar, Any

T = TypeVar('T')

def exception_handler(func: Callable[..., T]) -> Callable[..., T]:
    """예외 처리와 로깅을 위한 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 에러 로깅
            logger = logging.getLogger(func.__module__)
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
    """위험한 작업"""
    if data < 0:
        raise ValueError("음수는 허용되지 않습니다")
    return data * 2

# 사용
try:
    result = risky_operation(-5)
except ValueError as e:
    print(f"처리된 에러: {e}")
```

---

## 6. 고급 타입 힌트와 제네릭

### 복잡한 제네릭 타입
```python
from typing import TypeVar, Generic, Callable, Union, Optional, List, Dict, Any
from dataclasses import dataclass

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class Result(Generic[T]):
    """결과를 나타내는 제네릭 클래스"""
    
    def __init__(self, value: Optional[T] = None, error: Optional[str] = None):
        self.value = value
        self.error = error
    
    def is_success(self) -> bool:
        return self.error is None
    
    def get_value(self) -> T:
        if not self.is_success():
            raise ValueError("에러가 발생했습니다")
        return self.value

class Cache(Generic[K, V]):
    """키-값 캐시 제네릭 클래스"""
    
    def __init__(self):
        self._data: Dict[K, V] = {}
    
    def set(self, key: K, value: V) -> None:
        self._data[key] = value
    
    def get(self, key: K) -> Optional[V]:
        return self._data.get(key)
    
    def remove(self, key: K) -> bool:
        if key in self._data:
            del self._data[key]
            return True
        return False

class Pipeline(Generic[T]):
    """데이터 파이프라인 제네릭 클래스"""
    
    def __init__(self, data: List[T]):
        self.data = data
    
    def map(self, func: Callable[[T], V]) -> 'Pipeline[V]':
        return Pipeline([func(item) for item in self.data])
    
    def filter(self, predicate: Callable[[T], bool]) -> 'Pipeline[T]':
        return Pipeline([item for item in self.data if predicate(item)])
    
    def reduce(self, func: Callable[[V, T], V], initial: V) -> V:
        from functools import reduce
        return reduce(func, self.data, initial)

# 사용 예시
def process_numbers(numbers: List[int]) -> Result[List[int]]:
    """숫자 리스트 처리"""
    try:
        # 파이프라인으로 처리
        pipeline = Pipeline(numbers)
        result = (pipeline
                  .filter(lambda x: x > 0)
                  .map(lambda x: x * 2)
                  .reduce(lambda acc, x: acc + x, 0))
        
        return Result(value=result)
    except Exception as e:
        return Result(error=str(e))

# 타입 힌트와 함께 사용
cache: Cache[str, int] = Cache()
cache.set("count", 42)

result: Result[int] = process_numbers([1, 2, 3, 4, 5])
if result.is_success():
    print(f"결과: {result.get_value()}")
else:
    print(f"에러: {result.error}")
```

---

## 7. 고급 메모리 최적화

### __slots__와 메모리 효율성
```python
import sys
from dataclasses import dataclass

class RegularUser:
    """일반 클래스"""
    def __init__(self, user_id: int, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email

class SlotsUser:
    """__slots__를 사용한 클래스"""
    __slots__ = ['user_id', 'name', 'email']
    
    def __init__(self, user_id: int, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email

@dataclass
class DataClassUser:
    """dataclass를 사용한 클래스"""
    user_id: int
    name: str
    email: str

# 메모리 사용량 비교
def compare_memory_usage():
    """메모리 사용량 비교"""
    users_count = 10000
    
    # 일반 클래스
    regular_users = [RegularUser(i, f"User{i}", f"user{i}@example.com") 
                     for i in range(users_count)]
    regular_memory = sum(sys.getsizeof(user) for user in regular_users)
    
    # __slots__ 클래스
    slots_users = [SlotsUser(i, f"User{i}", f"user{i}@example.com") 
                   for i in range(users_count)]
    slots_memory = sum(sys.getsizeof(user) for user in slots_users)
    
    # dataclass
    dataclass_users = [DataClassUser(i, f"User{i}", f"user{i}@example.com") 
                       for i in range(users_count)]
    dataclass_memory = sum(sys.getsizeof(user) for user in dataclass_users)
    
    print(f"일반 클래스: {regular_memory:,} bytes")
    print(f"__slots__: {slots_memory:,} bytes")
    print(f"dataclass: {dataclass_memory:,} bytes")
    print(f"__slots__ 절약: {((regular_memory - slots_memory) / regular_memory * 100):.1f}%")

# 메모리 사용량 비교 실행
compare_memory_usage()
```

### 약한 참조와 순환 참조 해결
```python
import weakref
import gc
from typing import Dict, Any

class CacheManager:
    """약한 참조를 사용한 캐시 관리자"""
    
    def __init__(self):
        self._cache: Dict[str, weakref.ref] = {}
    
    def set(self, key: str, value: Any) -> None:
        """캐시에 값 저장 (약한 참조)"""
        self._cache[key] = weakref.ref(value)
    
    def get(self, key: str) -> Any:
        """캐시에서 값 가져오기"""
        if key in self._cache:
            value_ref = self._cache[key]
            value = value_ref()
            if value is None:
                # 참조된 객체가 가비지 컬렉션됨
                del self._cache[key]
                return None
            return value
        return None
    
    def cleanup(self) -> None:
        """가비지 컬렉션된 객체들 정리"""
        keys_to_remove = []
        for key, value_ref in self._cache.items():
            if value_ref() is None:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._cache[key]

class CircularReferenceExample:
    """순환 참조 예시"""
    
    def __init__(self, name: str):
        self.name = name
        self.parent = None
        self.children = []
    
    def add_child(self, child: 'CircularReferenceExample'):
        """자식 추가"""
        child.parent = self
        self.children.append(child)
    
    def __del__(self):
        print(f"{self.name} 객체 소멸")

def demonstrate_circular_reference():
    """순환 참조 시연"""
    # 순환 참조 생성
    parent = CircularReferenceExample("부모")
    child = CircularReferenceExample("자식")
    parent.add_child(child)
    
    print("순환 참조 생성됨")
    print(f"부모의 자식 수: {len(parent.children)}")
    print(f"자식의 부모: {child.parent.name}")
    
    # 가비지 컬렉션 실행
    print("\n가비지 컬렉션 실행...")
    gc.collect()
    
    # 약한 참조를 사용한 해결책
    print("\n약한 참조를 사용한 해결책:")
    cache_manager = CacheManager()
    
    parent2 = CircularReferenceExample("부모2")
    child2 = CircularReferenceExample("자식2")
    parent2.add_child(child2)
    
    # 약한 참조로 캐시
    cache_manager.set("parent", parent2)
    cache_manager.set("child", child2)
    
    print("약한 참조로 캐시됨")
    print(f"캐시된 부모: {cache_manager.get('parent').name}")
    
    # 객체 참조 제거
    parent2 = None
    child2 = None
    
    # 가비지 컬렉션 실행
    gc.collect()
    
    # 캐시 정리
    cache_manager.cleanup()
    print(f"캐시된 부모: {cache_manager.get('parent')}")

# 순환 참조 시연
demonstrate_circular_reference()
```

---

## 8. 고급 디자인 패턴

### 메타클래스를 사용한 싱글톤
```python
class SingletonMeta(type):
    """메타클래스를 사용한 싱글톤 패턴"""
    
    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        cls._instance = None
        cls._lock = None
    
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            # 스레드 안전을 위한 락 생성
            if cls._lock is None:
                import threading
                cls._lock = threading.Lock()
            
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__call__(*args, **kwargs)
        
        return cls._instance

class DatabaseConnection(metaclass=SingletonMeta):
    """데이터베이스 연결 싱글톤"""
    
    def __init__(self):
        self.connection_string = "localhost:5432"
        self.is_connected = False
        print("데이터베이스 연결 객체 생성됨")
    
    def connect(self):
        """데이터베이스 연결"""
        if not self.is_connected:
            self.is_connected = True
            print(f"데이터베이스에 연결됨: {self.connection_string}")
        return self.is_connected
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        if self.is_connected:
            self.is_connected = False
            print("데이터베이스 연결 해제됨")

# 사용 예시
db1 = DatabaseConnection()
db2 = DatabaseConnection()

print(f"db1 is db2: {db1 is db2}")  # True
print(f"db1 id: {id(db1)}")
print(f"db2 id: {id(db2)}")

db1.connect()
db2.connect()  # 이미 연결된 상태
```

### 팩토리 메서드와 추상 팩토리
```python
from abc import ABC, abstractmethod
from typing import Dict, Type

class Database(ABC):
    """데이터베이스 추상 클래스"""
    
    @abstractmethod
    def connect(self) -> str:
        pass
    
    @abstractmethod
    def execute_query(self, query: str) -> str:
        pass

class PostgreSQL(Database):
    """PostgreSQL 구현"""
    
    def connect(self) -> str:
        return "PostgreSQL 연결됨"
    
    def execute_query(self, query: str) -> str:
        return f"PostgreSQL에서 실행: {query}"

class MySQL(Database):
    """MySQL 구현"""
    
    def connect(self) -> str:
        return "MySQL 연결됨"
    
    def execute_query(self, query: str) -> str:
        return f"MySQL에서 실행: {query}"

class SQLite(Database):
    """SQLite 구현"""
    
    def connect(self) -> str:
        return "SQLite 연결됨"
    
    def execute_query(self, query: str) -> str:
        return f"SQLite에서 실행: {query}"

class DatabaseFactory:
    """데이터베이스 팩토리"""
    
    _databases: Dict[str, Type[Database]] = {
        'postgresql': PostgreSQL,
        'mysql': MySQL,
        'sqlite': SQLite
    }
    
    @classmethod
    def create_database(cls, db_type: str) -> Database:
        """데이터베이스 생성"""
        if db_type not in cls._databases:
            raise ValueError(f"지원하지 않는 데이터베이스: {db_type}")
        
        return cls._databases[db_type]()
    
    @classmethod
    def register_database(cls, name: str, db_class: Type[Database]):
        """새로운 데이터베이스 타입 등록"""
        cls._databases[name] = db_class
    
    @classmethod
    def get_supported_databases(cls) -> list:
        """지원하는 데이터베이스 목록 반환"""
        return list(cls._databases.keys())

# 사용 예시
try:
    # PostgreSQL 생성
    postgres = DatabaseFactory.create_database("postgresql")
    print(postgres.connect())
    print(postgres.execute_query("SELECT * FROM users"))
    
    # MySQL 생성
    mysql = DatabaseFactory.create_database("mysql")
    print(mysql.connect())
    print(mysql.execute_query("SELECT * FROM products"))
    
    # 지원하는 데이터베이스 목록
    print(f"지원하는 데이터베이스: {DatabaseFactory.get_supported_databases()}")
    
except ValueError as e:
    print(f"에러: {e}")
```

---

## 9. 성능 최적화 기법

### 프로파일링과 최적화
```python
import time
import cProfile
import pstats
from functools import wraps
from typing import Callable, Any

def profile_function(func: Callable[..., Any]) -> Callable[..., Any]:
    """함수 프로파일링 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            profiler.disable()
            
            # 프로파일 결과 출력
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')
            print(f"\n=== {func.__name__} 프로파일 결과 ===")
            stats.print_stats(10)  # 상위 10개 함수
    
    return wrapper

def performance_monitor(func: Callable[..., Any]) -> Callable[..., Any]:
    """성능 모니터링 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        start_memory = 0  # 실제로는 memory_profiler 사용
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            end_memory = 0
            
            execution_time = end_time - start_time
            print(f"{func.__name__}: {execution_time:.4f}초")
    
    return wrapper

@profile_function
@performance_monitor
def inefficient_function(n: int) -> int:
    """비효율적인 함수 (프로파일링 대상)"""
    result = 0
    for i in range(n):
        for j in range(n):
            result += i * j
    return result

@performance_monitor
def optimized_function(n: int) -> int:
    """최적화된 함수"""
    # 수학적 공식 사용
    return (n * (n - 1) * (2 * n - 1)) // 6

# 성능 비교
if __name__ == "__main__":
    n = 1000
    
    print("비효율적인 함수 실행:")
    result1 = inefficient_function(n)
    
    print("\n최적화된 함수 실행:")
    result2 = optimized_function(n)
    
    print(f"\n결과 비교:")
    print(f"비효율적: {result1}")
    print(f"최적화: {result2}")
    print(f"결과 일치: {result1 == result2}")
```

---

## 10. 면접 질문 & 답변

### 🎯 **고급 문법 관련 면접 질문**

#### **메타클래스**
**Q: 메타클래스란 무엇이고 언제 사용하나요?**
**A:** 메타클래스는 클래스를 생성하는 클래스입니다. `type()`이 기본 메타클래스이며, 클래스 생성 시점에 자동으로 로깅, 검증, 메서드 추가 등을 수행할 때 사용합니다.

**Q: 메타클래스와 상속의 차이점은?**
**A:** 상속은 인스턴스 레벨에서 동작하고, 메타클래스는 클래스 정의 레벨에서 동작합니다. 메타클래스는 클래스 자체의 구조를 변경할 수 있습니다.

#### **고급 데코레이터**
**Q: 매개변수가 있는 데코레이터를 어떻게 구현하나요?**
**A:** 데코레이터 팩토리 패턴을 사용합니다. 외부 함수가 매개변수를 받고, 내부에 실제 데코레이터를 정의하여 반환하는 구조입니다.

**Q: 데코레이터 체이닝의 장점은?**
**A:** 여러 기능을 독립적으로 구현하고 조합할 수 있어 코드 재사용성과 유지보수성이 향상됩니다.

#### **함수형 프로그래밍**
**Q: 모나드란 무엇인가요?**
**A:** 모나드는 값을 감싸는 컨테이너로, `map`, `flat_map` 등의 메서드를 제공합니다. 에러 처리나 비동기 처리에서 유용합니다.

**Q: 함수형 프로그래밍의 장단점은?**
**A:** 장점: 부작용이 없고 테스트하기 쉽습니다. 단점: 학습 곡선이 높고 디버깅이 어려울 수 있습니다.

#### **비동기 프로그래밍**
**Q: asyncio.Queue와 일반 Queue의 차이점은?**
**A:** asyncio.Queue는 비동기 환경에서 사용되며, `await`를 사용하여 비동기적으로 데이터를 가져오고 넣을 수 있습니다.

**Q: 세마포어와 뮤텍스의 차이점은?**
**A:** 세마포어는 여러 스레드가 동시에 접근할 수 있게 하고, 뮤텍스는 한 번에 하나의 스레드만 접근할 수 있게 합니다.

### 💡 **실무 활용 포인트**

1. **메타클래스**: 프레임워크 개발, 자동 코드 생성
2. **고급 데코레이터**: 미들웨어, 플러그인 시스템
3. **함수형 프로그래밍**: 데이터 파이프라인, 에러 처리
4. **비동기 프로그래밍**: 고성능 웹 서버, 마이크로서비스
5. **성능 최적화**: 대용량 데이터 처리, 실시간 시스템

---

<details>
<summary>cf. reference</summary>

- Python 공식 문서: https://docs.python.org/3/
- Real Python - Advanced Topics: https://realpython.com/python-advanced/
- Python Design Patterns: https://python-patterns.guide/
- Python Performance: https://docs.python.org/3/library/profile.html

</details>
