---
title: "Python 클로저, 데코레이터, 고차 함수(HOF)"
date: 2025-08-19
categories:
  - python
tags:
  - closure
  - decorator
  - higher-order-function
  - functional-programming 
---

# Python 클로저, 데코레이터, 고차 함수(HOF, Higher-Order Function)

## 함수형 프로그래밍 (Functional Programming, FP)이란?
- 데이터를 변경하지 않고, 순수 함수를 조합하여 프로그램을 구성하는 방식이다
- 함수를 "값(value)"처럼 다루는 프로그래밍 패러다임이다
- 파이썬은 "함수형 프로그래밍을 "지원"하는 객체지향 언어"이다. (파이썬은 본질적으로는 객체지향 언어이고, 함수형 스타일을 부분적으로 도입/지원하는 언어!)
    - 예: 람다 함수, 고차 함수, 클로저, 데코레이터, 제너레이터, 컴프리헨션, 불변 자료형 
- 파이썬 함수형 스타일 코딩의 핵심은 함수를 객체처럼 다룰 수 있다는 점이고,
그걸 잘 보여주는 개념들이 클로저, 고차 함수, 데코레이터이다. 
위의 개념들에 대해 알아보자! 

## 1. 개념 및 관계
### 1.1 세 개념의 연결고리

클로저, HOF, 데코레이터는 서로 밀접하게 연결된 개념이다. 

| 개념 | 설명 | 관계 |
|------|------|------|
| **클로저 (Closure)** | 외부 함수의 변수를 내부 함수가 기억하는 구조 | 데코레이터와 HOF의 기초가 되는 개념 |
| **HOF (Higher-Order Function)** | 함수를 인자로 받거나, 함수를 리턴하는 함수 | 데코레이터도 결국 HOF의 한 형태 |
| **데코레이터 (Decorator)** | 기존 함수를 수정하지 않고, 감싸서 기능을 확장하는 문법적 슈가(syntax sugar) | 보통 클로저 + HOF 조합으로 구현 |

### 1.2 클로저 (Closure) 
- 클로저는 내부 함수가 외부 함수의 지역변수를 기억하고 있는 상태를 의미한다.

```python
def outer_function(x):
    """외부 함수"""
    def inner_function(y):
        """내부 함수 - 클로저"""
        return x + y  # 외부 함수의 변수 x를 기억
    return inner_function

# 클로저 생성
add_five = outer_function(5) # outer_function의 인자로 들어감 
add_ten = outer_function(10)

# outer_function의 인자 x를 기억하는 inner_function의 인자로 각각 3을 넘겨줌 
# 이떄 add_five는 return x + y 와 같은 함수가 되는데, 이미 위에서 x를 넘겨줬으니 지금 넘겨받은 y만 대입해서 return 해주는 함수가 되는 것
print(add_five(3))   # 8 (5 + 3)
print(add_ten(3))    # 13 (10 + 3)

# 클로저의 상태 확인
print(f"add_five.__closure__: {add_five.__closure__}")
print(f"add_five.__closure__[0].cell_contents: {add_five.__closure__[0].cell_contents}")
```

**클로저의 핵심 포인트:**
- 외부 함수의 변수는 `__closure__` 속성에 저장됨
    - 즉, `__closure__` 속성은 "이 함수가 기억하고 있는 외부 변수들"을 보여주는 역할
- 각 클로저는 자신만의 독립적인 상태를 가짐
- 메모리에 변수 값이 계속 유지됨

**`nonlocal` 키워드:**
클로저에서 외부 변수 값을 내부 함수에서 변경하려면 `nonlocal`이 필요하다.

```python
def counter():
    count = 0
    def increment():
        nonlocal count  # 외부 함수의 count 변수를 수정하려면 nonlocal 키워드 필요!
        count += 1
        return count
    return increment

# 사용 예시
counter_func = counter()
print(counter_func())  # 1
print(counter_func())  # 2
print(counter_func())  # 3
```

