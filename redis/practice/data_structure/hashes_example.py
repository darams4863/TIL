import redis
import time

"""
[예시 시나리오]
👤 사용자 프로필 관리 시스템
    1. 사용자 프로필 정보 저장
    2. 세션 정보 관리
    3. 상품 정보 캐싱
    4. 설정 정보 관리

특징:
- Field-Value 구조 (JSON과 유사)
- 메모리 효율적인 객체 저장
- 부분 업데이트 가능
- 중첩된 데이터 구조 표현
"""

# Redis 연결
r = redis.Redis(host='localhost', port=6379, db=0)

def user_profile_example():
    """사용자 프로필 관리 예제"""
    print("👤 사용자 프로필 관리 시스템 시연")
    print("-" * 40)
    
    user_id = 1001
    profile_key = f"user:{user_id}"
    
    # 1. 사용자 프로필 정보 저장
    profile_data = {
        'name': 'Alice Johnson',
        'age': '28',
        'email': 'alice@example.com',
        'city': 'Seoul',
        'country': 'KR',
        'join_date': '2024-01-15',
        'last_login': '2024-01-30 10:30:00',
        'status': 'active'
    }
    
    print(f"👤 사용자 {user_id} 프로필 정보 저장:")
    for field, value in profile_data.items():
        r.hset(profile_key, field, value)
        print(f"  ✅ {field}: {value}")
    
    # 2. 특정 필드 조회
    print(f"\n📖 특정 필드 조회:")
    name = r.hget(profile_key, 'name')
    email = r.hget(profile_key, 'email')
    print(f"  이름: {name.decode('utf-8')}")
    print(f"  이메일: {email.decode('utf-8')}")
    
    # 3. 여러 필드 한번에 조회
    print(f"\n📋 여러 필드 조회:")
    fields = ['name', 'age', 'city', 'status']
    values = r.hmget(profile_key, fields)
    
    for field, value in zip(fields, values):
        print(f"  {field}: {value.decode('utf-8')}")
    
    # 4. 모든 필드 조회
    print(f"\n📄 모든 프로필 정보:")
    all_data = r.hgetall(profile_key)
    for field, value in all_data.items():
        print(f"  {field.decode('utf-8')}: {value.decode('utf-8')}")
    
    # 5. 필드 개수 확인
    field_count = r.hlen(profile_key)
    print(f"\n📊 프로필 필드 개수: {field_count}개")

def session_management_example():
    """세션 정보 관리 예제"""
    print("\n🔐 세션 정보 관리 시스템 시연")
    print("-" * 40)
    
    session_id = "session:abc123"
    
    # 1. 세션 정보 저장
    session_data = {
        'user_id': '1001',
        'login_time': '2024-01-30 10:30:00',
        'last_activity': '2024-01-30 11:45:00',
        'ip_address': '192.168.1.100',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'is_active': 'true',
        'permissions': 'read,write,delete'
    }
    
    print(f"🔐 세션 {session_id} 정보 저장:")
    for field, value in session_data.items():
        r.hset(session_id, field, value)
        print(f"  ✅ {field}: {value}")
    
    # 2. 세션 활동 업데이트
    new_activity = '2024-01-30 12:15:00'
    r.hset(session_id, 'last_activity', new_activity)
    print(f"\n⏰ 마지막 활동 시간 업데이트: {new_activity}")
    
    # 3. 세션 유효성 확인
    is_active = r.hget(session_id, 'is_active')
    if is_active and is_active.decode('utf-8') == 'true':
        print("✅ 세션이 활성 상태입니다.")
    else:
        print("❌ 세션이 비활성 상태입니다.")
    
    # 4. 세션 정보 요약
    print(f"\n📋 세션 정보 요약:")
    summary_fields = ['user_id', 'login_time', 'last_activity', 'ip_address']
    summary = r.hmget(session_id, summary_fields)
    
    for field, value in zip(summary_fields, summary):
        print(f"  {field}: {value.decode('utf-8')}")

def product_caching_example():
    """상품 정보 캐싱 예제"""
    print("\n📦 상품 정보 캐싱 시스템 시연")
    print("-" * 40)
    
    product_id = "P001"
    product_key = f"product:{product_id}"
    
    # 1. 상품 정보 저장
    product_data = {
        'name': 'iPhone 15 Pro',
        'price': '1500000',
        'category': 'Electronics',
        'brand': 'Apple',
        'color': 'Titanium',
        'storage': '256GB',
        'in_stock': 'true',
        'rating': '4.8',
        'review_count': '1250',
        'description': '최신 iPhone 15 Pro 모델입니다.',
        'image_url': 'https://example.com/iphone15pro.jpg'
    }
    
    print(f"📦 상품 {product_id} 정보 캐싱:")
    for field, value in product_data.items():
        r.hset(product_key, field, value)
        print(f"  ✅ {field}: {value}")
    
    # 2. 상품 가격 업데이트
    new_price = '1450000'
    r.hset(product_key, 'price', new_price)
    print(f"\n💰 가격 업데이트: {new_price}원")
    
    # 3. 재고 상태 확인
    in_stock = r.hget(product_key, 'in_stock')
    if in_stock and in_stock.decode('utf-8') == 'true':
        print("✅ 상품이 재고에 있습니다.")
    else:
        print("❌ 상품이 재고에 없습니다.")
    
    # 4. 상품 요약 정보
    print(f"\n📋 상품 요약 정보:")
    summary_fields = ['name', 'price', 'brand', 'rating', 'review_count']
    summary = r.hmget(product_key, summary_fields)
    
    for field, value in zip(summary_fields, summary):
        print(f"  {field}: {value.decode('utf-8')}")

