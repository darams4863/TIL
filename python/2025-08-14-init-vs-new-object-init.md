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

## 0. 매직 메서드란? 
- 파이썬의 매직 메서드는 `__이름__` 형식처럼 앞뒤로 밑줄 2개가 붙은 특수 메서드로, 클래스가 파이썬 내장 동작을 오버라이드(/내장 동작을 클래스가 커스터마이징) 할 수 있도록 해주는 특수한 이름의 메서드들이다. 
  - 예: `__init__(생성자)`, `__len__(len() 호출 시 실행)`, `__str__(str() 또는 print() 호출 시 문자열로 변환)`,   `__getitem__(객체에서 obj[0]처럼 인덱스로 접근할 때 실행)` 
  - 예를 들어 __str__은 print(obj) 시 사람이 읽기 쉬운 출력값을 지정할 수 있고, __getitem__은 obj[key] 방식으로 인덱싱 가능하게 해준다. 실무에서는 사용자 설정 객체를 dict처럼 다루기 위해 __getitem__, __setitem__을 사용하거나, 디버깅 편의성을 위해 __repr__을 정의할 수도 있다.
- 이런 메서드들을 오버라이딩하면:
  - 파이썬 내장함수 len(), str(), abs() 등의 동작을 나의 객체에 맞게 바꿀 수 있다. 즉 객체를 파이썬스럽게 다룰 수 있게 하는 방법의 핵심이다. 
  - 예: 
  ```python
  class Settings:
    def __init__(self):
        self._data = {"host": "localhost", "port": 8080}

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

  s = Settings()
  print(s["host"])  # localhost
  s["host"] = "127.0.0.1"
  print(s["host"])  # 127.0.0.1
  ```

## 1. __init__ vs __new__ 기본 개념
- 두 메서드는 **모두 인스턴스를 생성할 떄 호출되는 매직 메서드**이지만, 역할과 실행 시점이 완전히 다르다. 

### 핵심 차이점
- **`__new__`**: 
  - 인스턴스를 **생성**하는 메서드이다 (constructor)
  - 호출 시점: 클래스 호출 시 가장 먼저 호출 -> 객체가 생성되기 전에 호출 
  - 리턴값: 인스턴스(보통 `super().__new__`)를 리턴해야한다 
  - 주 사용처: 불변 객체(예: tuple, str)의 커스터마이징, 싱글톤 패턴
  - 정적 메서드인가: 예 (`@staticmethod` 처럼 동작함. 즉, 클래스 내부에서 정의되지만 클래스나 인스턴스와 무관하게 동작하는 메서드이고, 일반 메서드와 달리 self나 cls를 받지 않는다. 클래스 소속이긴 하지만, 순수한 함수처럼 사용된다. 선언할 때 @staticmethod 데코레이터를 사용한다)
- **`__init__`**: 
  - 인스턴스를 **초기화**하는 메서드이다 (initializer)
  - 호출 시점: `__new__`가 객체를 반환한 다음 -> 객체가 생성된 후에 호출 
  - 리턴값: 아무 것도 리턴하지 않음 (None)
  - 주 사용처: 일반적인 인스턴스 초기화 
  - 정적 메서드인가: 아니오 (`self`를 인자로 받음)
- 정리: 

```python
"""
__new__는 인스턴스를 생성하는 메서드,
__init__은 생성된 인스턴스를 초기화하는 메서드입니다.

__new__는 클래스 호출 시 가장 먼저 실행되며, 반드시 인스턴스를 반환해야 하고,
__init__은 __new__가 반환한 인스턴스를 받아 초기화 작업을 수행합니다.

주로 __init__만 정의해서 사용하지만, 불변 객체를 커스터마이징하거나
싱글톤처럼 인스턴스 생성을 제어하고자 할 때는 __new__를 오버라이드하기도 합니다.
"""

class MyClass:
    def __new__(cls, *args, **kwargs):
        print("📦 __new__ 호출 - 인스턴스 생성")
        instance = super().__new__(cls)
        return instance
    
    def __init__(self, value):
        print("🔧 __init__ 호출 - 인스턴스 초기화")
        self.value = value

obj = MyClass(42)
# 출력 순서:
# 📦 __new__ 호출 - 인스턴스 생성
# 🔧 __init__ 호출 - 인스턴스 초기화
```

#### 일반 메서드 vs 클래스 메서드 vs 정적 메서드
- 정리: 

|종류|첫 번째 인자|특징|대표 용도|
|---------|--------|--------------|---------------|
|일반 메서드|self|인스턴스 메서드|객체 상태 변경|
|클래스 메서드|cls|클래스 자체를 다룸|팩토리 메서드 등|
|정적 메서드|없음|독립적 로직 처리|유틸성 함수|

- 예: 

