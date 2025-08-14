---
title: "__init__ vs __new__, 객체 생성"
date: 2025-08-14
categories:
  - python
tags:
  - __init__
  - __new__
  - object-creation
  - immutable
  - mutable
  - memory-management
---

# __init__ vs __new__, 객체 생성

## 1. __init__ vs __new__ 기본 개념

### 핵심 차이점
- **`__new__`**: 객체를 **생성**하는 메서드 (constructor)
- **`__init__`**: 객체를 **초기화**하는 메서드 (initializer)

### 객체 생성 흐름
```python
# 객체 생성 시 호출 순서
1. __new__(cls, *args, **kwargs) → 객체 생성 및 반환
2. __init__(self, *args, **kwargs) → 객체 초기화
```

## 2. __new__ 메서드 상세

### __new__의 역할
- 클래스의 **새로운 인스턴스를 생성**하고 반환
- `object.__new__()`가 실제 메모리 할당을 담당
- 반환값이 `None`이면 `__init__`이 호출되지 않음

### __new__ 오버라이딩 예시
```python
class Singleton:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, name):
        self.name = name

# 사용 예시
s1 = Singleton("첫번째")
s2 = Singleton("두번째")
print(s1 is s2)  # True - 같은 객체
print(s1.name)   # "두번째" - 마지막 __init__ 호출 결과
```

### Immutable 객체에서의 활용
```python
class ImmutableTuple(tuple):
    def __new__(cls, *args):
        # 튜플 생성 전에 검증 로직 추가
        if len(args) < 2:
            raise ValueError("최소 2개 이상의 요소가 필요합니다")
        return super().__new__(cls, args)
    
    def __init__(self, *args):
        # immutable이므로 초기화 불필요
        pass

# 사용 예시
try:
    t1 = ImmutableTuple(1, 2, 3)  # 성공
    t2 = ImmutableTuple(1)        # ValueError 발생
except ValueError as e:
    print(f"에러: {e}")
```

## 3. __init__ 메서드 상세

### __init__의 역할
- 이미 생성된 객체의 **초기화 작업** 수행
- 인스턴스 변수 설정, 기본값 할당 등
- 반환값이 없음 (None 반환)

### __init__ 오버라이딩 예시
```python
class User:
    def __init__(self, name, age, email=None):
        self.name = name
        self.age = age
        self.email = email or f"{name}@example.com"
        self.created_at = datetime.now()
    
    def __str__(self):
        return f"User(name={self.name}, age={self.age}, email={self.email})"

# 사용 예시
user1 = User("김철수", 25)
user2 = User("이영희", 30, "lee@example.com")
print(user1)  # User(name=김철수, age=25, email=김철수@example.com)
```

## 4. Immutable vs Mutable 객체

### Immutable 객체
- **한 번 생성되면 값 변경 불가**
- **해시 가능** → dict key, set 요소로 사용 가능
- **스레드 안전** → 동기화 비용 없음

#### Immutable 객체 종류
```python
# 기본 타입
x = 42          # int
y = 3.14        # float
z = "hello"     # str
t = (1, 2, 3)  # tuple
f = frozenset([1, 2, 3])  # frozenset

# 사용 예시
my_dict = {x: "정수", z: "문자열", t: "튜플"}  # dict key로 사용 가능
my_set = {x, y, z}  # set 요소로 사용 가능
```

### Mutable 객체
- **생성 후 내부 상태 변경 가능**
- **해시 불가능** → dict key, set 요소로 사용 불가
- **스레드 안전하지 않음** → 동기화 필요

#### Mutable 객체 종류
```python
# 기본 타입
my_list = [1, 2, 3]      # list
my_dict = {"a": 1}       # dict
my_set = {1, 2, 3}       # set
my_bytearray = bytearray(b"hello")  # bytearray

# 사용 예시
try:
    my_dict[my_list] = "값"  # TypeError: unhashable type: 'list'
except TypeError as e:
    print(f"에러: {e}")
```

