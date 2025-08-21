---
title: "파이썬에서 자주 쓰이는 디자인 패턴"
date: 2025-08-21
categories:
  - python
  - design-patterns
tags:
  - factory-pattern
  - strategy-pattern
  - decorator-pattern
  - singleton-pattern
  - observer-pattern
  - python-design
---

# 파이썬에서 자주 쓰이는 디자인 패턴

## 1. 팩토리 패턴 (Factory Pattern)

### ✓ 개념
- 팩토리 패턴은 객체 생성 로직을 캡슐화하여, 클라이언트 코드가 구체적인 클래스에 의존하지 않도록 해주는 생성 패턴.
- 세부적인 구현 방식에 따라 팩토리 패턴은 대표적으로 3가지 변형이 있다:  
    - Simple Factory (실질적 패턴 X, 비공식):
        - 함수나 클래스로 조건문에 따라 객체를 생성하는 방식 
    - Factory Method (공식 GoF 패턴): 
        - 객체 생성을 서브클래스에 우임하여, 새로운 객체 타입이 생겨도 기존 코드를 수정하지 않음 (OCP(개방-폐쇄 원칙) 만족)
            - *cf. OCP(Open-Closed Principle): Open for extension, Closed for modification. “기존 코드를 수정하지 않고 기능을 확장할 수 있어야 한다”는 원칙*
    - Abstract Factory (공식 GoF 패턴): 
        - 관련된 객체군(family of objects)을 일관되게 생성할 수 있는 인터페이스 제공 (버튼 + 텍스트박스 같은 세트 생성용)

    
### ✓ Python 예시 
#### (심플) 팩토리 패턴 예시

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

# 추상 클래스
class Animal(ABC):
    @abstractmethod
    def speak(self) -> str:
        pass

# 구체 클래스들
class Dog(Animal):
    def speak(self) -> str:
        return "Woof!"

class Cat(Animal):
    def speak(self) -> str:
        return "Meow!"

class Bird(Animal):
    def speak(self) -> str:
        return "Tweet!"

# 팩토리 함수
def animal_factory(animal_type: str) -> Animal:
    animals = {
        "dog": Dog,
        "cat": Cat,
        "bird": Bird
    }
    
    if animal_type not in animals:
        raise ValueError(f"Unknown animal type: {animal_type}")
    
    return animals[animal_type]()

# 사용 예시
def demonstrate_factory():
    """팩토리 패턴 시연"""
    try:
        # 팩토리를 통한 객체 생성 
        dog = animal_factory("dog")
        cat = animal_factory("cat")
        bird = animal_factory("bird")
        
        print(f"Dog says: {dog.speak()}")
        print(f"Cat says: {cat.speak()}")
        print(f"Bird says: {bird.speak()}")
        
        # 잘못된 타입 요청
        # unknown = animal_factory("unknown")  # ValueError 발생
        
    except ValueError as e:
        print(f"Error: {e}")

# 실행
if __name__ == "__main__":
    demonstrate_factory()

# 팩토리 함수가 하나의 진입점(animal_factory)를 제공하고, 클라이언트는 animal_type이라는 문자열만 넘기면 내부적으로 적절한 객체가 생성됨.
# => 객체 생성을 캡슐화했지만, 상속을 통해 팩토리 클래스를 확장하거나 오버라이드하지는 않음.
```

#### 팩토리 메서드 패턴 예시
- 객체 생성을 위한 팩토리 메서드를 추상화하여, 서브클래스가 생성 책임을 가짐 
- 위 예시의 animal_factory 같은 함수는 사라지고, 각 팩토리 클래스가 책임을 나눠 가짐 

```python 
from abc import ABC, abstractmethod

# 제품
class Animal(ABC):
    @abstractmethod
    def speak(self) -> str:
        pass

# 제품 구현
class Dog(Animal):
    def speak(self) -> str:
        return "Woof!"

class Cat(Animal):
    def speak(self) -> str:
        return "Meow!"

# 팩토리 추상 클래스
class AnimalFactory(ABC):
    @abstractmethod
    def create_animal(self) -> Animal:
        pass

# 각 팩토리 서브클래스
class DogFactory(AnimalFactory):
    def create_animal(self) -> Animal:
        return Dog()

class CatFactory(AnimalFactory):
    def create_animal(self) -> Animal:
        return Cat()

