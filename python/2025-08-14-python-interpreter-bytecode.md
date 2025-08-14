---
title: "파이썬은 왜 느릴까? 인터프리터 구조부터 바이트코드까지"
date: 2025-08-14
categories:
  - python
tags:
  - interpreter
  - bytecode
  - gil
  - ast
  - pvm
  - cpython
  - jit
  - pypy
---

# 파이썬은 왜 느릴까? 인터프리터 구조부터 바이트코드까지

## 1. Python은 인터프리터 언어인가요? 컴파일 과정 설명해 주세요.

### 기본 답변
- **Python은 전통적으로 인터프리터 언어로 분류**되지만, 엄밀히 말하면 **"컴파일 + 인터프리터 혼합 구조"**입니다
- Python은 실행 전 .py 소스코드를 내부적으로 AST로 파싱하고, 이를 Python 전용 바이트코드(.pyc)로 변환(transfile)한 뒤, Python Virtual Machine(PVM)에서 한 줄씩 해석하며 실행합니다.
- 실행 흐름: **소스코드 → AST → 바이트코드 → PVM 실행**

### 인터프리터 언어 vs 컴파일 언어

#### 핵심 차이점
**인터프리터 언어**: 소스코드를 실행 시점에 해석하여 실행 (Python, JavaScript, PHP)  
**컴파일 언어**: 소스코드를 미리 기계어로 변환하여 실행 (C/C++, Go, Java)

#### 대표적인 인터프리터 언어
- **Python**: 바이트코드로 컴파일 후 PVM에서 실행
- **JavaScript**: V8 엔진에서 바이트코드로 컴파일 후 실행
- **PHP**: Zend 엔진에서 바이트코드로 컴파일 후 실행

#### 대표적인 컴파일 언어
- **C/C++**: 소스코드를 직접 기계어로 컴파일
- **Go**: 소스코드를 기계어로 컴파일
- **Java**: 소스코드를 바이트코드로 컴파일 후 JVM에서 실행

#### 주요 차이점
| 구분 | 인터프리터 언어 | 컴파일 언어 |
|------|----------------|-------------|
| **실행 속도** | 상대적으로 느림 | 빠름 |
| **플랫폼 독립성** | 높음 (VM/인터프리터만 있으면 실행) | 낮음 (플랫폼별 컴파일 필요) |
| **개발 편의성** | 높음 (즉시 실행, 디버깅 용이) | 낮음 (컴파일 과정 필요) |
| **메모리 사용량** | 상대적으로 많음 | 적음 |
| **에러 발견** | 런타임에 발견 | 컴파일 타임에 발견 |

### Python 혼합 구조의 장단점

#### 장점
- **빠른 시작**: 바이트코드 캐싱으로 두 번째 실행부터 빠름
- **플랫폼 독립성**: PVM만 있으면 어디서든 실행 가능
- **개발 편의성**: 컴파일 과정 없이 즉시 실행 가능
- **최적화 기회**: 바이트코드 단계에서 일부 최적화 수행

#### 단점
- **초기 지연**: 첫 실행 시 컴파일 오버헤드
- **메모리 사용**: 바이트코드와 PVM이 추가 메모리 사용
- **실행 속도**: 순수 컴파일 언어보다 느림
- **복잡성**: 컴파일과 인터프리터 과정을 모두 거쳐야 함

### CPython에서의 구체적인 실행 흐름
1. **소스 코드 파싱**: 소스 코드를 파싱하여 AST(Abstract Syntax Tree) 생성
2. **바이트코드 생성**: AST를 기반으로 바이트코드 생성
3. **캐싱**: 바이트코드는 `.pyc` 파일로 캐시될 수 있음
4. **실행**: Python Virtual Machine(PVM)이 바이트코드를 실행
```
소스코드 → AST → 바이트코드 → PVM
```

## 2. Python vs CPython, 무엇이 다른가요?
### Python과 CPython의 관계
- **Python**: 프로그래밍 언어 자체의 이름 (문법, 규칙, 표준)
- **CPython**: Python 언어를 구현한 구체적인 프로그램 (인터프리터)

