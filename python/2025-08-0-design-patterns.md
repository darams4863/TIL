---
title: "파이썬에서 자주 쓰이는 디자인 패턴 정리 (실무 & 면접용)"
date: 2025-08-19
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

# 파이썬에서 자주 쓰이는 디자인 패턴 정리 (실무 & 면접용)

## 📋 목차
1. **팩토리 패턴 (Factory Pattern)** - 객체 생성 캡슐화
2. **전략 패턴 (Strategy Pattern)** - 알고리즘 교체
3. **데코레이터 패턴 (Decorator Pattern)** - 기능 추가
4. **싱글톤 패턴 (Singleton Pattern)** - 인스턴스 1개 보장
5. **옵저버 패턴 (Observer Pattern)** - 상태 변화 → 자동 알림
6. **패턴별 비교표** - 핵심 키워드와 실무 예시
7. **면접 대비 요약 정리** - 실무 경험과 답변 전략

---

## 1. 팩토리 패턴 (Factory Pattern)

### ✓ 개념 (Concept)

**객체 생성 로직을 캡슐화하여, 클라이언트 코드가 구체 클래스에 직접 의존하지 않도록 함**

### ✓ Python 예시 (Python Example)

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
```

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

### ✓ 면접 질문 (Interview Questions)

**Q: "팩토리 패턴을 쓰는 이유는?"**
- 클라이언트 코드와 구체 클래스 간의 결합도 감소
- 객체 생성 로직의 중앙화 및 유지보수성 향상
- 새로운 타입 추가 시 기존 코드 수정 없이 확장 가능

**Q: "객체 생성 분기를 어떻게 유연하게 관리하나요?"**
- 딕셔너리나 매핑을 통한 타입별 클래스 관리
- 설정 파일이나 환경 변수를 통한 동적 팩토리 구성
- 플러그인 아키텍처를 통한 확장 가능한 팩토리 설계

---

## 2. 전략 패턴 (Strategy Pattern)

### ✓ 개념 (Concept)

**런타임에 알고리즘을 바꿀 수 있도록, 알고리즘을 캡슐화하고 교체 가능하게 설계**

### ✓ Python 예시 (Python Example)

```python
from abc import ABC, abstractmethod
from typing import List, Any

# 전략 인터페이스
class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: List[Any]) -> List[Any]:
        pass

# 구체적인 전략들
class QuickSort(SortStrategy):
    def sort(self, data: List[Any]) -> List[Any]:
        return sorted(data)

class ReverseSort(SortStrategy):
    def sort(self, data: List[Any]) -> List[Any]:
        return sorted(data, reverse=True)

class CustomSort(SortStrategy):
    def sort(self, data: List[Any]) -> List[Any]:
        # 커스텀 정렬 로직 (예: 짝수 우선)
        return sorted(data, key=lambda x: (x % 2, x))

# 컨텍스트 클래스
class Context:
    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: SortStrategy):
        """전략 동적 변경"""
        self._strategy = strategy
    
    def sort_data(self, data: List[Any]) -> List[Any]:
        """현재 전략으로 데이터 정렬"""
        return self._strategy.sort(data)

# 사용 예시
def demonstrate_strategy():
    """전략 패턴 시연"""
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    
    # QuickSort 전략 사용
    context = Context(QuickSort())
    result = context.sort_data(data)
    print(f"QuickSort: {result}")
    
    # ReverseSort 전략으로 변경
    context.set_strategy(ReverseSort())
    result = context.sort_data(data)
    print(f"ReverseSort: {result}")
    
    # CustomSort 전략으로 변경
    context.set_strategy(CustomSort())
    result = context.sort_data(data)
    print(f"CustomSort: {result}")

# 실행
if __name__ == "__main__":
    demonstrate_strategy()
