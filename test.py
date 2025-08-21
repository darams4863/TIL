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
    # print(say_hello("Alice"))
    print()
    print(unstable_greet("Bob"))