# 사용 예시
def demonstrate_factory_method():
    factory: AnimalFactory = DogFactory()
    dog = factory.create_animal()
    print(f"Dog says: {dog.speak()}")

    factory = CatFactory()
    cat = factory.create_animal()
    print(f"Cat says: {cat.speak()}")


# 각 객체 생성 책임이 클래스에 위임됨
# → OCP (개방-폐쇄 원칙) 충족: 기존 코드를 수정하지 않고 기능 확장 가능
```

#### 추상 팩토리 패턴 예시
- 관련 객체군(제품군)을 일관되게 생성하는 팩토리 인터페이스 제공 
- 서로 연관된 복수의 객체들을 통째로 생성하는 구조 

```python 
# "동물"을 만드는게 아니고 "동물" + "소리 기계" 세트를 만든다고 가정 

# 제품 계열 A
class Animal(ABC):
    @abstractmethod
    def speak(self) -> str:
        pass

class Dog(Animal):
    def speak(self) -> str:
        return "Woof!"

class Cat(Animal):
    def speak(self) -> str:
        return "Meow!"

# 제품 계열 B
class SoundMachine(ABC):
    @abstractmethod
    def make_noise(self) -> str:
        pass

class DogSoundMachine(SoundMachine):
    def make_noise(self) -> str:
        return "Playing barking sound..."

class CatSoundMachine(SoundMachine):
    def make_noise(self) -> str:
        return "Playing meowing sound..."

# 추상 팩토리
class AnimalSetFactory(ABC):
    @abstractmethod
    def create_animal(self) -> Animal:
        pass

    @abstractmethod
    def create_sound_machine(self) -> SoundMachine:
        pass

# 구체 팩토리
class DogSetFactory(AnimalSetFactory):
    def create_animal(self) -> Animal:
        return Dog()

    def create_sound_machine(self) -> SoundMachine:
        return DogSoundMachine()

class CatSetFactory(AnimalSetFactory):
    def create_animal(self) -> Animal:
        return Cat()

    def create_sound_machine(self) -> SoundMachine:
        return CatSoundMachine()

# 사용 예시
def demonstrate_abstract_factory():
    factory: AnimalSetFactory = DogSetFactory()
    animal = factory.create_animal()
    machine = factory.create_sound_machine()

    print(animal.speak())
    print(machine.make_noise())


# 동물과 사운드 기계를 함께 세트로 일관되게 생성
```

#### 정리: 3가지 팩토리 패턴 차이

|패턴|구조|특징|코드 난이도|
|---------------|-------------------|--------------------|--------|
|Simple Factory|하나의 함수로 객체 생성|간단하지만 확장에 약함|⭐|
|Factory Method|서브클래스가 팩토리 역할|OCP에 부합, 커스터마이징 용이|⭐⭐|
|Abstract Factory|관련된 객체군을 함께 생성|복잡하지만 통일성 보장|⭐⭐⭐|


### ✓ 실무 예시 (Practical Examples)

- **API 응답에 따라 다양한 객체 생성**: 외부 API 응답 형태에 따른 데이터 처리 객체 생성
- **DB 유형, 외부 API 연동 구조가 다른 경우**: 데이터베이스 종류나 외부 서비스에 따른 어댑터 객체 생성

```python
# 실무 예시: API 응답 처리 팩토리
class ApiResponseHandler(ABC):
    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

class UserResponseHandler(ApiResponseHandler):
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": data.get("user_id"),
            "name": data.get("display_name"),
            "email": data.get("email_address")
        }

class ProductResponseHandler(ApiResponseHandler):
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": data.get("product_id"),
            "title": data.get("product_name"),
            "price": data.get("cost")
        }

def response_handler_factory(response_type: str) -> ApiResponseHandler:
    handlers = {
        "user": UserResponseHandler,
        "product": ProductResponseHandler
    }
    return handlers[response_type]()

# 사용
user_handler = response_handler_factory("user")
processed_user = user_handler.process({"user_id": 1, "display_name": "John", "email_address": "john@example.com"})
```

---

## 2. 전략 패턴 (Strategy Pattern)

### ✓ 개념 
- 행위를 캡슐화하고, 실행 시점에 알고리즘(전략)을 바꿀 수 있게 해주는 패턴. (즉, 상황에 따라 알고리즘(전략)을 쉽게 바꿀 수 있게 만드는 패턴)

### ✓ Python 예시

```python
# strategy.py
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: int) -> str:
        pass