```python
class MyClass:

    def instance_method(self):
        # ✅ self: 인스턴스 자신을 참조 → 객체 상태에 접근하거나 수정 가능
        print("나는 인스턴스 메서드입니다. self로 호출됨")

    @classmethod
    def class_method(cls):
        # ✅ cls: 클래스 자체를 참조 → 클래스 속성 변경/접근 시 사용
        print("나는 클래스 메서드입니다. cls로 호출됨")

    @staticmethod
    def static_method():
        # ✅ self나 cls 없음 → 독립적인 유틸성 로직
        print("나는 정적 메서드입니다. self나 cls 없이 호출됨")

obj = MyClass()

obj.instance_method()     # 👉 인스턴스를 통해 호출 (self 자동 전달됨)
obj.class_method()        # 👉 인스턴스를 통해 호출 (cls 자동 전달됨)
obj.static_method()       # 👉 인스턴스를 통해 호출 (인자 없음)

MyClass.class_method()    # 👉 클래스로도 호출 가능 (cls 자동 전달)
MyClass.static_method()   # 👉 클래스로 호출 (완전한 독립 메서드)

# 언제 어떤 것을 사용? 
# •	인스턴스 메서드는 해당 인스턴스의 상태(속성)를 읽거나 변경할 때 사용됩니다.
# •	클래스 메서드는 인스턴스를 새로 생성하거나, 클래스 전역 설정 등 클래스 자체에 관련된 동작이 필요할 때 사용합니다.
# •	정적 메서드는 클래스나 인스턴스와 무관하게 독립적으로 동작하는 헬퍼 함수를 정의할 때 사용합니다.
```


여기부터 ~~ 
4. 도 확인 필요 실무 예시 (깊은 / 얕은 복사)



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
- Python에서는 객체가 생성된 후 내부 상태를 변경할 수 있으면 mutable, 그렇지 않으면 immutable로 구분한다. 리스트나 딕셔너리는 mutable, 정수나 문자열은 immutable이다. 

**함수 인자 전달 시 핵심 포인트:**
- Python은 함수 인자 전달 시 **'값'이 아닌 '참조(객체 주소)'를 전달**한다
- 변수 이름은 객체를 '가리키는' 참조일 뿐이다

**Mutable vs Immutable의 함수 내 동작 차이:**

```python
# Mutable 객체: 리스트 예시
def add_item(my_list):
    my_list.append(4)  # 원본 객체 직접 수정

lst = [1, 2, 3]
print(f"Before: id={id(lst)} → {lst}")
add_item(lst)
print(f"After: id={id(lst)} → {lst}")
# 출력: Before: id=140234567890 → [1, 2, 3]
#       After: id=140234567890 → [1, 2, 3, 4]  # 같은 객체, 내용만 변경

# Immutable 객체: 정수 예시  
def add_num(n):
    n += 1  # 새로운 객체 생성하여 n에 할당
    print(f"In function: id={id(n)}, value={n}")

num = 10
print(f"Before: id={id(num)} → {num}")
add_num(num)
print(f"After: id={id(num)} → {num}")
# 출력: Before: id=140234567890 → 10
#       In function: id=140234567891 → 11  # 함수 내에서만 다른 객체
#       After: id=140234567890 → 10        # 원본은 그대로
```

**메모리 관점에서의 차이점:**

| 구분 | Mutable 객체 (list, dict, set) | Immutable 객체 (int, str, tuple) |
|------|--------------------------------|----------------------------------|
| 함수 인자로 전달 시 | 같은 객체를 공유함 | 새로운 객체가 만들어짐 |
| 함수 내부에서 값 변경 시 | 원본도 변경됨 (side effect) | 원본은 그대로, 복사된 객체만 변경됨 |
| 메모리 주소 | 함수 안/밖 모두 동일 | 함수 안에서만 주소가 다름 |

**사이드 이펙트가 문제인 이유:**
1. **예측 불가능**: 함수 실행 결과가 외부 상태에 따라 달라짐
2. **디버깅 어려움**: 함수 외부 값 변화의 원인 추적이 어려움  
3. **재사용성 저하**: 같은 입력에 대해 다른 결과 가능
4. **병렬 처리 위험**: 외부 상태 공유로 인한 race condition

**실무에서 자주 겪는 사례와 해결책:**

```python
# 문제 상황: 전역 mutable 객체 공유
def add_header(headers):
    headers['Authorization'] = 'Bearer xyz'

# 주의가 필요한 코드
common_headers = {}
add_header(common_headers)
# → 이후 다른 요청에서도 'Authorization'이 의도치 않게 포함될 수 있음

# 해결책 1: deepcopy 사용
import copy
def add_header_safe(headers):
    headers_copy = copy.deepcopy(headers)
    headers_copy['Authorization'] = 'Bearer xyz'
    return headers_copy

# 해결책 2: 슬라이싱으로 얕은 복사 (1차원만)
def add_header_safe2(headers):
    headers_copy = headers[:]  # 리스트의 경우
    headers_copy.append('new_item')
    return headers_copy

# 해결책 3: 새로운 객체 생성
def add_header_safe3(headers):
    return {**headers, 'Authorization': 'Bearer xyz'}  # 딕셔너리 병합
```

