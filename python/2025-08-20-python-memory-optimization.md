---
title: "Python 메모리 최적화 기법"
date: 2025-08-20
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
- `__slots__`는 클래스에 `__dict__`를 생성하지 않도록 하여 메모리 절약 + 속도 최적화를 위해 사용되는 특별한 클래스 속성이다.
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

## 2. 객체 재사용 (Interning)
- 인터닝이란 같은 갖는 불변 객체를 메모리 상에서 하나만 만들어두고, 재사용하는 기법이다. 
- 변경 불가능한 객체(Immutable Objects)만 인터닝 대상이고, 
    - 정수, 문자열, 튜플, 불(boolean), None 등은 가능 
    - 리스트, 딕셔너리 등 가변 객체는 인터닝 불가 
- 같은 값을 갖는 객체를 중복 생성하지 않아 메모리 절약이 가능하다. 
- 객체 수 자체가 줄어들기 때문에 가비지 컬렉션 부담이 완화된다 

### cf. is vs == 비교와 객체 ID
- `is`는 객체 자체가 같은가를 보고 `==`는 내용이 같은가를 확인한다. (cf. None 체크시에는 is 사용이 권장된다)
- is는 결국 `id(객체1) == id(객체2)`를 의미하는 sugar syntax이다. 따라서 is 연산은 "두 객체가 메모리 상에서 동일한 객체인지"를 비교하는 것이다.

```python
a = "hello"
b = "hello"
print(a is b)  # True / False → 메모리 공유 중 (인터닝) / 인터닝 X 
print(a == b)  # True 

# 이때 인터닝이 되어있는 경우에만 is가 True고, 
# 그렇지 않으면 is는 False, == 만 True 
```

- 그래서 파이썬은 -5 ~ 256 범위의 정수, 자주 쓰는 짧은 문자열 등은 자동으로 인터닝 처리를 하는데, 이런 객체는 **계속 재사용**되기 때문에, 새로운 객체 생성을 줄이고 GC 비용도 주는 효과가 있다. 
- 그래서 개발자가 직접 인터닝을 신경 쓰고 싶을 때는? 
    - 자주 반복되는 문자열은 `sys.intern()`으로 intern 처리됨 → 비교 속도↑, 메모리↓

```python 
from sys import intern

a = intern("very_very_long_common_string")
b = intern("very_very_long_common_string")

# intern()으로 동일 객체 재사용 → 메모리 절약 + 비교 속도 향상
if a is b:
    ...
``` 

### cf. 참조 카운팅 내부 구조 이해하기 
- `참조 카운팅` = 객체가 참조되고 있는 횟수를 추적하여, **0이 되면 즉시 메모리 해제(GC)**하는 방식이다 
- 그래서 객체 수를 줄이거나 재사용(인터닝)하면 참조 관리 비용이 줄고 → 결과적으로 메모리 최적화에 기여하게 됨 
- 참조 카운팅을 확인하고 싶으면 `sys.getrefcount()`을 활용하면 된다 

```python
import sys

a = [1, 2, 3]
print(sys.getrefcount(a))  # 2 (로컬 변수 + getrefcount의 인자 자체)

b = a
print(sys.getrefcount(a))  # 3 (b도 참조 중)

del a
print(sys.getrefcount(b))  # 2 (a는 삭제됨, b만 남음)

del b  # 이제 참조 0 → 메모리 해제

# 참조 카운팅은 파이썬 객체의 생명주기를 자동으로 관리하는 핵심 원리로,
# 불필요한 객체 생성을 줄이고, 참조 수를 최소화하면 메모리 회수 효율이 높아져
# 결국 메모리 최적화에 직접적인 영향을 미친다
```

## 3. 약한 참조(Weak Reference)와 순환 참조(Circular Reference)
1. 순환 참조는 의도적으로 방지할 것 
2. 약한 참조는 의도적으로 사용할 것 
<!--  
- 약한 참조: 
    - 객체를 참조하되, 참조 카운트를 증가시키지 않음 
    - 객체가 GC로 사라져도 약한 참조는 자동으로 None이 됨 
- 순환 참조: 
    - 두 객체가 서로를 참조하면 참조 카운트가 0이 안 되어서, __del__()이 호출되지 않고 GC에 의존해야 하는 상황이 됨 -->

### 순환 참조 
- **순환 참조는 두 객체가 서로를 참조하고 있어서 둘 다 삭제되지 못하고 메모리에 남는 상황**에 발생한다

```python 
class Subject:
    def __init__(self):
        self.observers = []

    def register(self, observer):
        self.observers.append(observer)

class Observer:
    def __init__(self, subject):
        self.subject = subject
        subject.register(self)

s = Subject()
o = Observer(s)
``` 