### 1.3 HOF (Higher-Order Function) - 고차 함수
- HOF는 함수를 인자로 받거나, 함수를 반환하는 함수이다.
- 결국 고차 함수는 클로저를 통해 함수를 인자로 받거나, 함수를 반환할 수 있는 것이다.
- 다시, 고차 함수는 함수로 인자로 받거나, 함수를 반환하는 함수. 이 두 조건 중 하나만 만족해도 고차 함수라고 부를 수 있는건데, 클로저는 고차 함수의 "결과물" 중 하나라고 볼 수 있는 것.
    - 고차 함수가 함수를 반환할 때, 그 반환된 함수가 외부 변수에 접근하고 기억하면 → 클로저가 되는 것
    - 예: 위의 예시에서 outer_function()은 고차 함수, inner_function()은 클로저(outer_function()의 지역 변수 x를 기억하고 있음)
    - => 고차 함수는 클로저를 만들어낼 수 있는 함수 구조고, 클로저는 그 안에서 만들어진 상태 기억하는 함수라고 보면 된다

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

### 1.4 데코레이터 (Decorator)
- 데코레이터는 함수를 인자로 받아서, 기능을 확장한 후 다시 함수로 반환하는 구조이다. 
- 예시 1: 

```python
def my_decorator(func):                 # ✅ 고차 함수: 함수를 인자로 받음
    def wrapper(*args, **kwargs):       # ✅ 클로저: 외부 변수 func을 기억
        print("함수 호출 전")
        result = func(*args, **kwargs) # result = func(*args, **kwargs) → func는 greet, 그래서 print(f"안녕하세요, {name}님!") 실행됨. 결과를 리턴하는게 아니고 콘솔에 출력하는 내부 로직이라 여기서 "안녕하세요, 홍길동님!" 출력!
        print("함수 호출 후")
        return result
    return wrapper

@my_decorator # my_decorator(greet) → wrapper 반환
def greet(name):
    print(f"안녕하세요, {name}님!") 

# 사용
greet("홍길동") # greet("홍길동") → 실제로는 wrapper("홍길동") 실행

# 출력 결과 
# 함수 호출 전
# 안녕하세요, 홍길동님! 
# 함수 호출 후
```

- 예시 2: 

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("함수 호출 전")
        result = func(*args, **kwargs)   # 반환값을 받아옴
        print("함수 호출 후")
        return result
    return wrapper

@my_decorator
def add(a, b):
    return a + b

result = add(3, 4)
print(f"최종 결과: {result}")

# 출력 결과 
# 함수 호출 전 
# 함수 호출 후
# 최종 결과: 7
```

**파이썬 내장 데코레이터들:**
`@classmethod`와 `@staticmethod`, `@property`는 파이썬의 내장 데코레이터로, 데코레이터에 대한 이해가 깊어질수록 파생 개념으로 이해할 수 있습니다.

```python
class Calculator:
    def __init__(self, x, y):
        self._x = x
        self._y = y
        
    @staticmethod
    def add(x, y):
        """✅ 정적 메서드 - 인스턴스나 클래스 상태에 의존하지 않음.
        인스턴스나 클래스 상태와 무관한 유틸리티 함수 만들 때 사용."""
        return x + y
    
    @classmethod
    def create_from_string(cls, expression):
        """✅ 클래스 메서드 - 클래스 자체를 첫 번째 인자로 받음.
        클래스 상태를 조작하거나, 생성자를 대체하고 싶을 때 사용."""
        # "1+2" 같은 문자열을 파싱해서 인스턴스를 반환
        if '+' in expression:
            x, y = map(int, expression.split('+'))
            return cls(x, y)  # ✅ cls()를 이용해 Calculator 인스턴스를 생성
        return None

    @property
    def result(self):
        """✅ @property: 메서드를 속성처럼 사용할 수 있게 함
        self._x + self._y 값을 계산해서 속성처럼 접근"""
        return self._x + self._y

# ✅ 사용 예시
# 1. 정적 메서드는 클래스 이름으로 바로 호출 가능 (유틸리티 함수처럼)
print(Calculator.add(3, 5))  # 출력: 8