## 5. 객체 생성과 메모리 흐름

### 메모리 할당 과정
```python
class Example:
    def __new__(cls, *args, **kwargs):
        print("1. __new__ 호출 - 메모리 할당")
        instance = super().__new__(cls)
        print(f"2. 생성된 객체: {instance}")
        return instance
    
    def __init__(self, value):
        print("3. __init__ 호출 - 초기화")
        self.value = value
        print(f"4. 초기화 완료: {self.value}")

# 객체 생성 시 실행 흐름
obj = Example("테스트")
```

### 메모리 관리 메커니즘

#### 참조 카운팅 (Reference Counting)
```python
import sys

# 참조 카운트 확인
x = [1, 2, 3]
print(f"참조 카운트: {sys.getrefcount(x)}")  # 2 (변수 + getrefcount 인자)

y = x  # 참조 추가
print(f"참조 카운트: {sys.getrefcount(x)}")  # 3

del y  # 참조 제거
print(f"참조 카운트: {sys.getrefcount(x)}")  # 2
```

#### 가비지 컬렉션 (Garbage Collection)
```python
import gc

# 순환 참조 예시
class Node:
    def __init__(self, name):
        self.name = name
        self.ref = None

# 순환 참조 생성
node1 = Node("A")
node2 = Node("B")
node1.ref = node2
node2.ref = node1

# 참조 카운트는 0이 아니지만 순환 참조로 인해 접근 불가
del node1
del node2

# 가비지 컬렉션으로 순환 참조 해결
gc.collect()
```

## 6. 실무 활용 사례

### Singleton 패턴 구현
```python
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

## 7. 면접 질문 & 답변

### Q: __init__과 __new__의 차이점을 설명해주세요.
**A:** 
- **`__new__`**: 객체를 **생성**하는 메서드로, 실제 메모리 할당을 담당합니다. 클래스의 새 인스턴스를 반환하며, 이 메서드가 `None`을 반환하면 `__init__`이 호출되지 않습니다.

- **`__init__`**: 이미 생성된 객체를 **초기화**하는 메서드로, 인스턴스 변수 설정이나 기본값 할당 등의 작업을 수행합니다. 반환값이 없습니다.

**호출 순서**: `__new__` → `__init__`

### Q: Immutable 객체가 중요한 이유는 무엇인가요?
**A:** 
1. **해시 가능성**: dict의 key나 set의 요소로 사용할 수 있습니다.
2. **스레드 안전성**: 여러 스레드에서 동시 접근해도 상태 변경이 없어 동기화 비용이 줄어듭니다.
3. **예측 가능성**: 객체 생성 후 상태가 변하지 않아 코드의 동작을 예측하기 쉽습니다.
4. **성능 최적화**: Python이 작은 정수나 문자열을 인터닝하여 메모리를 절약할 수 있습니다.

### Q: 메모리 최적화를 위해 어떤 기법을 사용하나요?
**A:** 
1. **`__slots__` 사용**: 인스턴스 딕셔너리 대신 슬롯을 사용하여 메모리 사용량 감소
2. **가비지 컬렉션 관리**: `gc.collect()`로 순환 참조 해결
3. **객체 풀링**: 자주 생성/삭제되는 객체를 재사용
4. **약한 참조**: `weakref`를 사용하여 메모리 누수 방지

### Q: 순환 참조 문제를 어떻게 해결하나요?
**A:** 
1. **약한 참조 사용**: `weakref.ref()`로 순환 참조 방지
2. **가비지 컬렉션**: `gc.collect()`로 주기적 정리
3. **참조 구조 설계**: 순환 참조가 발생하지 않도록 아키텍처 설계
4. **컨텍스트 매니저**: `with` 문으로 리소스 자동 정리

---

<details>
<summary>cf. reference</summary>

- 

</details> 

