---
title: "Python 메모리 최적화 기법"
date: 2025-08-18
categories:
  - python
tags:
  - memory-optimization
  - __slots__
  - reference-counting
  - weak-references
  - garbage-collection
---

# Python 메모리 최적화 기법

## 1. __slots__를 사용한 메모리 최적화

`__slots__`는 클래스에 `__dict__`를 생성하지 않도록 하여 메모리 절약 + 속도 최적화를 위해 사용되는 특별한 클래스 속성이다.

- 파이썬 클래스 인스턴스는 기본적으로 `__dict__`라는 딕셔너리를 갖고있어 동적으로 속성을 추가할 수 있다. 
- `__dict__`는 유연하지만 속성 1개마다 추가적인 메모리를 사용한다. 
- 이때 `__slots__`을 사용하면 지정한 속성 외에는 추가 불가 → 딕셔너리 할당 메모리 절감이 가능하다.

```python
import sys

# 일반 클래스 (__dict__ 사용)
class WithDict:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# __slots__ 사용 클래스
class WithSlots:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = x
        self.y = y

# 메모리 사용량 비교
a = WithDict(1, 2)
b = WithSlots(1, 2)

print(f"WithDict 메모리: {sys.getsizeof(a)} bytes")    # 예: 56 bytes
print(f"WithSlots 메모리: {sys.getsizeof(b)} bytes")   # 예: 40 bytes
print(f"메모리 절약: {sys.getsizeof(a) - sys.getsizeof(b)} bytes")

# __slots__ 사용 시 장점
# 1. 메모리 사용량 감소 (인스턴스 __dict__ 제거)
# 2. 속성 접근 속도 향상
# 3. 동적 속성 추가 방지 (런타임 에러)
```

## 2. is vs == 비교와 객체 ID

- `is`는 객체 자체가 같은가를 보고 `==`는 내용이 같은가를 확인한다. (cf. None 체크시에는 is 사용이 권장된다)
- is는 결국 `id(객체1) == id(객체2)`를 의미하는 sugar syntax이다. 따라서 is 연산은 "두 객체가 메모리 상에서 동일한 객체인지"를 비교하는 것이다.

```python
# 리스트 비교 예시
a = [1, 2, 3]
b = [1, 2, 3]

print(f"a == b: {a == b}")    # True - 값 비교
print(f"a is b: {a is b}")    # False - 객체 ID 다름
print(f"a의 id: {id(a)}") # id(객체)는 객체의 고유한 메모리 주소를 반환하는 메서드 
print(f"b의 id: {id(b)}")

# 작은 정수는 인터닝 (interning)
x = 100
y = 100
print(f"x is y (100): {x is y}")    # True - 작은 정수는 인터닝

# 큰 정수는 인터닝 대상 아님
x = 1000
y = 1000
print(f"x is y (1000): {x is y}")  # False - 큰 정수는 인터닝 안됨

# 문자열 인터닝
s1 = "hello"
s2 = "hello"
print(f"s1 is s2: {s1 is s2}")     # True - 문자열 리터럴은 인터닝
```

## 3. id()와 객체 재사용 (Interning)

```python
# CPython의 객체 재사용 메커니즘
print("=== 작은 정수 인터닝 ===")
for i in range(-5, 257):
    a = i
    b = i
    if a is not b:
        print(f"인터닝 안됨: {i}")

print("\n=== 문자열 인터닝 ===")
# 컴파일 타임에 결정되는 문자열은 인터닝
s1 = "hello"
s2 = "hello"
print(f"리터럴 문자열: {s1 is s2}")  # True

# 런타임에 생성된 문자열은 인터닝 안됨
s3 = "".join(['h', 'e', 'l', 'l', 'o'])
print(f"동적 생성 문자열: {s1 is s3}")  # False

# 하지만 값은 같음
print(f"값 비교: {s1 == s3}")  # True
```

## 4. 참조 카운팅 내부 구조