```

### ✓ 실무 예시 (Practical Examples)

- **다양한 정렬 기준 제공**: 사용자 선택에 따른 정렬 알고리즘 동적 변경
- **추천 알고리즘, 포인트 적립 방식 등 동적 교체**: 비즈니스 로직의 유연한 변경

```python
# 실무 예시: 결제 전략 패턴
class PaymentStrategy(ABC):
    @abstractmethod
    def calculate_fee(self, amount: float) -> float:
        pass

class CreditCardPayment(PaymentStrategy):
    def calculate_fee(self, amount: float) -> float:
        return amount * 0.03  # 3% 수수료

class BankTransferPayment(PaymentStrategy):
    def calculate_fee(self, amount: float) -> float:
        return 500  # 고정 수수료 500원

class CryptoPayment(PaymentStrategy):
    def calculate_fee(self, amount: float) -> float:
        return amount * 0.01  # 1% 수수료

class PaymentProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: PaymentStrategy):
        self._strategy = strategy
    
    def process_payment(self, amount: float) -> Dict[str, float]:
        fee = self._strategy.calculate_fee(amount)
        total = amount + fee
        
        return {
            "amount": amount,
            "fee": fee,
            "total": total
        }

# 사용
processor = PaymentProcessor(CreditCardPayment())
result = processor.process_payment(10000)
print(f"신용카드 결제: {result}")

processor.set_strategy(BankTransferPayment())
result = processor.process_payment(10000)
print(f"계좌이체: {result}")
```

### ✓ 면접 질문 (Interview Questions)

**Q: "전략 패턴과 if-else 구조의 차이는?"**
- **전략 패턴**: 런타임에 알고리즘 교체 가능, 확장성과 유지보수성 우수
- **if-else**: 컴파일 타임에 결정, 간단하지만 확장성 제한

**Q: "전략 객체를 DI(의존성 주입) 방식으로 주입하려면?"**
```python
# FastAPI에서의 의존성 주입 예시
from fastapi import Depends
from typing import Dict, Type

class PaymentService:
    def __init__(self, payment_strategies: Dict[str, PaymentStrategy]):
        self.strategies = payment_strategies
    
    def get_payment_processor(self, payment_type: str) -> PaymentProcessor:
        if payment_type not in self.strategies:
            raise ValueError(f"Unknown payment type: {payment_type}")
        return PaymentProcessor(self.strategies[payment_type])

# 의존성 설정
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

### ✓ 개념 (Concept)

**객체에 동적으로 책임을 추가하는 패턴. Python의 `@decorator` 문법이 이 패턴을 자연스럽게 지원**

### ✓ Python 예시 (Python Example)

```python
from functools import wraps
import time
import logging

# 기본 데코레이터
def logger(func):
    """함수 호출 로깅 데코레이터"""
    @wraps(func)  # 원본 함수 메타데이터 유지
    def wrapper(*args, **kwargs):
        print(f"Function {func.__name__} called")
        result = func(*args, **kwargs)
        print(f"Function {func.__name__} finished")
        return result
    return wrapper

# 인자를 받는 데코레이터
def retry(max_attempts: int = 3, delay: float = 1.0):
    """재시도 로직 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

# 성능 측정 데코레이터
def performance_monitor(func):
    """함수 실행 시간 측정 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"{func.__name__} 실행 시간: {execution_time:.3f}초")
        
        return result
    return wrapper

# 사용 예시
@logger
@performance_monitor
def say_hello(name: str) -> str:
    """간단한 인사 함수"""
    time.sleep(0.1)  # 시뮬레이션
    return f"Hello, {name}!"

@retry(max_attempts=3, delay=0.5)
def unreliable_function():
    """불안정한 함수 (가끔 실패)"""
    import random
    if random.random() < 0.7:  # 70% 확률로 실패
        raise ValueError("임시 오류")
    return "성공!"

# 실행
if __name__ == "__main__":
    print(say_hello("World"))
    print(unreliable_function())
```

### ✓ 실무 예시 (Practical Examples)