- 파이썬의 기본 GC는 참조 카운트 기반이기 때문에, 위와 같이 서로를 참조하는 구조에서는 참조 카운트가 0이 되지 않아 메모리에서 해제되지 않게 된다 
    - 이게 누적되면 메모리 누수(memory leak) 발생 
- 그래서 실무에서는 이런 구조를 의도적으로 피하거나, 어쩔 수 없는 경우에는 GC가 메모리를 해제하기를 기다리거나 del, `gc.collect()`를 수동으로 호출하는 방법이 있는데 유지보수 측면에서 매우 위험하고 지저분한 코드가 될 수 있어 `약한 참조(weakref)`로 고리를 끊는 방법을 권장한다. 
    - 예: A가 B를 가지고 있고, B가 다시 A를 가지고 있는 구조 → 둘 다 지워도 메모리에 남아있는 좀비 객체가 될 수 있음

### 약한 참조 
- `weakref`는 객체 A가 객체 B를 참조해야 하는데, 객체 B의 생명주기를 A가 책임지지 않아야 할 때 사용한다 
- weakref를 통해 고리를 약하게 만들어 GC가 회수 가능하도록 하는 것이 포인트 
    - 객체가 소멸되면 약한 참조는 자동으로 None이 되므로 메모리 해제에 방해되지 않음 

```python 
import weakref

class Observer:
    def __init__(self, subject):
        self.subject = weakref.ref(subject)  # 👈 약한 참조
        subject.register(self)
``` 

## 4. 제너레이터 (yield)를 활용한 메모리 효율성
- return은 모든 결과를 한꺼번에 메모리에 올림
- yield는 한 번에 하나의 값만 생성하므로 메모리 효율적 
- 핵심 개념: `Lazy Evaluation(지연 평가)`
    - 제너레이터(yield)로

```python
import sys

# 메모리 비효율적인 방식 (전체 리스트 생성)
def get_large_list_bad(n):
    """전체 리스트를 메모리에 로드 - 메모리 비효율적"""
    return [i * i for i in range(n)]

# 메모리 효율적인 방식 (제너레이터)
def get_large_list_good(n):
    """제너레이터로 하나씩 생성 - 메모리 효율적"""
    for i in range(n):
        yield i * i

# 메모리 사용량 비교
n = 1000000

# 나쁜 방식: 전체 리스트 생성
print("=== 나쁜 방식 (전체 리스트) ===")
bad_list = get_large_list_bad(n)
print(f"리스트 크기: {sys.getsizeof(bad_list)} bytes")

# 좋은 방식: 제너레이터
print("\n=== 좋은 방식 (제너레이터) ===")
good_gen = get_large_list_good(n)
print(f"제너레이터 크기: {sys.getsizeof(good_gen)} bytes")

# 제너레이터 사용 예시
print("\n=== 제너레이터 활용 ===")
def process_large_file(filename):
    """대용량 파일을 메모리 효율적으로 처리"""
    with open(filename, 'r') as file:
        for line in file:  # 한 줄씩 읽기
            yield line.strip()

# 실제 사용 시
# for line in process_large_file('large_file.txt'):
#     process_line(line)  # 메모리 사용량 최소화
```

## 5. GC (가비지 컬렉터) 튜닝
- GC 튜닝을 통해 파이썬의 메모리 최적화를 시도할 수 있다. 
- 대표적으로 gc.set_threshold()로 GC 수집 주기를 조정하거나, 메모리 사용이 많은 블로 이후 gc.collect()로 수동 수집을 하여 메모리 사용량을 줄이는 방식이 있다. 
- 이는 객체 생성/소멸이 반복되거나 순환 참조가 많을 떄 메모리 릴리즈 시점을 제어해, CPU 낭비 방지 또는 메모리 누수 예방에 도움이 될 수 있다. 
- 하지만 GC 수동 제어는 잘못 쓰면 오히려 성능에 역효과를 줄 수 있다. 
예를 들어, gc.collect()를 너무 자주 호출하면 오히려 CPU 부하가 증가하고, 
반대로 GC를 너무 늦게 호출하면 사용되지 않는 객체가 계속 메모리에 남아 있어 메모리 누수 문제가 생길 수 있다.
따라서 반드시 **사전 분석 도구(e.g. tracemalloc)**로 메모리 누수나 과다 할당 구간을 확인하고, 수동 수집은 특정 요청 처리 이후 등 **명확한 경계가 있는 구간에만 제한적으로 적용**하는 방식으로 운영해야 한다. 