### 쉽게 설명하면
- **Python** = 언어의 설계도 (어떻게 코드를 작성할지 정의)
- **CPython** = 그 설계도를 실제로 구현한 프로그램 (코드를 실행하는 엔진)

### Python 구현체들
Python 언어를 실행할 수 있는 여러 구현체가 있습니다:

#### CPython (가장 일반적)
- **C로 작성**된 Python 인터프리터
- **공식 레퍼런스 구현체**
- `python` 명령어로 실행하는 것이 대부분 CPython
- **GIL 사용**, 안정성과 호환성이 높음

#### PyPy
- **Python으로 작성**된 Python 인터프리터
- **JIT 컴파일러** 사용으로 성능 향상
- 메모리 사용량이 더 많음

#### Jython
- **Java로 작성**된 Python 인터프리터
- Java 플랫폼에서 실행
- Java 라이브러리와 연동 가능

#### IronPython
- **C#으로 작성**된 Python 인터프리터
- .NET 플랫폼에서 실행

### 왜 CPython을 사용하나요?
1. **표준**: Python 공식 구현체
2. **안정성**: 가장 검증되고 안정적
3. **호환성**: 모든 Python 라이브러리와 호환
4. **성숙도**: 오랫동안 개발되어 안정적
5. **커뮤니티**: 가장 큰 사용자 커뮤니티와 지원

## 3. AST(Abstract Syntax Tree)란 무엇인가요?

### AST의 정의
- ast는 **Abstract Syntax Tree**를 생성하고 조작할 수 있게 해주는 표준 Python 내부 모듈로, 쉽게 말하면:
    - 파이썬 코드를 트리 구조로 바꿔서 내부 구조를 분석하거나, 자동 수정하거나, 검사하는데 쓰는 도구입니다
- 파이썬 소스 코드는 실행 전에 AST로 변환되어 바이트코드를 생성하는데 활용됩니다. 
- 예: 
```python
import ast

code = """
def greet(name):
    print("Hello", name)
"""

tree = ast.parse(code) # 파이썬 소스 문자열을 AST로 변환 
print(ast.dump(tree, indent=4)) # 트리 구조를 문자열로 출력 
# cf. 
# ast.NodeVisitor, NodeTransformer: 노드를 순회하거나 변경할 때 사용

"""
e.g. 
Module(
    body=[
        FunctionDef(
            name='greet',
            args=arguments(
                args=[
                    arg(arg='name')]),
            body=[
                Expr(
                    value=Call(
                        func=Name(id='print', ctx=Load()),
                        args=[
                            Constant(value='Hello'),
                            Name(id='name', ctx=Load())]))])])
"""
```

### AST를 사용하는 이유?
- 정적 분석: 문법 검사, 코드 규칙 위반 탐지
- 코드 변환/최적화: 자동 리팩터링, 코드 생성기
- 보안 점검: eval, exec 등의 위험 코드 탐지
- 개발 도구 제작: 나만의 린터, 코드 검사기
```text 
[요약]
“AST는 Abstract Syntax Tree의 약자로, 파이썬 코드가 실행되기 전에 내부적으로 트리 구조로 파싱된 중간 표현입니다.
파이썬 소스코드는 먼저 AST로 변환된 후, 바이트코드로 컴파일되고, 마지막으로 PVM(Python Virtual Machine)이 이 바이트코드를 한 줄씩 읽어가며 실행하게 됩니다.
또한, Python의 ast 모듈을 사용하면 이 AST 구조를 직접 조회하거나, 코드를 분석·변환하는 작업도 가능해서 정적 분석 도구나 리팩터링 툴 등에 활용됩니다.”
```