```python
import sys
import ctypes

# CPython의 참조 카운팅 내부 구조
def get_ref_count_details(obj):
    """객체의 참조 카운팅 상세 정보"""
    # PyObject 구조체의 ob_refcnt 필드 접근
    # 주의: 이는 CPython 구현에 의존적이며 위험할 수 있음
    try:
        # ctypes를 사용한 내부 구조 접근 (교육 목적)
        ref_count = sys.getrefcount(obj)
        obj_id = id(obj)
        obj_type = type(obj).__name__
        
        return {
            'ref_count': ref_count,
            'object_id': obj_id,
            'type': obj_type,
            'size': sys.getsizeof(obj)
        }
    except Exception as e:
        return f"에러: {e}"

# 참조 카운팅 상세 분석
x = [1, 2, 3]
print("=== 참조 카운팅 상세 분석 ===")
print(f"객체 정보: {get_ref_count_details(x)}")

# 참조 추가/제거 시 변화
y = x
print(f"참조 추가 후: {get_ref_count_details(x)}")

del y
print(f"참조 제거 후: {get_ref_count_details(x)}")

# CPython 내부 구조 설명
print("\n=== CPython 내부 구조 ===")
print("PyObject 구조체:")
print("  - ob_refcnt: 참조 카운트 (Py_ssize_t)")
print("  - ob_type: 타입 객체 포인터")
print("  - ob_data: 실제 데이터")
```

## 5. 약한 참조와 순환 참조 해결

```python
import weakref
import gc

# 약한 참조를 사용한 캐시 구현
class Cache:
    def __init__(self):
        # WeakValueDictionary: 키가 약한 참조로 관리됨
        self._cache = weakref.WeakValueDictionary()
    
    def get(self, key):
        return self._cache.get(key)
    
    def set(self, key, value):
        self._cache[key] = value
    
    def clear(self):
        self._cache.clear()
    
    def size(self):
        return len(self._cache)

# 사용 예시
cache = Cache()

# 객체 생성 및 캐시 저장
class ExpensiveObject:
    def __init__(self, name):
        self.name = name
        print(f"{name} 객체 생성됨")
    
    def __del__(self):
        print(f"{name} 객체 소멸됨")

# 캐시에 객체 저장
obj1 = ExpensiveObject("첫번째")
obj2 = ExpensiveObject("두번째")

cache.set("obj1", obj1)
cache.set("obj2", obj2)

print(f"캐시 크기: {cache.size()}")  # 2

# 객체 참조 제거
del obj1
gc.collect()  # 가비지 컬렉션 실행

print(f"obj1 제거 후 캐시 크기: {cache.size()}")  # 1
print(f"obj2 여전히 존재: {cache.get('obj2')}")

# 약한 참조의 장점
print("\n=== 약한 참조 장점 ===")
print("1. 메모리 누수 방지: 참조된 객체가 없어지면 자동 제거")
print("2. 순환 참조 해결: 약한 참조는 참조 카운트에 포함되지 않음")
print("3. 캐시 구현: 메모리 부족 시 자동으로 오래된 객체 제거")

# WeakRef 사용 예시
class Observer:
    def __init__(self, name):
        self.name = name
    
    def update(self, data):
        print(f"{self.name}이 {data}를 받았습니다")

class Subject:
    def __init__(self):
        # 약한 참조로 옵저버 관리
        self._observers = weakref.WeakSet()
    
    def add_observer(self, observer):
        self._observers.add(observer)
    
    def notify(self, data):
        # 약한 참조로 인해 이미 소멸된 옵저버는 자동 제거됨
        for observer in self._observers:
            observer.update(data)

# 사용 예시
subject = Subject()
observer1 = Observer("옵저버1")
observer2 = Observer("옵저버2")

subject.add_observer(observer1)
subject.add_observer(observer2)

print("=== 옵저버 패턴 테스트 ===")
subject.notify("데이터1")

# observer1 제거
del observer1
gc.collect()

print("observer1 제거 후:")
subject.notify("데이터2")  # observer2만 알림
```

## 6. 실무 활용 사례

### Singleton 패턴 구현
```python
import threading

class DatabaseConnection:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-checked locking
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, connection_string):
        if not hasattr(self, 'connection_string'):  # 한 번만 초기화
            self.connection_string = connection_string
            self.connection = self._create_connection()
    
    def _create_connection(self):
        # 실제 DB 연결 로직
        return f"Connected to {self.connection_string}"
```

### Immutable Data Class
```python
from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)  # frozen=True로 immutable 생성
class Point:
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def __add__(self, other: 'Point') -> 'Point':
        return Point(self.x + other.x, self.y + other.y)

# 사용 예시
p1 = Point(1.0, 2.0)
p2 = Point(4.0, 6.0)
p3 = p1 + p2  # 새로운 Point 객체 생성

try:
    p1.x = 5.0  # FrozenInstanceError 발생
except Exception as e:
    print(f"에러: {e}")
```

---

<details>
<summary>cf. reference</summary>

- 

</details>