```python
import base64
import gc
import tracemalloc
import time
from PIL import Image
import io

def simulate_heavy_processing():
    """가상의 대용량 이미지 처리를 시뮬레이션"""
    # 5000x5000 이미지 생성 (메모리 사용량 큼)
    img = Image.new('RGB', (5000, 5000), color='white')

    # 메모리 스트림에 저장
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    byte_data = buffer.getvalue()

    # base64 인코딩
    encoded = base64.b64encode(byte_data).decode('utf-8')

    # 의도적으로 메모리 해제
    del img
    del buffer
    del byte_data
    del encoded


def display_top(snapshot, key_type='lineno', limit=5):
    print("[ top memory usage ]")
    top_stats = snapshot.statistics(key_type)

    for index, stat in enumerate(top_stats[:limit], 1):
        print(f"{index}. {stat}")
    total = sum(stat.size for stat in top_stats)
    print(f"Total allocated size (top {limit}): {total / 1024:.1f} KiB")


if __name__ == "__main__":
    tracemalloc.start()

    print("\n[ before processing ]")
    snapshot1 = tracemalloc.take_snapshot()
    display_top(snapshot1)

    simulate_heavy_processing()

    print("\n[ after processing (no gc) ]")
    snapshot2 = tracemalloc.take_snapshot()
    display_top(snapshot2)

    print("\n[ manual gc.collect() 실행 ]")
    gc.collect()
    time.sleep(1)  # GC가 완료되도록 약간 대기

    snapshot3 = tracemalloc.take_snapshot()
    print("\n[ after manual gc.collect() ]")
    display_top(snapshot3)

# 출력 예시 
```

### GC vs tracemalloc 
- gc 모듈 
    - 파이썬 내장 가비지 컬렉터(Garbage Collector) 제어용 모듈 
    - `gc.collect()` -> 수동으로 쓰레기 객체 수집 
    - `gc.get_stats(), gc.set_threshold()` -> GC 동작 기준/빈도 조절 
    - 보통 순환 참조가 GC 대상이 되는데, 수동 수집 안하면 Generation 2까지 버티기도 함 
        - cf. 파이썬의 GC는 **3세대(Generation 0,1,2)** 나뉘어 있고, 오래 살아남은 객체는 더 느리게 검사하는 전략을 쓴다. 이게 바로 "세대 기반 GC"이다.
        - 대부분의 객체는 생성 직후에 곧바로 죽는다. 따라서 "새로 생성된 애들만 자주 검사"하면 GC 속도가 빨라진다. 
        - 반면 오래 살아남은 애들은 자주 안봐도 된다 -> 비용 대비 효과가 적으니까. 
        위에서 Generation 2까지 버틴다는 것은 오래 살아남았다는 것이고, 이는 GC가 느리게 체크하고 메모리를 해제한다는 의미이다.

- tracemalloc 모듈 
    - 파이썬 3.4+ 내장된 메모리 추적 및 분석 도구 
    - 이름처럼 “메모리 할당을 추적(trace)“하고, 특정 시점의 스냅샷(snapshot) 을 찍어서 분석
    - `tracemalloc.start()` -> 추적 시작 
    - `tracemalloc.take_snapshot()` -> 메모리 상태 캡쳐 
    - `.statistivs('lineno')` -> 어느 파일/라인에서 메모리 가장 많이 잡아먹는지 출력 

### cf. PIL/Pillow 
- PIL = Python Imaging Library로 `pip install pillow`를 해야 사용 가능 
- Image 클래스에서 `Image.new('RGB', (5000, 5000), color='white')`를 하면 5000 x 5000 픽셀의 흰색 이미지를 생성하겠다는 것이고, RGB 컬러모드로 color='white'인 배경을 흰색으로 초기화 하겠다는 의미. 즉, 메모리 상에 이미지 객체를 만들고 저장은 하지 않은 상태를 의미
- 이미지 지우너 포맷은 'JPEG', 'PNG', 'BMP', 'GIF', 'TIFF', 'WEBP', 'ICO', 'PDF' 등 다수

### cf. io.BytesIO
- 파이썬의 입출력(IO) 작업을 메모리상에서 수행할 수 있는 가상 파일 객체
- 디스크에 저장하지 않고 메모리에 바이트 스트림 형태로 데이터를 다룸
- open('파일', 'wb') 대신 io.BytesIO()를 쓰면 임시 데이터 버퍼로 활용 가능
- `.save(buffer, format='JPEG')` -> 이미지를 JPEG 포맷으로 buffer에 저장하겠다는 것. 즉, 메모리 내에서 JPEG 인코딩된 바이트가 생성이 된다는 의미. 
- `byte_data = buffer.getvalue()` -> BytesIO 버퍼에 저장된 모든 바이트 데이터를 꺼내서 반환. 이 결과는 bytes 객체이며, base64로 인코딩하는데 사용됨 