# 2. 클래스 메서드를 통해 문자열을 파싱하여 인스턴스를 생성
calc = Calculator.create_from_string("10+20")

# 3. @property 덕분에 메서드처럼 호출하지 않고도 속성처럼 접근
print(calc.result)  # 출력: 30 (== calc._x + calc._y)
```

## 2. 실무 활용 사례

### 2.1 로깅 데코레이터

```python
import logging
import time
from functools import wraps
from typing import Callable, Any

def logging_decorator(level: str = "INFO"):
    """로깅 데코레이터 - 실무에서 자주 사용"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)  # cf. @wraps를 쓰지 않으면 __name__, __doc__, __annotations__이 덮여버리게 됨. 원본 함수 메타데이터 유지하려면 사용해야함
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

# 호출시 동작 흐름: 
# logging_decorator(level="DEBUG") 라는 함수 호출이 먼저 실행
# 이 호출은 decorator(func) 함수 자체를 반환함. 즉, 여기서 process_user_data는 func로 들어가게 됨
# 이제 process_user_data 함수는 process_user_data = wrapper  # 감싸진 wrapper 함수로 대체됨
# wrapper(*args, **kwargs)가 호출되면, 내부에서 func(*args, **kwargs) → 즉 process_user_data(...) 원본 함수가 호출돼. 그 리턴값은 result = ...에 담긴 뒤 그대로 리턴

# 출력 예시: 
# INFO:__main__:함수 process_user_data 실행 시작 - 인자: (123, {'name': '홍길동', 'age': 30}), {}
# INFO:__main__:함수 process_user_data 실행 완료 - 소요시간: 0.100초
# {'user_id': 123, 'processed': True, 'data': {'name': '홍길동', 'age': 30}}
```

### 2.2 인증 데코레이터

```python
from functools import wraps
from typing import Callable, Any
import jwt
from datetime import datetime, timedelta
import traceback
SECRET_KEY = "secret"

def require_auth(required_roles: list = None):
    """인증 및 권한 체크 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            token = kwargs.get('token') or (args[0] if args else None)

            if not token:
                raise ValueError("인증 토큰이 필요합니다")

            try:
                # JWT 토큰 검증
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
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
def delete_user(user_id: int, token: str = None, **kwargs) -> dict:
    """사용자 삭제 함수 - admin 권한 필요"""
    return {
        "message": f"사용자 {user_id} 삭제 완료",
        "deleted_by": kwargs.get('user_id'),
        "roles": kwargs.get('user_roles')
    }

# 테스트용 토큰 생성
def create_test_token(user_id: int, roles: list):
    payload = {
        'user_id': user_id,
        'roles': roles,
        'exp': datetime.now() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    # PyJWT 2.x 이상에서는 str로 변환 필요
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

# 테스트 실행
if __name__ == "__main__":
    admin_token = create_test_token(1, ["admin", "user"])
    user_token = create_test_token(2, ["user"])

    try:
        # ✅ admin 권한 → 성공
        result = delete_user(user_id=123, token=admin_token)
        print("✅ admin_token 실행 결과:", result)

        # ❌ user 권한만 → 실패
        result = delete_user(user_id=123, token=user_token)
        print("❌ user_token 실행 결과:", result)
    except Exception as e:
        # print(traceback.format_exc())
        print(f"🚫 예외 발생: {e}")

# 출력 예시: 
# ✅ admin_token 실행 결과: {'message': '사용자 1 삭제 완료', 'deleted_by': None, 'roles': ['admin', 'user']}
# 🚫 예외 발생: 필요한 권한: ['admin'], 현재 권한: ['user']
```

## 3. 고급 기법

### 3.1 클래스 데코레이터
- 클래스 자체를 데코레이션하는 고급 기법

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

### 3.2 체이닝 데코레이터
- 여러 데코레이터를 조합해서 사용하는 방법
- 데코레이터 체이닝 시 순서가 함수의 동작에 영향을 줄 수 있다는 점 유의

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

### 3.3 매개변수화된 데코레이터 팩토리

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

---

<details>
<summary>참고 자료</summary>

- 

</details> 



