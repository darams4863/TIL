import redis
import time

"""
[예시 시나리오]
🌐 웹사이트 캐싱 시스템
    1. HTML 페이지 캐싱
    2. 조회수 카운터
    3. 사용자 정보 일괄 관리
    4. 조건부 데이터 설정

특징:
- Binary-safe 문자열 (HTML, JSON, 이미지 등 저장 가능)
- 최대 512MB까지 저장 가능
- TTL 설정으로 자동 만료 관리
"""

# Redis 연결
r = redis.Redis(host='localhost', port=6379, db=0)

def html_caching_example():
    """HTML 페이지 캐싱 예제"""
    print("🌐 HTML 캐싱 시스템 시연")
    print("-" * 40)
    
    # 1. HTML 페이지 캐싱
    html_content = "<html><body><h1>Welcome to My Site</h1><p>This is cached content</p></body></html>"
    r.set('homepage', html_content)
    print(f"✅ HTML 페이지 캐시 저장: {len(html_content)} bytes")
    
    # 2. 캐시된 HTML 조회
    cached_html = r.get('homepage')
    print(f"📖 캐시된 HTML 조회: {cached_html.decode('utf-8')[:50]}...")
    
    # 3. TTL이 있는 캐시 설정 (30초)
    r.setex('homepage_cache', 30, html_content)
    ttl = r.ttl('homepage_cache')
    print(f"⏰ 캐시 TTL 설정: {ttl}초 남음")
    
    # 4. TTL 확인
    time.sleep(1)
    remaining_ttl = r.ttl('homepage_cache')
    print(f"⏰ 1초 후 TTL: {remaining_ttl}초 남음")

def view_counter_example():
    """조회수 카운터 예제"""
    print("\n📊 조회수 카운터 시스템 시연")
    print("-" * 40)
    
    # 1. 초기 조회수 설정
    r.set('view_count', 0)
    print("📊 조회수 초기화: 0")
    
    # 2. 조회수 증가 시뮬레이션
    for i in range(5):
        r.incr('view_count')
        current_count = r.get('view_count')
        print(f"👀 방문자 {i+1}: 조회수 {current_count.decode('utf-8')}")
        time.sleep(0.2)
    
    # 3. 감소도 가능
    r.decr('view_count')
    final_count = r.get('view_count')
    print(f"📉 조회수 감소 후: {final_count.decode('utf-8')}")

def user_info_example():
    """사용자 정보 일괄 관리 예제"""
    print("\n👤 사용자 정보 관리 시스템 시연")
    print("-" * 40)
    
    # 1. 여러 사용자 정보 한번에 설정
    user_data = {
        'user:1:name': 'Alice',
        'user:1:age': '25',
        'user:1:city': 'Seoul',
        'user:1:email': 'alice@example.com'
    }
    r.mset(user_data)
    print("✅ 사용자 정보 일괄 저장 완료")
    
    # 2. 여러 정보 한번에 조회
    keys = ['user:1:name', 'user:1:age', 'user:1:city', 'user:1:email']
    user_info = r.mget(keys)
    
    print("📖 사용자 정보 조회:")
    for key, value in zip(keys, user_info):
        print(f"  {key}: {value.decode('utf-8')}")

def conditional_setting_example():
    """조건부 설정 예제"""
    print("\n🔒 조건부 설정 시스템 시연")
    print("-" * 40)
    
    # 1. 키가 없을 때만 설정 (SETNX)
    result1 = r.setnx('unique_key', 'first_value')
    print(f"🔒 첫 번째 설정 시도: {'성공' if result1 else '실패'}")
    
    result2 = r.setnx('unique_key', 'second_value')
    print(f"🔒 두 번째 설정 시도: {'성공' if result2 else '실패'}")
    
    # 2. 실제 저장된 값 확인
    stored_value = r.get('unique_key')
    print(f"📖 저장된 값: {stored_value.decode('utf-8')}")
    
    # 3. 키가 있을 때만 업데이트 (SET + XX)
    r.set('existing_key', 'old_value')
    r.set('existing_key', 'new_value', xx=True)  # 키가 있을 때만 업데이트
    updated_value = r.get('existing_key')
    print(f"📝 업데이트된 값: {updated_value.decode('utf-8')}")

def json_caching_example():
    """JSON 데이터 캐싱 예제"""
    print("\n📄 JSON 데이터 캐싱 시스템 시연")
    print("-" * 40)
    
    import json
    
    # 1. JSON 데이터 생성
    product_data = {
        'id': 'P001',
        'name': 'iPhone 15',
        'price': 1200000,
        'category': 'Electronics',
        'in_stock': True,
        'tags': ['smartphone', 'apple', '5g']
    }
    
    # 2. JSON을 문자열로 캐싱
    json_string = json.dumps(product_data, ensure_ascii=False)
    r.setex('product:P001', 60, json_string)  # 60초 TTL
    print(f"✅ JSON 데이터 캐싱: {len(json_string)} bytes")
    
    # 3. 캐시된 JSON 조회 및 파싱
    cached_json = r.get('product:P001')
    if cached_json:
        product = json.loads(cached_json.decode('utf-8'))
        print(f"📖 캐시된 상품 정보: {product['name']} - {product['price']}원")
    
    # 4. TTL 확인
    ttl = r.ttl('product:P001')
    print(f"⏰ JSON 캐시 TTL: {ttl}초 남음")

def main():
    print("🔤 Redis Strings 자료구조 실습")
    print("=" * 60)
    
    # 각 예제 실행
    html_caching_example()
    view_counter_example()
    user_info_example()
    conditional_setting_example()
    json_caching_example()
    
    print("\n" + "=" * 60)
    print("🎉 Strings 실습 완료!")
    print("\n💡 핵심 포인트:")
    print("1. Binary-safe 문자열로 HTML, JSON, 이미지 등 저장 가능")
    print("2. TTL 설정으로 자동 만료 관리")
    print("3. INCR/DECR로 카운터 구현")
    print("4. MSET/MGET으로 일괄 처리")
    print("5. SETNX로 조건부 설정 (중복 방지)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 프로그램 종료")
    except redis.ConnectionError:
        print("❌ Redis 연결 실패. Redis 서버가 실행 중인지 확인하세요.") 