### cf. base64 인코딩 / 디코딩 관련 
- 바이트와 base64는 다르다!
    - 바이트: 이미지처럼 인코딩된 binary data 
    - base64: 바이트 데이터를 문자열(text)로 안전하게 바꾸는 인코딩 방식 
        - 예: 이미지 파일을 API로 전송할 때 binary 그대로 보내면 깨질 수 있음. 그래서 텍스트 기반 인코딩(base64)를 사용. 
        - bytes 타입으로 base64 인코딩된 결과 (예: b'/9j/4AAQSkZJRgABAQAAAQABAAD...').
        이걸 .decode("utf-8")로 UTF-8 문자열로 변환하면 API 전송이나 JSON 포함할 때 문자열로 전송되어 안깨짐! 
        
## 6. 적절한 자료구조 선택 전략 
- 데이터의 성격에 따라 적절한 자료 구조를 선택하는 것만으로도 메모리 효율과 성능을 크게 개선할 수 있다. 예를 들어, 고정된 불변 데이터에는 리스트보다 튜플, 수치 데이터 배열에는 array.array, 큐 구조에는 list 대신 deque를 써서 O(n)연산을 O(1)로 줄일 수 있다. 

### tuple vs list 
- 튜플은 불변이고, 리스트는 가변이다. 메모리 사용량 측면에서 보면 이는 튜플은 메모리 사용량이 더 적고, 리스트는 상대적으로 크다고 볼 수 있다. 
또한 튜플은 해시 가능한 불변 객체이기 때문에 dict의 key 등으로 사용하면 더 빠른 장점이 있고, 리스트는 가변 객체라 해시 불가하다. 따라서 삽입/삭제에는 유연하지만 key로 바로 찾을 수 없기 때문에 시간복잡도가 더 높다. 따라서 키로 사용하거나 고정된 구조에서는 튜플을, 동적 데이터 추가/삭제할 일이 있다면 리스트를 사용하는 것이 좋다. 

### dict vs namedtuple vs dataclass(slot=True)

|항목|dict|namedtuple|dataclass(slots=True)|
|--------|--------|--------|--------|
|속성 정의|동적|고정|고정|
|가변성|가변|불변|가변|
|메모리 효율|가장 낮음|가장 높음|중간 이상|
|가독성/IDE 지원|낮음|높음|높음|
|추가 메서드|X|X|O (메서드 정의 가능)|

- 요약:
    -  데이터 구조가 정해져 있으면 dict보다 namedtuple 또는 dataclass(slots=True)
    - 속성 변경 필요하면 dataclass
    - 메모리 많이 쓰는 서비스에서는 dict 대신 dataclass(slots=True) 사용하면 수천 객체 기준 큰 절감 가능. (cf. dataclass(slots=True)는 내부적으로 __slots__을 사용해 인스턴스마다 __dict__를 생성하지 않도록 막기 때문에 수천 개 인스턴스를 생성하는 경우 메모리 절감 효과가 크다)

### set vs list (중복 제거 & 포함 검사)
- set은 중복을 허용하지 않고, list는 허용한다. 순서도 set은 삽입 순서가 유지되지 않지만 리스트는 삽입 순서가 보존된다. in 연산자로 포함 여부를 확인하는 경우 set은 O(1) 시간복잡도를 유지하지만 리스트는 O(n) 정도를 유지한다. 
- 따라서 set은 중복 제거, 빠른 검색에 유용하고, 리스트는 순차처리나 정렬에 유용하게 사용될 수 있다. 

### list vs array.array
- 리스트는 다양한 자료형이 혼합해서 들어갈 수 있지만, array.array는 하나의 타입으로 고정해서 들어간다. 메모리 효율 측면에서 array.array가 더 높기 때문에 수치 연산이 많거나 정수/실수처럼 단일 타입 숫자 데이터만 들어가는 배열의 경우 array.array가 더 유용하다. 
(cf. but 단순 수치형 배열에는 array.array가 효율적이지만, 대부분의 실무에서는 numpy의 ndarray가 훨씬 강력하고 범용적으로 쓰인다)

### list vs deque (큐/스택 자료 구조)
- 큐나 스택을 구현할 때, 일반 list보다 `from collections import deque`를 활용해서 큐/스택을 구현하면 더 빠르다. 특히 양방향 삽입/삭제가 필요한 구조라면 deque는 필수이다. 
(cf. list로 큐를 구현하면 pop(0) 시 전체 요소를 앞으로 밀어야 하므로 O(n)의 시간복잡도를 가지지만, deque는 popleft()가 O(1)이므로 대기열 구조에 적합하다)

---

<details>
<summary>cf. reference</summary>

- 
</details>