## 4. PVM(Python Virtual Machine)이란 무엇인가요?
- **Python Virtual Machine**: Python의 바이트코드를 실행하는 가상 머신으로, 바이트코드를 한 줄씩 읽어가며 실행하는 역할을 수행합니다. 
(- PVM 자체는 이미 네이티브 코드(기계어)로 빌드된 프로그램으로 바이트코드를 해석(interpret)하면서 내부에서 필요한 연산을 수행할 때 CPU를 사용하는 것. 즉, CPU에 위치하거나 하는게 아니고 이 PVM이라는 가상 머신에서 바이트코드를 해석하고 실행할 때, 즉 연산에 CPU를 사용하는 개념)

### PVM 작동 원리 요약 
- 파이썬 소스코드는 실행 시 다음 과정을 거칩니다:
```text
.py (소스 코드)
    ↓ ① 파싱 및 AST 생성
AST (추상 구문 트리)
    ↓ ② 바이트코드 컴파일
.pyc (바이트코드)
    ↓ ③ Python Virtual Machine(PVM)
실행 결과

=> 즉, PVM은 Python 바이트코드를 실제로 실행하는 인터프리터입니다.
```

|단계|설명|
|--------------|--------------------------------------------------------|
|1. 파싱|.py 파일의 소스코드는 **파서(Parser)**에 의해 읽히고, **AST(Abstract Syntax Tree)**로 변환됨|
|2. 컴파일|AST는 **바이트코드(bytecode)**로 컴파일되며, 이는 사람이 읽을 수 없는 중간 단계 코드임 → 보통 .pyc로 캐싱됨|
|3. PVM 실행|Python Virtual Machine이 이 바이트코드를 한 줄씩 읽고 실행함 → 인터프리터처럼 동작|
|4. 실행 흐름 제어|조건문, 반복문, 함수 호출, 예외 처리 등을 PVM이 관리하는 내부 스택 구조로 처리함|
|5. 메모리 관리|변수, 객체, 참조, GC(가비지 컬렉션)도 PVM 내부 메모리 매니저가 처리|
|6. 최종 결과 출력|실행 결과가 stdout 또는 프로그램 결과로 출력됨|

#### cf. Python 바이트코드 확인하는 내장 모듈 -> dis 
- 예시: 
```python 
cf. 바이트코드는 dis 모듈을 통해 확인 가능!
import dis

def example():
    return sum([1, 2, 3])

dis.dis(example)
# e.g. 출력하면 ...
#  34           RESUME                   0

#  35           LOAD_GLOBAL              1 (sum + NULL)
#               BUILD_LIST               0
#               LOAD_CONST               1 ((1, 2, 3))
#               LIST_EXTEND              1
#               CALL                     1
#               RETURN_VALUE

# 설명: 
#  34           RESUME                   0
#               └─ Python 3.11+부터 등장한 초기 명령어로, 함수 실행 준비를 마친 후 실행 재개를 의미합니다. (코루틴 및 디버깅 용도 포함)

#  35           LOAD_GLOBAL              1 (sum + NULL)
#               └─ 전역 네임스페이스에서 'sum' 함수를 불러옵니다. 이때 'NULL'은 디폴트 인수나 바인딩 여부 확인용으로 붙음

#               BUILD_LIST               0
#               └─ 비어있는 리스트 객체를 하나 생성합니다. (초기 용량 0)

#               LOAD_CONST               1 ((1, 2, 3))
#               └─ 상수 풀에서 튜플 (1, 2, 3)을 로드합니다

#               LIST_EXTEND              1
#               └─ 앞에서 만든 빈 리스트에 튜플 (1, 2, 3)을 unpack해서 추가합니다 → [1, 2, 3] 형태로 변경

#               CALL                     1
#               └─ 'sum' 함수 호출. 인자 1개([1, 2, 3])를 넘겨서 sum([1, 2, 3]) 실행

#               RETURN_VALUE
#               └─ sum 함수의 반환값을 이 함수의 결과로 반환합니다
``` 