- **FastAPI 라우터에 인증, 로깅, 캐싱 기능 추가**: API 엔드포인트에 공통 기능 적용
- **재시도 로직과 성능 측정 기능 래핑**: 비즈니스 로직과 부가 기능 분리

```python
# 실무 예시: FastAPI에서의 데코레이터 활용
from fastapi import FastAPI, HTTPException, Depends
from functools import wraps
import jwt
import time

app = FastAPI()

# 인증 데코레이터
def require_auth(required_roles: list = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 실제로는 request에서 토큰 추출
            token = kwargs.get('token')
            if not token:
                raise HTTPException(status_code=401, detail="인증 필요")
            
            try:
                payload = jwt.decode(token, "secret", algorithms=["HS256"])
                user_roles = payload.get('roles', [])
                
                if required_roles and not any(role in user_roles for role in required_roles):
                    raise HTTPException(status_code=403, detail="권한 부족")
                
                return await func(*args, **kwargs)
            except jwt.InvalidTokenError:
                raise HTTPException(status_code=401, detail="유효하지 않은 토큰")
        
        return wrapper
    return decorator

# 캐싱 데코레이터
def cache_result(ttl_seconds: int = 300):
    def decorator(func):
        cache = {}
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            current_time = time.time()
            
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < ttl_seconds:
                    return result
            
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            return result
        
        return wrapper
    return decorator

# 사용 예시
@app.get("/users/{user_id}")
@require_auth(required_roles=["admin", "user"])
@cache_result(ttl_seconds=60)
async def get_user(user_id: int, token: str):
    """사용자 정보 조회 (인증 + 캐싱 적용)"""
    # 실제 사용자 조회 로직
    return {"user_id": user_id, "name": "John Doe", "role": "user"}
```

### ✓ 면접 질문 (Interview Questions)

**Q: "데코레이터가 내부적으로 어떻게 동작하나요?"**
- 함수를 인자로 받아서 래퍼 함수로 감싸는 구조
- `@decorator`는 `func = decorator(func)`와 동일
- 클로저를 활용하여 원본 함수와 추가 기능을 결합

**Q: "왜 `functools.wraps`가 필요한가요?"**
- 원본 함수의 메타데이터(`__name__`, `__doc__` 등) 유지
- 디버깅과 인트로스펙션에서 원본 함수 정보 확인 가능
- 데코레이터 체이닝 시 메타데이터 손실 방지

---

## 4. 싱글톤 패턴 (Singleton Pattern)

### ✓ 개념 (Concept)

**클래스의 인스턴스를 오직 하나만 생성하도록 보장. Python에서는 모듈 자체가 싱글톤처럼 사용되기도 함**

### ✓ Python 예시 (Python Example)

```python
import threading
from typing import Optional

# 방법 1: 메타클래스를 사용한 싱글톤
class SingletonMeta(type):
    _instance: Optional[object] = None
    _lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:  # 스레드 안전성 보장
                if not cls._instance:
                    cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

class Config(metaclass=SingletonMeta):
    def __init__(self):
        self.database_url = "postgresql://localhost:5432/mydb"
        self.api_key = "secret_key"
        self.debug_mode = True
    
    def get_database_url(self) -> str:
        return self.database_url
    
    def get_api_key(self) -> str:
        return self.api_key

# 방법 2: 데코레이터를 사용한 싱글톤
def singleton(cls):
    """클래스를 싱글톤으로 만드는 데코레이터"""
    instances = {}
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class DatabaseConnection:
    def __init__(self):
        self.connection_string = "mysql://localhost:3306/mydb"
        print("데이터베이스 연결 생성")
    
    def connect(self):
        return f"Connected to {self.connection_string}"

# 방법 3: 모듈 레벨 싱글톤
class AppSettings:
    def __init__(self):
        self.app_name = "MyApp"
        self.version = "1.0.0"
        self.environment = "production"

# 모듈 레벨에서 인스턴스 생성
app_settings = AppSettings()

# 사용 예시
def demonstrate_singleton():
    """싱글톤 패턴 시연"""
    print("=== 메타클래스 싱글톤 ===")
    config1 = Config()
    config2 = Config()
    print(f"config1 is config2: {config1 is config2}")  # True
    
    print("\n=== 데코레이터 싱글톤 ===")
    db1 = DatabaseConnection()
    db2 = DatabaseConnection()
    print(f"db1 is db2: {db1 is db2}")  # True
    
    print("\n=== 모듈 레벨 싱글톤 ===")
    from importlib import import_module
    module1 = import_module(__name__)
    module2 = import_module(__name__)
    print(f"module1.app_settings is module2.app_settings: {module1.app_settings is module2.app_settings}")  # True

# 실행
if __name__ == "__main__":
    demonstrate_singleton()
```