def settings_management_example():
    """설정 정보 관리 예제"""
    print("\n⚙️ 설정 정보 관리 시스템 시연")
    print("-" * 40)
    
    app_settings_key = "app:settings"
    
    # 1. 애플리케이션 설정 저장
    settings_data = {
        'debug_mode': 'false',
        'log_level': 'INFO',
        'cache_ttl': '3600',
        'max_connections': '100',
        'timeout': '30',
        'language': 'ko',
        'theme': 'dark',
        'notifications': 'true',
        'auto_save': 'true',
        'backup_interval': '24'
    }
    
    print(f"⚙️ 애플리케이션 설정 저장:")
    for field, value in settings_data.items():
        r.hset(app_settings_key, field, value)
        print(f"  ✅ {field}: {value}")
    
    # 2. 설정 변경
    r.hset(app_settings_key, 'debug_mode', 'true')
    r.hset(app_settings_key, 'log_level', 'DEBUG')
    print(f"\n🔧 설정 변경:")
    print(f"  debug_mode: true")
    print(f"  log_level: DEBUG")
    
    # 3. 설정 확인
    print(f"\n📋 현재 설정:")
    current_settings = r.hgetall(app_settings_key)
    for field, value in current_settings.items():
        print(f"  {field.decode('utf-8')}: {value.decode('utf-8')}")
    
    # 4. 설정 필드 존재 확인
    print(f"\n🔍 설정 필드 존재 확인:")
    fields_to_check = ['debug_mode', 'log_level', 'nonexistent_field']
    for field in fields_to_check:
        exists = r.hexists(app_settings_key, field)
        status = "존재함" if exists else "존재하지 않음"
        print(f"  {field}: {status}")

def hash_operations_example():
    """Hash 고급 연산 예제"""
    print("\n🔧 Hash 고급 연산 시연")
    print("-" * 40)
    
    test_key = "test:hash"
    
    # 1. 숫자 필드 증가/감소
    r.hset(test_key, 'counter', 0)
    r.hincrby(test_key, 'counter', 5)  # 5 증가
    r.hincrby(test_key, 'counter', 3)  # 3 증가
    r.hincrby(test_key, 'counter', -2)  # 2 감소
    
    counter = r.hget(test_key, 'counter')
    print(f"📊 카운터 값: {counter.decode('utf-8')}")
    
    # 2. 부동소수점 증가
    r.hset(test_key, 'score', 0.0)
    r.hincrbyfloat(test_key, 'score', 1.5)
    r.hincrbyfloat(test_key, 'score', 2.7)
    
    score = r.hget(test_key, 'score')
    print(f"📈 점수: {score.decode('utf-8')}")
    
    # 3. 필드 이름만 조회
    field_names = r.hkeys(test_key)
    print(f"\n📝 필드 이름들:")
    for field in field_names:
        print(f"  {field.decode('utf-8')}")
    
    # 4. 값만 조회
    values = r.hvals(test_key)
    print(f"\n📄 값들:")
    for value in values:
        print(f"  {value.decode('utf-8')}")
    
    # 5. 랜덤 필드 조회
    random_field = r.hrandfield(test_key)
    if random_field:
        random_value = r.hget(test_key, random_field)
        print(f"\n🎲 랜덤 필드: {random_field.decode('utf-8')} = {random_value.decode('utf-8')}")

def main():
    print("🗂️ Redis Hashes 자료구조 실습")
    print("=" * 60)
    
    # 각 예제 실행
    user_profile_example()
    session_management_example()
    product_caching_example()
    settings_management_example()
    hash_operations_example()
    
    print("\n" + "=" * 60)
    print("🎉 Hashes 실습 완료!")
    print("\n💡 핵심 포인트:")
    print("1. Field-Value 구조로 객체 데이터 저장에 최적")
    print("2. 부분 업데이트로 메모리 효율적")
    print("3. HINCRBY/HINCRBYFLOAT로 숫자 필드 연산")
    print("4. HKEYS/HVALS로 필드명/값만 조회")
    print("5. HRANDFIELD로 랜덤 필드 조회")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 프로그램 종료")
    except redis.ConnectionError:
        print("❌ Redis 연결 실패. Redis 서버가 실행 중인지 확인하세요.") 