#### GIL(Global Interpreter Lock)이란?
- CPython의 메모리 관리 안전성을 보장하기 위해 도입된 락
    - CPython의 Garbage Collection(GC)는 객체의 메모리를 관리할 떄 **레퍼런스 카운팅**(reference counting)을 기본 방식으로 사용(즉, 각 객체는 내부적으로 "지금 몇 개의 변수가 나를 참조하고 있는가"를 숫자로 가지고 있는다)한다.
    - 이때 멀티스레드 환경에서 동시에 레퍼런스 카운트를 조작하면, 동시에 레퍼런스 카운트를 한쪽 스레드에서는 +1, 한쪽 스레드에서는 -1을 하면 `race condition`(경쟁 상태)가 발생 가능하게 되고, 잘못된 reference count를 갖게되고, 메모리 누수 또는 조기 해제(crash)가 나게된다. 
    - 따라서 이러한 문제점에 의해 CPython은 한번에 하나의 스레드만 파이썬 바이트코드를 실행하도록 강제하는 전역 락(GIL)을 도입했다.
    - 즉, GIL 덕분에 reference count 변경은 항상 안전하게 작동하지만, 모든 바이트코드 실행은 GIL을 획득한 스레드만 가능하게 되어 멀티 스레드 환경에서 병렬처리가 불가하다  
- 한 번에 하나의 스레드만 Python 바이트코드를 실행할 수 있게 제한함
- 즉, 멀티스레드를 사용해도 CPU 병렬 실행이 불가능함
- 왜 존재할까?
	- CPython의 레퍼런스 카운팅 기반 GC는 thread-safe하지 않기 때문
	- GIL이 없다면 동시에 객체를 참조/해제하는 과정에서 충돌 발생 가능
- GIL의 문제점
    - 멀티스레드로 CPU-bound 작업 처리 시 성능 저하
    - 특히 머신러닝, 대규모 수치 연산 등 CPU 연산이 많은 작업에서 병목 발생
- 우회 방법 

|상황|우회 방법|설명|
|----------------|----------------|----------------------------|
|CPU-bound|multiprocessing|프로세스 단위로 병렬 실행 (GIL 무효)|
|I/O-bound|asyncio, aiohttp|GIL 영향 거의 없음 (비동기 처리)|
|특수한 경우|Cython, Numba|GIL 해제하고 네이티브 코드 실행|
|아예 다른 인터프리터|Jython, IronPython 등|GIL 없음 (단, 생태계 제약 있음)



### PVM의 역할
- 바이트코드 로딩: 컴파일 된 .pyc 파일을 읽음  
- 실행 흐름 관리: 바이트코드를 한 줄씩 해석하며 실행
- 메모리 관리: 변수, 객체, 참조 등 메모리 구조 관리 
- 예외 처리: try-except 블록, 에러 핸들링 
- 함수 호출/스택: call stack, frame 관리 
- 모듈 import: import 시 내부적으로 PVM이 모듈 로딩 


## 5. CPython이란 무엇인가요?

### CPython의 정의
- **CPython**: 
- CPython은 Python 언어의 공식 구현체이며, C언어로 작성된 인터프리터(PVM 포함)다.
- 일반적으로 설치하는 `python` 명령어는 대부분 CPython

### 다른 Python 구현체들과의 차이점

#### PyPy
- PyPy는 Python으로 작성된 Python 인터프리터이며, **JIT(Just-In-Time) 컴파일러** 를 탑재한 고성는 Python 구현체이다
- 반복 연산에서 매우 빠름
- 메모리 사용량이 더 많음

#### Jython
- Java 플랫폼용 Python 구현체
- Java 생태계와의 통합을 위해 사용

#### IronPython
- .NET 플랫폼용 Python 구현체

### CPython의 특징
- **GIL(Global Interpreter Lock) 사용**: 멀티스레딩 한계
- **안정성과 호환성**: 가장 높은 수준
- **메모리 효율성**: 상대적으로 적은 메모리 사용

## 6. JIT(Just-In-Time) 컴파일이란 무엇인가요?