### ✓ 실무 예시 (Practical Examples)

- **설정 객체, 데이터베이스 커넥션 풀, 설정 캐시 등**: 단일 인스턴스가 필요한 경우에 활용

```python
# 실무 예시: 데이터베이스 커넥션 풀 싱글톤
import psycopg2
from psycopg2 import pool
from typing import Optional

class DatabasePool(metaclass=SingletonMeta):
    def __init__(self):
        self._pool: Optional[pool.SimpleConnectionPool] = None
        self._config = {
            'host': 'localhost',
            'database': 'mydb',
            'user': 'postgres',
            'password': 'password',
            'minconn': 1,
            'maxconn': 10
        }
    
    def initialize_pool(self):
        """커넥션 풀 초기화"""
        if not self._pool:
            self._pool = pool.SimpleConnectionPool(
                self._config['minconn'],
                self._config['maxconn'],
                **{k: v for k, v in self._config.items() if k not in ['minconn', 'maxconn']}
            )
            print("데이터베이스 커넥션 풀 초기화 완료")
    
    def get_connection(self):
        """커넥션 가져오기"""
        if not self._pool:
            self.initialize_pool()
        return self._pool.getconn()
    
    def return_connection(self, conn):
        """커넥션 반환"""
        if self._pool:
            self._pool.putconn(conn)
    
    def close_pool(self):
        """풀 종료"""
        if self._pool:
            self._pool.closeall()
            self._pool = None

# 사용
db_pool = DatabasePool()
conn = db_pool.get_connection()
# ... 데이터베이스 작업 ...
db_pool.return_connection(conn)
```

### ✓ 면접 질문 (Interview Questions)

**Q: "모듈을 싱글톤처럼 사용하는 방식과 싱글톤 패턴 구현의 차이점은 무엇인가요?"**
- **모듈**: Python의 모듈 시스템이 자동으로 싱글톤 보장, 간단하고 안전
- **싱글톤 패턴**: 명시적인 제어, 상속과 다형성 지원, 더 복잡한 초기화 로직 가능

**Q: "멀티스레드 환경에서 싱글톤 패턴은 안전한가요?" (스레드 안전성 문제)**
- **문제**: 동시에 여러 스레드가 인스턴스 생성 시도 시 중복 생성 가능
- **해결**: `threading.Lock()`을 사용한 동기화 또는 `@threading.local` 데코레이터 활용

---

## 5. 옵저버 패턴 (Observer Pattern)

### ✓ 개념 (Concept)

**Subject(관찰 대상)의 상태 변화에 따라 Observer(관찰자)가 자동으로 알림을 받는 디자인 패턴**

### ✓ Python 예시 (Python Example)

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import time

# Observer 인터페이스
class Observer(ABC):
    @abstractmethod
    def update(self, subject, data: Any):
        pass

# Subject 인터페이스
class Subject(ABC):
    @abstractmethod
    def attach(self, observer: Observer):
        pass
    
    @abstractmethod
    def detach(self, observer: Observer):
        pass
    
    @abstractmethod
    def notify(self, data: Any):
        pass