**핵심 정리:**
- **Immutable 객체 사용**: 사이드 이펙트 방지에 효과적
- **Mutable 객체**: 함수 내에서 복사본을 만들어 조작하는 것이 안전
- **deepcopy vs shallow copy**: 중첩된 구조는 deepcopy, 단순 구조는 슬라이싱이나 생성자 사용

### Immutable 객체
- **한 번 생성되면 값 변경 불가**
- **해시 가능** → dict key, set 요소로 사용 가능
- **스레드 안전** → 동기화 비용 없음
- **Immutable 객체 종류**:

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
- **Mutable 객체 종류**:

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

## 6. 메모리 최적화 기법

### __slots__를 사용한 메모리 최적화
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

### is vs == 비교와 객체 ID
```python
# 리스트 비교 예시
a = [1, 2, 3]
b = [1, 2, 3]

print(f"a == b: {a == b}")    # True - 값 비교
print(f"a is b: {a is b}")    # False - 객체 ID 다름
print(f"a의 id: {id(a)}")
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

### id()와 객체 재사용 (Interning)
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

### 참조 카운팅 내부 구조
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

### 약한 참조와 순환 참조 해결
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

## 7. 실무 활용 사례

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

## 8. 면접 질문 & 답변

### Q: 파이썬의 매직 메서드란 무엇이고, 실무에서 사용해본 적이 있나요?
**A:** 

```text
파이썬의 매직 메서드는 __init__, __str__처럼 앞뒤로 밑줄 2개가 붙은 특수 메서드로, 클래스가 파이썬 내장 동작을 오버라이드할 수 있도록 해줍니다.
예를 들어 __str__은 print(obj) 시 사람이 읽기 쉬운 출력값을 지정할 수 있고, __getitem__은 obj[key] 방식으로 인덱싱 가능하게 해줍니다.
실무에서는 사용자 설정 객체를 dict처럼 다루기 위해 __getitem__, __setitem__을 사용하거나, 디버깅 편의성을 위해 __repr__을 정의해본 경험이 있습니다.
```

### Q: __str__과 __repr__의 차이는 무엇인가요?
**A:** 

```python
# __str__은 사용자 친화적인 출력용이고, __repr__은 개발자/디버깅용 표현입니다.
# print()는 __str__을 먼저 호출하고, 없으면 __repr__을 fallback으로 사용합니다.
# 반대로 repr()은 항상 __repr__을 호출합니다.

def __str__(self):    # 사용자에게 보이게
    return "사용자 이름: 다예"

def __repr__(self):   # 개발자 디버깅 용도
    return "User(name='다예')"
``` 


### Q: __getitem__과 __iter__, __len__을 같이 쓰면 어떤 이점이 있을까요?
**A:** 
"이 세 가지 메서드를 함께 구현하면 컨테이너형 객체처럼 만들 수 있어 for, len(), [] 접근이 모두 가능해집니다.
파이썬 내장 자료형처럼 동작하게 되어, 사용성과 테스트가 훨씬 좋아집니다."

### Q: __eq__, __hash__는 언제 함께 재정의해야 하나요?
**A:** 

```text 
__eq__만 재정의하면 == 비교는 가능하지만, 객체를 set이나 dict의 key로 쓸 수 없습니다.
이때 __hash__도 함께 재정의해서 두 객체가 같다면 해시값도 같게 해줘야 합니다.
즉, ==가 True면 hash()도 같아야 set, dict에서 의도대로 동작합니다.
```

### Q: __eq__만 있고 __hash__가 없는 객체를 set에 넣으면 어떻게 되나요?
**A:** 

```text 
__hash__가 없으면 해당 객체는 mutable로 간주되어 unhashable type 에러가 납니다.
따라서 set, dict의 key로 쓸 수 없습니다.
```

### Q:매직 메서드를 활용해 dict처럼 동작하는 설정 클래스를 구현해보세요.
**A:** 
```python
class Settings:
    def __init__(self):
        self._data = {"env": "prod", "debug": False}

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
```

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

### Q: `is`와 `==`의 차이점을 설명해주세요.
**A:** 
- **`==`**: **값 비교**를 수행합니다. 두 객체의 내용이 같은지 확인합니다.
- **`is`**: **객체 ID 비교**를 수행합니다. 두 변수가 같은 메모리 위치를 가리키는지 확인합니다.

**예시**:
```python
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)  # True (값이 같음)
print(a is b)  # False (다른 객체)

# 작은 정수는 인터닝으로 인해 같은 객체
x = 100
y = 100
print(x is y)  # True
```

### Q: `__slots__`를 언제 사용하나요?
**A:** 
1. **메모리 최적화가 중요한 경우**: 대량의 객체를 생성할 때
2. **속성 접근 속도 향상이 필요한 경우**: 자주 접근하는 속성이 많을 때
3. **동적 속성 추가를 방지하고 싶은 경우**: 클래스 구조를 고정하고 싶을 때
4. **제한된 메모리 환경**: 임베디드 시스템이나 서버 환경

**주의사항**: 상속 시 부모 클래스의 `__slots__`와 충돌할 수 있으며, 동적 속성 추가가 불가능합니다.

---

<details>
<summary>cf. reference</summary>

- 

</details> 