### JIT 컴파일의 개념
- **Just-In-Time**: 실행 시점에 자주 사용되는 코드를 네이티브 코드로 컴파일 
    - 일반적인 인터프리터는 한줄씩 해석하고 실행, 이렇게 진행하는데 JIT은 그 중 반복적으로 많이 쓰이는 코드를 골라서 **미리 기계어로 변환해두고 빠르게 실행**하는 방식이다.
- **핫스팟(자주 실행되는 부분) 최적화**: 자주 실행되는 부분을 동적으로 최적화

### PyPy에서의 JIT 동작
- Python의 공식 구현체인 CPython은 JIT을 사용하지 않음. 하지만 PyPy는 Python을 빠르게 돌리기 위해 JIT을 도입함.
```python
# 예시: 반복문에서 JIT의 효과
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# 처음 실행: 인터프리터 모드로 실행
# 자주 호출되는 부분: JIT 컴파일로 네이티브 코드 생성
# 결과: 반복 연산에서 상당한 성능 향상
```

### 인터프리터 vs JIT vs AOT 컴파일러 
|구분|특징|
|-------|-------------------------------------------------|
|인터프리터|실행 시 한 줄씩 해석 (느림)|
|AOT(Ahead-of-Time)|실행 전에 전체 코드 컴파일 (빠름, ex: C/C++)|
|JIT|실행 중 자주 쓰이는 부분만 기계어로 변환 (동적 최적화)|

### JIT의 장단점
**장점:**
- 반복 연산에서 큰 성능 향상
- 동적 최적화로 런타임에 최적의 코드 생성

**단점:**
- 초기 실행 시 컴파일 오버헤드
- 메모리 사용량 증가
- 모든 코드에 대해 효과적이지 않음

## 7. Python이 느린 이유와 최적화 방안

### Python이 느린 주요 원인

#### 1. 인터프리터 방식
- Python은 바이트코드를 한 줄씩 해석하며 실행하는 구조라, 컴파일 언어보다 실행 속도가 느림

#### 2. GIL(Global Interpreter Lock)
- CPython에서 하나의 스레드만 Python 바이트코드를 실행할 수 있어, 멀티코어(멀티스레드) 환경에서 CPU 바운드 작업 병렬 처리 제한
- 단일 스레드만 Python 바이트코드 실행 가능

#### 3. 동적 타입 시스템
- 변수의 타입이 런타임에 결정되므로 타입 체크/추론 비용이 추가 발생

#### 4. 메모리 관리 오버헤드 
- 참조 카운트 기반 GC + 순환 참조 탐지(GC overhead)로 인해 메모리 관리 비용이 큼

#### 5. 내부 자료구조 최적화 부족 
- 리스트, 딕셔너리 등 고수준 자료구조 사용이 잦아 메모리 및 연산 성능 손실 발생


### 최적화 방안

#### 1. 알고리즘 최적화 (Algorithm Optimization)
**가장 강력한 성능 향상 방법**: 시간 복잡도 개선
```python
# 느린 방식 (O(n²))
def find_duplicates_slow(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates

# 빠른 방식 (O(n)) - set 활용
def find_duplicates_fast(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)

# 내장 자료구조 활용
# 느린 방식
if item in large_list:  # O(n)

# 빠른 방식
if item in large_set:   # O(1)
```

#### 2. C 확장 활용 (Utilize C Extensions)
**계산 성능 극대화**: C 기반 라이브러리 활용
```python
# 순수 Python - 느림
def calculate_sum_python(data):
    total = 0
    for item in data:
        total += item
    return total

# NumPy 활용 - 빠름
import numpy as np
def calculate_sum_numpy(data):
    return np.sum(data)

# Pandas 활용
import pandas as pd
df = pd.DataFrame(large_data)
result = df.groupby('category')['value'].sum()

# scikit-learn 활용
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier()
clf.fit(X_train, y_train)
```