# 구체적인 Subject
class NewsAgency(Subject):
    def __init__(self):
        self._observers: List[Observer] = []
        self._news: List[str] = []
    
    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"옵저버 {observer.__class__.__name__} 등록됨")
    
    def detach(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"옵저버 {observer.__class__.__name__} 제거됨")
    
    def notify(self, data: Any):
        for observer in self._observers:
            observer.update(self, data)
    
    def publish_news(self, news: str):
        """뉴스 발행"""
        self._news.append(news)
        print(f"뉴스 발행: {news}")
        self.notify(news)
    
    def get_news(self) -> List[str]:
        return self._news

# 구체적인 Observer들
class NewsChannel(Observer):
    def __init__(self, name: str):
        self.name = name
    
    def update(self, subject, data: Any):
        print(f"[{self.name}] 뉴스 수신: {data}")

class NewsWebsite(Observer):
    def __init__(self, url: str):
        self.url = url
    
    def update(self, subject, data: Any):
        print(f"[{self.url}] 웹사이트 업데이트: {data}")

class NewsApp(Observer):
    def __init__(self, app_name: str):
        self.app_name = app_name
    
    def update(self, subject, data: Any):
        print(f"[{self.app_name}] 푸시 알림: {data}")

# 사용 예시
def demonstrate_observer():
    """옵저버 패턴 시연"""
    # 뉴스 에이전시 생성
    news_agency = NewsAgency()
    
    # 옵저버들 등록
    tv_channel = NewsChannel("KBS")
    website = NewsWebsite("news.example.com")
    mobile_app = NewsApp("뉴스앱")
    
    news_agency.attach(tv_channel)
    news_agency.attach(website)
    news_agency.attach(mobile_app)
    
    # 뉴스 발행
    news_agency.publish_news("대통령, 경제 정책 발표")
    news_agency.publish_news("주식 시장 급등")
    
    # 옵저버 제거
    news_agency.detach(tv_channel)
    news_agency.publish_news("스포츠 뉴스")

# 실행
if __name__ == "__main__":
    demonstrate_observer()
```

### ✓ 실무 예시 (Practical Examples)

- **실시간 알림**: 사용자 활동에 따른 실시간 알림 시스템
- **이벤트 기반 아키텍처**: 마이크로서비스 간 이벤트 통신

```python
# 실무 예시: 사용자 활동 모니터링 시스템
class UserActivityTracker(Subject):
    def __init__(self):
        self._observers: List[Observer] = []
        self._user_activities: List[Dict[str, Any]] = []
    
    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, data: Any):
        for observer in self._observers:
            observer.update(self, data)
    
    def track_activity(self, user_id: int, activity: str, timestamp: float):
        """사용자 활동 추적"""
        activity_data = {
            "user_id": user_id,
            "activity": activity,
            "timestamp": timestamp
        }
        self._user_activities.append(activity_data)
        self.notify(activity_data)

class NotificationService(Observer):
    def __init__(self):
        self.notification_count = 0
    
    def update(self, subject, data: Any):
        user_id = data["user_id"]
        activity = data["activity"]
        
        # 특정 활동에 대한 알림 생성
        if activity in ["login", "purchase", "logout"]:
            self.send_notification(user_id, f"활동 감지: {activity}")
    
    def send_notification(self, user_id: int, message: str):
        self.notification_count += 1
        print(f"알림 #{self.notification_count} - 사용자 {user_id}: {message}")

class AnalyticsService(Observer):
    def __init__(self):
        self.activity_stats = {}
    
    def update(self, subject, data: Any):
        activity = data["activity"]
        if activity not in self.activity_stats:
            self.activity_stats[activity] = 0
        self.activity_stats[activity] += 1
        
        print(f"활동 통계 업데이트: {self.activity_stats}")