class KakaoPay(PaymentStrategy):
    def pay(self, amount: int) -> str:
        return f"KakaoPay로 {amount}원 결제 완료"

class CreditCard(PaymentStrategy):
    def pay(self, amount: int) -> str:
        return f"신용카드로 {amount}원 결제 완료"

# factory.py
def get_payment_strategy(method: str) -> PaymentStrategy:
    strategies = {
        "kakao": KakaoPay(),
        "card": CreditCard()
    }
    if method not in strategies:
        raise ValueError("지원하지 않는 결제 수단입니다.")
    return strategies[method]

# main.py (FastAPI)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from strategy import PaymentStrategy
from factory import get_payment_strategy

app = FastAPI()

class PaymentRequest(BaseModel):
    method: str
    amount: int

@app.post("/pay")
def pay(request: PaymentRequest):
    try:
        strategy: PaymentStrategy = get_payment_strategy(request.method)
        result = strategy.pay(request.amount)
        return {"result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

- 클라이언트에서 "kakao"나 "card" 같은 결제 방식을 JSON으로 보내면, 이를 기반으로 실행 시점에 적절한 결제 전략 클래스를 선택하여 실행하는 구조.
- 전략 선택은 런타임에 일어나며, get_payment_strategy() 같은 팩토리 함수를 통해 전략 객체를 리턴받고, 공통 인터페이스(pay())로 호출한다. 
- if-else 분기를 피하고 확장성도 높일 수 있는 효과.

#### cf. 전략 패턴과 if-else 구조의 차이
- **전략 패턴**: 런타임에 알고리즘 교체 가능, 확장성과 유지보수성 우수
- **if-else**: 컴파일 타임에 결정, 간단하지만 확장성 제한

#### cf. 전략 객체를 DI(의존성 주입) 방식으로 주입하려면?

```python
# FastAPI에서의 의존성 주입 예시
from fastapi import Depends
from typing import Dict, Type

# 객체가 의존하는 객체(=의존성)을 직접 생성하지 않고, **외부에서 주입받는 방식**. 외부에서 넘겨주면 어떤 객체가 들어갈지가 유연해짐.
class PaymentService:
    def __init__(self, payment_strategies: Dict[str, PaymentStrategy]):
        self.strategies = payment_strategies
    
    def get_payment_processor(self, payment_type: str) -> PaymentProcessor:
        if payment_type not in self.strategies:
            raise ValueError(f"Unknown payment type: {payment_type}")
        return PaymentProcessor(self.strategies[payment_type])

# 의존성 설정 (외부에서)
def get_payment_service() -> PaymentService:
    strategies = {
        "credit_card": CreditCardPayment(),
        "bank_transfer": BankTransferPayment(),
        "crypto": CryptoPayment()
    }
    return PaymentService(strategies)
```

---

## 3. 데코레이터 패턴 (Decorator Pattern)

### ✓ 개념 
- 기존 객체에 기능을 추가하면서, 객체 구조는 변경하지 않고, 동적으로 행동을 확장할 수 있는 패턴 
- Python의 `@decorator` 문법이 이 패턴을 지원
- 기존 클래스(또는 함수)의 코드를 변경하지 않고, 기능을 덧붙이고 싶은데, 상속보다 유연하게 기능 조합이 필요할 때 사용

### ✓ Python 예시 
- 
```python
from functools import wraps
import time
import random

# 🎯 Decorator - Logger
def logger(func):
    """로깅 기능을 추가하는 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[Logger] Function {func.__name__} called with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"[Logger] Function {func.__name__} returned {result}")
        return result
    return wrapper

# 🎯 Decorator - Retry
def retry(max_attempts: int = 3, delay: float = 1.0):
    """에러 발생 시 재시도 기능을 추가하는 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    print(f"[Retry] Attempt {attempt}")
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"[Retry] Failed attempt {attempt}: {e}")
                    if attempt == max_attempts:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

# 🎯 핵심 기능 함수들 - 데코레이터 문법으로 적용
@logger
def say_hello(name: str) -> str:
    """간단한 인사 함수 (핵심 기능)"""
    return f"Hello, {name}!"

@logger
@retry(max_attempts=3, delay=0.5)
def unstable_greet(name: str) -> str: # unstable_greet = logger(retry(...)(unstable_greet))랑 같은 의미 
    """가끔 실패하는 함수 (불안정한 인사)"""
    if random.random() < 0.6:
        raise ValueError("임시 오류 발생!")
    return f"Nice to meet you, {name}"

# ✅ 실행 예시
if __name__ == "__main__":
    print(say_hello("Alice"))
    print()
    print(unstable_greet("Bob"))


# 출력 예시 
# [Logger] Function say_hello called with args=('Alice',), kwargs={}
# [Logger] Function say_hello returned Hello, Alice!
# Hello, Alice!

# [Logger] Function wrapper called with args=('Bob',), kwargs={}
# [Retry] Attempt 1
# [Retry] Failed attempt 1: 임시 오류 발생!
# [Retry] Attempt 2
# [Retry] Failed attempt 2: 임시 오류 발생!
# [Retry] Attempt 3
# [Logger] Function unstable_greet returned Nice to meet you, Bob
# Nice to meet you, Bob
```

#### cf. 데코레이터가 내부적으로 어떻게 동작하나요?
- 파이썬의 데코레이터는 함수나 클래스의 동작을 변경하거나 확장할 수 있는 문법적 설탕(syntax sugar)인 `@decorator`인데, 
`@decorator`는 사실살 `func = decorator(func)` 형태의 함수 재정의 방식으로 작동한다
    - 즉, `@decorator`는 `func = decorator(func)`와 동일
- 함수 정의 시, 파이썬은 데코레이터 함수에 원본 함수를 인자로 넘겨서 실행하고, 그 리턴값을 해당 이름에 다시 바인딩한다. 
    - 예: 클로저를 활용하여 원본 함수와 추가 기능을 결합

    ```python
    @my_decorator
    def hello():
        print("hi")

    # 위는 결국 hello = my_decorator(hello)와 동일. 실제 동작 흐름의 예시는 아래와 같다 
    from functools import wraps

    def my_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print("Before call")
            result = func(*args, **kwargs)
            print("After call")
            return result
        return wrapper

    @my_decorator
    def say_hello(name):
        print(f"Hello, {name}")

    say_hello("Alice")

    # 실행 결과 
    #Before call
    #Hello, Alice
    #After call
    ```


#### cf. 왜 `functools.wraps`가 필요한가?
- functools.wraps는 데코레이터 안에서 원래 함수의 `__name__`, `__doc__` 등 wrapper함수가 funcdml 정체성/메타 정보를 유지할 수 있게 해준다. (디버깅, 문서화 시 매우 중요) 
    - wraps(func)는 내부적으로 `wrapper.__name__ = func.__name__`같은 메타데이터 복사 작업을 한다. 


---

## 4. 싱글톤 패턴 (Singleton Pattern)

### ✓ 개념
- 어떤 클래스의 인스턴스가 딱 하나만 생성되도록 보장하고, 어디서든 그 인스턴스에 접근할 수 있는 전역 접근 지점을 제공하는 패턴이다 
- 공통된 자원 e.g. DB 연결, 환경 설정 관리 객체, 로거 등 하나만 있고 전역에서 공유할 수 있는 객체에 사용된다 

### ✓ Python 예시 

```python
import threading
import logging
import redis
from typing import Optional
from contextlib import contextmanager

# 방법 1: 메타클래스를 사용한 싱글톤 (실무에서 가장 많이 사용)
class SingletonMeta(type):
    _instance: Optional[object] = None
    _lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:  # 스레드 안전성 보장
                if not cls._instance:
                    cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

class DatabaseManager(metaclass=SingletonMeta):
    """데이터베이스 연결 관리자 - 싱글톤으로 구현"""
    
    def __init__(self):
        self._connections = {}
        self._config = {
            'postgres': {
                'host': 'localhost',
                'port': 5432,
                'database': 'production_db',
                'user': 'app_user',
                'password': 'secure_password'
            },
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'db': 0
            }
        }
        print("🔧 DatabaseManager 초기화 완료")
    
    def get_postgres_connection(self):
        """PostgreSQL 연결 반환"""
        if 'postgres' not in self._connections:
            # 실제로는 psycopg2나 asyncpg 사용
            self._connections['postgres'] = f"Connected to {self._config['postgres']['database']}"
            print(f"📊 PostgreSQL 연결 생성: {self._config['postgres']['database']}")
        return self._connections['postgres']
    
    def get_redis_connection(self):
        """Redis 연결 반환"""
        if 'redis' not in self._connections:
            # 실제로는 redis-py 사용
            self._connections['redis'] = f"Connected to Redis {self._config['redis']['host']}:{self._config['redis']['port']}"
            print(f"🔴 Redis 연결 생성: {self._config['redis']['host']}:{self._config['redis']['port']}")
        return self._connections['redis']
    
    def close_all_connections(self):
        """모든 연결 종료"""
        self._connections.clear()
        print("🔒 모든 데이터베이스 연결 종료")

# 방법 2: 데코레이터를 사용한 싱글톤 (간단한 설정 객체에 적합)
def singleton(cls):
    """클래스를 싱글톤으로 만드는 데코레이터"""
    instances = {}
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class AppConfig:
    """애플리케이션 설정 - 싱글톤으로 구현"""
    
    def __init__(self):
        # 환경 변수나 설정 파일에서 로드
        self.APP_NAME = "E-Commerce API"
        self.APP_VERSION = "2.1.0"
        self.DEBUG = False
        self.API_RATE_LIMIT = 1000
        self.JWT_SECRET = "super_secret_key_2024"
        self.SESSION_TIMEOUT = 3600
        
        # 외부 서비스 설정
        self.PAYMENT_GATEWAY_URL = "https://api.payment.com/v2"
        self.EMAIL_SERVICE_URL = "https://api.email.com/v1"
        self.SMS_SERVICE_URL = "https://api.sms.com/v1"
        
        print(f"⚙️ {self.APP_NAME} v{self.APP_VERSION} 설정 로드 완료")
    
    def get_database_url(self) -> str:
        """데이터베이스 URL 반환"""
        return f"postgresql://user:pass@localhost:5432/{self.APP_NAME.lower().replace(' ', '_')}"
    
    def is_production(self) -> bool:
        """프로덕션 환경 여부 확인"""
        return not self.DEBUG

# 방법 3: 모듈 레벨 싱글톤 (로거, 캐시 등에 적합)
class LoggerManager:
    """로깅 관리자 - 모듈 레벨 싱글톤"""
    
    def __init__(self):
        self.logger = logging.getLogger('app')
        self.logger.setLevel(logging.INFO)
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 파일 핸들러
        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(logging.DEBUG)
        
        # 포맷터
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        print("📝 LoggerManager 초기화 완료")

# 모듈 레벨에서 인스턴스 생성
logger_manager = LoggerManager()

# 실무 사용 예시
def demonstrate_singleton():
    """실무에서의 싱글톤 패턴 활용 시연"""
    
    print("\n" + "="*50)
    print("🏢 실무에서의 싱글톤 패턴 활용")
    print("="*50)
    
    # 1. 데이터베이스 매니저 사용
    print("\n1️⃣ 데이터베이스 연결 관리:")
    db_manager1 = DatabaseManager()
    db_manager2 = DatabaseManager()
    
    print(f"   db_manager1 is db_manager2: {db_manager1 is db_manager2}")
    
    # 데이터베이스 연결 사용
    postgres_conn = db_manager1.get_postgres_connection()
    redis_conn = db_manager1.get_redis_connection()
    
    print(f"   PostgreSQL: {postgres_conn}")
    print(f"   Redis: {redis_conn}")
    
    # 2. 애플리케이션 설정 사용
    print("\n2️⃣ 애플리케이션 설정 관리:")
    config1 = AppConfig()
    config2 = AppConfig()
    
    print(f"   config1 is config2: {config1 is config2}")
    print(f"   앱 이름: {config1.APP_NAME}")
    print(f"   버전: {config1.APP_VERSION}")
    print(f"   데이터베이스 URL: {config1.get_database_url()}")
    print(f"   프로덕션 환경: {config1.is_production()}")
    
    # 3. 로거 매니저 사용
    print("\n3️⃣ 로깅 시스템:")
    logger1 = logger_manager.logger
    logger2 = logger_manager.logger
    
    print(f"   logger1 is logger2: {logger1 is logger2}")
    
    # 실제 로깅
    logger1.info("애플리케이션 시작")
    logger1.warning("데이터베이스 연결 지연 감지")
    logger1.error("외부 API 호출 실패")
    
    # 4. 실제 비즈니스 로직에서의 활용
    print("\n4️⃣ 비즈니스 로직에서의 활용:")
    
    class UserService:
        def __init__(self):
            self.db_manager = DatabaseManager()
            self.config = AppConfig()
            self.logger = logger_manager.logger
        
        def create_user(self, user_data: dict):
            """사용자 생성"""
            self.logger.info(f"사용자 생성 시작: {user_data.get('email')}")
            
            # 설정 확인
            if not self.config.is_production():
                self.logger.debug("개발 환경에서 사용자 생성")
            
            # 데이터베이스 연결 사용
            db_conn = self.db_manager.get_postgres_connection()
            self.logger.info(f"데이터베이스 연결 사용: {db_conn}")
            
            # 실제 사용자 생성 로직...
            self.logger.info("사용자 생성 완료")
            return {"user_id": 123, "status": "created"}
    
    # 사용자 서비스 사용
    user_service = UserService()
    result = user_service.create_user({"email": "user@example.com", "name": "홍길동"})
    print(f"   사용자 생성 결과: {result}")

# 실행
if __name__ == "__main__":
    demonstrate_singleton()
```

#### cf. 멀티스레드 환경에서 싱글톤 패턴은 안전한가? (스레드 안전성 문제)
- 동시에 여러 스레드가 인스턴스 생성 시도 시 중복 생성 가능하다는 문제점
- `threading.Lock()`을 사용한 동기화 또는 `@threading.local` 데코레이터 활용하여 해결하면 된다 

---

## 5. 옵저버 패턴 (Observer Pattern)

### ✓ 개념 
- Subject(관찰 대상)의 상태 변화에 따라 Observer(관찰자)가 자동으로 알림을 받는 디자인 패턴
- 주체(Subject): 상태를 가지고 있으며, 옵저버들을 등록하거나 제거할 수 있고, 상태 변화가 있으면 옵저버들에게 알람을 보낸다 
- 옵저버(Observer): 주체에 등록되어 있다가, 주체에 상태 변화가 생기면 자동으로 알림을 받는 객체이다 
- 즉, `구독-발행(Pub-Sub)구조`와 유사하다 

### ✓ Python 예시 

```python
class Subject:
    def __init__(self):
        self._observers = []

    def register(self, observer):
        self._observers.append(observer)

    def unregister(self, observer):
        self._observers.remove(observer)

    def notify(self, message):
        for observer in self._observers:
            observer.update(message)

class Observer:
    def __init__(self, name):
        self.name = name

    def update(self, message):
        print(f"[{self.name}] 알림 받음: {message}")

# 사용 예시
subject = Subject()

observer_a = Observer("사용자 A")
observer_b = Observer("사용자 B")

subject.register(observer_a)
subject.register(observer_b)

subject.notify("새로운 공지가 있습니다!")

# 출력:
# [사용자 A] 알림 받음: 새로운 공지가 있습니다!
# [사용자 B] 알림 받음: 새로운 공지가 있습니다!
```

### ✓ 면접 질문 (Interview Questions)

#### cf. 옵저버 패턴과 pub/sub의 차이점은?
- **옵저버**: Subject와 Observer가 직접 연결, 동기적 통신
- **Pub/Sub**: 중간에 메시지 브로커가 존재, 비동기적 통신, 느슨한 결합

#### cf. 옵저버 패턴의 단점과 해결 방법은?
- **단점**: 메모리 누수(Observer가 제거되지 않음), 순환 참조 가능성
- **해결**: Weak Reference 사용, 이벤트 버스 패턴으로 대체

---

## 6. 패턴별 비교표

|패턴명|핵심 키워드|실무 예시|자주 묻는 질문|
|---------|---------|---------|---------------------------|
|**팩토리**|객체 생성 캡슐화|API 응답별 처리|객체 분기 처리의 유연성|
|**전략**|알고리즘 교체|추천/정렬 기준|DI 구조와 전략 분리|
|**데코레이터**|기능 추가|인증/로깅|데코레이터 내부 동작|
|**싱글톤**|인스턴스 1개 보장|설정, DB 커넥션|모듈과의 차이|
|**옵저버**|상태 변화 → 자동 알림|실시간 알림|pub/sub와 비교|

---


<details>
<summary>참고 자료</summary>

- 
</details> 