#### 3. JIT 컴파일러 사용 (Use JIT Compiler)
**반복 연산에서 수십 배 성능 향상**: PyPy 등 JIT 지원 인터프리터 사용
```python
# CPython에서 실행 시 느림
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# PyPy에서 실행 시 JIT 컴파일로 빠름
# 자주 호출되는 부분이 네이티브 코드로 컴파일됨
for i in range(1000):
    result = fibonacci(i)

# PyPy는 CPython과 완전히 별개의 인터프리터라 
# main_app.py          → CPython
# jit_optimized_part.py → PyPy로 실행 (subprocess or REST API)
# 이렇게 나누고 ... 
# main_app.py
import subprocess

subprocess.run(["pypy", "jit_optimized_part.py"])
# 이런식으로 분리해서 실행하면 두개의 다른 인터프리터를 돌릴 수 있게 된다 
```

#### 4. 멀티프로세싱 사용 (Use Multiprocessing)
**GIL 우회**: `multiprocessing`으로 CPU 병렬 처리, `asyncio`로 I/O 병렬 처리
```python
# 멀티프로세싱으로 CPU 바운드 작업 병렬 처리
from multiprocessing import Pool

def cpu_intensive_task(n):
    return sum(i * i for i in range(n))

if __name__ == '__main__':
    with Pool(4) as pool:
        results = pool.map(cpu_intensive_task, range(1000, 10000, 1000))

# asyncio로 I/O 병렬 처리
import asyncio
import aiohttp

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()

async def fetch_all_urls(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

#### 5. Cython, Numba
**C 수준 성능**: Python 코드를 컴파일하거나 최적화
```python
# Cython 예시 (파일명: example.pyx)
# cythonize로 컴파일 후 사용
def cython_fibonacci(int n):
    cdef int a = 0, b = 1, i
    for i in range(n):
        a, b = b, a + b
    return a

# Numba 예시
from numba import jit

@jit(nopython=True)
def numba_fibonacci(n):
    if n <= 1:
        return n
    return numba_fibonacci(n-1) + numba_fibonacci(n-2)