# 사용
tracker = UserActivityTracker()
notification_service = NotificationService()
analytics_service = AnalyticsService()

tracker.attach(notification_service)
tracker.attach(analytics_service)

# 사용자 활동 추적
tracker.track_activity(1, "login", time.time())
tracker.track_activity(1, "purchase", time.time())
tracker.track_activity(2, "login", time.time())
```

### ✓ 면접 질문 (Interview Questions)

**Q: "옵저버 패턴과 pub/sub의 차이점은?"**
- **옵저버**: Subject와 Observer가 직접 연결, 동기적 통신
- **Pub/Sub**: 중간에 메시지 브로커가 존재, 비동기적 통신, 느슨한 결합

**Q: "옵저버 패턴의 단점과 해결 방법은?"**
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

## 7. 면접 대비 요약 정리

### 7.1 실무 + 면접용 마무리 3문장 요약

1. **파이썬은 유연한 문법 덕분에 디자인 패턴을 간결하게 구현할 수 있습니다.**
2. **특히 데코레이터, 싱글톤, 전략 패턴은 실무에서도 자주 활용되며, 코드 확장성과 유지보수성을 높여줍니다.**
3. **면접에서는 패턴 개념뿐 아니라 왜 필요한가?, 실무에서 어떻게 썼는가?까지 이야기할 수 있어야 합니다.**

### 7.2 면접 대비 핵심 포인트

#### 팩토리 패턴
- **핵심**: 객체 생성 로직 캡슐화
- **면접 질문**: "객체 생성 분기를 어떻게 유연하게 관리하나요?"
- **답변 포인트**: 딕셔너리 매핑, 설정 기반 동적 팩토리, 확장 가능한 구조

#### 전략 패턴
- **핵심**: 런타임 알고리즘 교체
- **면접 질문**: "전략 패턴과 if-else 구조의 차이는?"
- **답변 포인트**: 확장성, 유지보수성, 의존성 주입과의 연계

#### 데코레이터 패턴
- **핵심**: 기능 추가와 분리
- **면접 질문**: "데코레이터가 내부적으로 어떻게 동작하나요?"
- **답변 포인트**: 함수 래핑, 클로저 활용, 메타데이터 유지

#### 싱글톤 패턴
- **핵심**: 단일 인스턴스 보장
- **면접 질문**: "모듈을 싱글톤처럼 사용하는 방식과의 차이점은?"
- **답변 포인트**: 명시적 제어 vs 자동 보장, 상속과 다형성 지원

#### 옵저버 패턴
- **핵심**: 상태 변화 자동 알림
- **면접 질문**: "옵저버 패턴과 pub/sub의 차이점은?"
- **답변 포인트**: 직접 연결 vs 메시지 브로커, 동기 vs 비동기

### 7.3 실무 경험 어필 전략

**"실무에서 디자인 패턴을 활용한 경험"**
- **상황**: 대규모 사용자 관리 시스템 구축
- **행동**: 팩토리 패턴으로 다양한 사용자 타입별 처리 객체 생성
- **결과**: 새로운 사용자 타입 추가 시 기존 코드 수정 없이 확장 가능

**"성능 최적화를 위한 패턴 활용"**
- **상황**: API 응답 시간 개선 필요
- **행동**: 데코레이터 패턴으로 캐싱, 로깅, 성능 측정 기능 분리
- **결과**: 응답 시간 30% 단축, 코드 가독성 향상

---

<details>
<summary>참고 자료</summary>

- [Design Patterns: Elements of Reusable Object-Oriented Software](https://en.wikipedia.org/wiki/Design_Patterns)
- [Python Design Patterns](https://python-patterns.guide/)
- [Real Python - Design Patterns](https://realpython.com/python-design-patterns/)
- [Python Decorators](https://docs.python.org/3/glossary.html#term-decorator)
- [Python Metaclasses](https://docs.python.org/3/reference/datamodel.html#metaclasses)

</details> 