```

#### 6. 반복문 최소화 (Minimize Loops)
**고수준 문법 활용**: 벡터 연산, 리스트 컴프리헨션으로 루프 최소화
```python
# 느린 방식 - 전통적인 루프
def process_data_slow(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

# 빠른 방식 - 리스트 컴프리헨션
def process_data_fast(data):
    return [item * 2 for item in data if item > 0]

# 벡터 연산 활용
import numpy as np
data = np.array([1, 2, 3, 4, 5])
result = data[data > 0] * 2  # 벡터화된 연산

# map, filter, reduce 활용
from functools import reduce
numbers = [1, 2, 3, 4, 5]
squared_sum = reduce(lambda x, y: x + y, map(lambda x: x**2, filter(lambda x: x > 0, numbers)))
```

### 기타: C#이나 Java에서 병렬 처리 = 멀티스레딩일까? 멀티프로세싱일까?
- 기본 전제: C# / Java는 GIL이 없음
    - Python: GIL 때문에 스레드가 동시에 실행 불가 → 멀티프로세싱으로 회피
    - C# / Java: GIL 없음 → 진짜 멀티스레딩 병렬 처리 가능
- 결론: 

|언어|병렬 처리 기본 전략|GIL 유무|병렬 처리 방식|
|-------|----------------------------|------|---------------------|
|Python|멀티프로세싱 (CPU-bound), asyncio (I/O)|✅ 있음|프로세스 기반 병렬화|
|Java|멀티스레딩 (Thread, ExecutorService)|❌ 없음|스레드 기반 병렬화|
|C# (.NET)|멀티스레딩 (Task, Thread, TPL)|❌ 없음|스레드 기반 병렬화



## 8. 면접 질문 & 답변 

### Q: Python이 느리다고 평가받는 이유는 뭔가요? 
**A:** Python이 느리다고 평가받는 이유는 다음과 같습니다:

1. **인터프리터 기반 구조**: 바이트코드를 한 줄씩 실행해야 하므로 컴파일 언어보다 느림
2. **GIL(Global Interpreter Lock)**: 멀티코어 환경에서의 병렬 처리에 제약
3. **동적 타이핑**: 타입 체크나 추론 과정에서 런타임 오버헤드 발생
4. **메모리 관리**: 참조 카운트 기반 GC와 순환 참조 탐지로 인한 오버헤드

**해결 방안**:
- 고성능 연산: NumPy, Pandas 등 C 기반 라이브러리 활용
- 병렬 처리: multiprocessing, asyncio 활용
- 성능 최적화: PyPy(JIT), Cython, Numba 등 활용

**결론**: Python은 생산성과 유연성을 우선시하므로, 적절한 도구 선택과 아키텍처 설계로 병목 지점을 완화해야 합니다.

### Q: Python이 컴파일 언어인가요, 인터프리터 언어인가요?
**A:** Python은 "컴파일 + 인터프리터 혼합 구조"입니다. 소스코드를 바이트코드로 컴파일한 후, PVM에서 인터프리터 방식으로 실행합니다.
(PVM은 파이썬 바이트코드를 실제로 실행하는 가상 머신입니다. Python 소스 코드는 AST와 바이트코드로 변환된 후, 최종적으로는 PVM이 한 줄씩 실행하게 됩니다. 그래서 파이썬은 인터프리터 언어이지만, 내부적으로는 ‘컴파일 + 인터프리트’ 구조를 가지고 있다고 말할 수 있습니다.)

### Q: .pyc 파일은 무엇인가요?
**A:** Python이 소스코드를 바이트코드로 컴파일한 결과물입니다. 다음 실행 시 컴파일 과정을 생략하여 시작 속도를 향상시킵니다.

### Q: PyPy가 CPython보다 빠른 이유는?
**A:** JIT 컴파일러를 사용하여 자주 실행되는 코드를 네이티브 코드로 컴파일하기 때문입니다. 특히 반복 연산에서 큰 성능 향상을 보입니다.

### Q: Python의 성능을 개선하는 방법은?
**A:** 
1. 적절한 자료구조 선택 (set, dict 활용)
2. 리스트 컴프리헨션 사용
3. C 확장 모듈 활용 (NumPy, Pandas)
4. 비동기 프로그래밍 (asyncio)
5. 프로파일링을 통한 병목 지점 파악

### Q: GIL로 인한 성능 병목을 극복하려면 어떻게 해야 하나요?
**A:** Python은 GIL로 인해 스레드 기반 병렬 처리에 제약이 있습니다. 하지만 실무에서는 다음과 같은 방식으로 GIL을 우회합니다:

1. **multiprocessing**: 프로세스 병렬화로 GIL 우회
2. **asyncio**: I/O 최적화를 통한 비동기 처리
3. **Numba/Cython**: JIT/C 확장으로 성능 향상
4. **외부 인터프리터**: PyPy 등 다른 Python 구현체 활용

### Q: multiprocessing과 subprocess의 차이를 설명해주세요.
**A:** 
- **multiprocessing**: 파이썬 함수들을 병렬로 실행하기 위한 라이브러리로, GIL을 피하기 위해 독립적인 프로세스를 여러 개 띄웁니다.
- **subprocess**: 외부 프로그램이나 shell 명령어를 실행하기 위한 용도로, 파이썬 코드 외의 작업을 수행할 때 주로 사용됩니다.

### Q: Python은 멀티스레딩이 있는데 왜 멀티프로세싱을 사용하나요?
**A:** Python의 GIL(Global Interpreter Lock) 때문에, 하나의 프로세스 내에서는 한 번에 하나의 스레드만 Python 바이트코드를 실행할 수 있습니다.

따라서 CPU-bound 작업에서는 threading 모듈을 써도 병렬 처리 이점이 없고, 오히려 context switching 오버헤드만 생깁니다.

**해결책**: multiprocessing을 사용해 GIL을 우회하고, 각 프로세스가 병렬로 실행되도록 합니다.

**참고**: C#, Java는 GIL이 없어서 일반적으로 스레드 기반 병렬 API(Thread, Task 등)로 병렬 처리합니다.


---

<details>
<summary>cf. reference</summary>

- 

</details> 

