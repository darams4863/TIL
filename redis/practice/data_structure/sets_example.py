import redis
import time

"""
[예시 시나리오]
🏷️ 태그 관리 및 추천 시스템
    1. 게시물 태그 관리
    2. 중복 방지 큐
    3. 추천 시스템 (교집합/합집합)
    4. 일일 접속 사용자 관리

특징:
- 중복 없는 유니크한 요소들
- 정렬되지 않은 집합
- 빠른 집합 연산 (교집합, 합집합, 차집합)
- 멤버 존재 여부 빠른 확인
"""

# Redis 연결
r = redis.Redis(host='localhost', port=6379, db=0)

def tag_management_example():
    """게시물 태그 관리 예제"""
    print("🏷️ 게시물 태그 관리 시스템 시연")
    print("-" * 40)
    
    # 1. 게시물별 태그 추가
    posts = {
        'post:1001': ['redis', 'database', 'nosql', 'cache'],
        'post:1002': ['redis', 'performance', 'optimization'],
        'post:1003': ['database', 'sql', 'nosql'],
        'post:1004': ['python', 'redis', 'api'],
        'post:1005': ['javascript', 'redis', 'frontend']
    }
    
    print("📝 게시물 태그 추가:")
    for post_id, tags in posts.items():
        r.sadd(post_id + ':tags', *tags)
        print(f"  {post_id}: {', '.join(tags)}")
    
    # 2. 특정 게시물의 태그 조회
    post_id = 'post:1001'
    tags = r.smembers(post_id + ':tags')
    print(f"\n📖 {post_id}의 태그:")
    for tag in tags:
        print(f"  {tag.decode('utf-8')}")
    
    # 3. 태그 개수 확인
    tag_count = r.scard(post_id + ':tags')
    print(f"📊 태그 개수: {tag_count}개")
    
    # 4. 특정 태그 존재 여부 확인
    check_tags = ['redis', 'python', 'javascript']
    print(f"\n🔍 태그 존재 여부 확인:")
    for tag in check_tags:
        exists = r.sismember(post_id + ':tags', tag)
        status = "존재함" if exists else "존재하지 않음"
        print(f"  {tag}: {status}")

def unique_queue_example():
    """중복 방지 큐 예제"""
    print("\n🔄 중복 방지 큐 시스템 시연")
    print("-" * 40)
    
    processed_jobs_key = "processed_jobs"
    
    # 1. 처리된 작업 ID 등록
    job_ids = ['job_123', 'job_456', 'job_789', 'job_101', 'job_202']
    
    print("✅ 처리된 작업 등록:")
    for job_id in job_ids:
        r.sadd(processed_jobs_key, job_id)
        print(f"  {job_id}")
    
    # 2. 새로운 작업 중복 확인
    new_jobs = ['job_123', 'job_999', 'job_456', 'job_777']
    
    print(f"\n🔍 새로운 작업 중복 확인:")
    for job_id in new_jobs:
        is_processed = r.sismember(processed_jobs_key, job_id)
        if is_processed:
            print(f"  {job_id}: 이미 처리됨 (중복)")
        else:
            print(f"  {job_id}: 새로운 작업 (처리 가능)")
            r.sadd(processed_jobs_key, job_id)
    
    # 3. 처리된 작업 수 확인
    total_processed = r.scard(processed_jobs_key)
    print(f"\n📊 총 처리된 작업 수: {total_processed}개")

def recommendation_system_example():
    """추천 시스템 예제"""
    print("\n🎯 추천 시스템 시연")
    print("-" * 40)
    
    # 1. VIP 고객이 주문한 상품들
    vip_orders_key = "vip_orders"
    vip_products = ['product_001', 'product_002', 'product_003', 'product_004', 'product_005']
    r.sadd(vip_orders_key, *vip_products)
    print(f"👑 VIP 고객 주문 상품: {', '.join(vip_products)}")
    
    # 2. 추천 서비스를 이용한 주문들
    recommended_orders_key = "recommended_service_orders"
    recommended_products = ['product_002', 'product_003', 'product_005', 'product_006', 'product_007']
    r.sadd(recommended_orders_key, *recommended_products)
    print(f"🎯 추천 서비스 주문 상품: {', '.join(recommended_products)}")
    
    # 3. 교집합: VIP 고객이 추천 서비스를 이용한 상품
    intersection = r.sinter(vip_orders_key, recommended_orders_key)
    print(f"\n🔗 VIP + 추천 서비스 교집합:")
    for product in intersection:
        print(f"  {product.decode('utf-8')}")
    
    # 4. 합집합: 모든 주문 상품
    union = r.sunion(vip_orders_key, recommended_orders_key)
    print(f"\n📦 모든 주문 상품 (합집합):")
    for product in union:
        print(f"  {product.decode('utf-8')}")
    
    # 5. 차집합: VIP만 주문한 상품
    vip_only = r.sdiff(vip_orders_key, recommended_orders_key)
    print(f"\n👑 VIP만 주문한 상품 (차집합):")
    for product in vip_only:
        print(f"  {product.decode('utf-8')}")

def daily_users_example():
    """일일 접속 사용자 관리 예제"""
    print("\n👥 일일 접속 사용자 관리 시스템 시연")
    print("-" * 40)
    
    daily_users_key = "daily_users:2024:01:30"
    
    # 1. 일일 접속 사용자 등록
    user_ids = ['user_001', 'user_002', 'user_003', 'user_004', 'user_005']
    
    print("👤 일일 접속 사용자 등록:")
    for user_id in user_ids:
        r.sadd(daily_users_key, user_id)
        print(f"  {user_id}")
    
    # 2. 중복 접속 시도 (중복은 자동으로 무시됨)
    duplicate_users = ['user_001', 'user_003', 'user_006', 'user_007']
    
    print(f"\n🔄 중복 접속 시도:")
    for user_id in duplicate_users:
        result = r.sadd(daily_users_key, user_id)
        if result == 1:
            print(f"  {user_id}: 새로운 접속")
        else:
            print(f"  {user_id}: 중복 접속 (무시됨)")
    
    # 3. 일일 접속자 수 확인
    daily_count = r.scard(daily_users_key)
    print(f"\n📊 일일 접속자 수: {daily_count}명")
    
    # 4. TTL 설정 (24시간 후 자동 삭제)
    r.expire(daily_users_key, 86400)  # 24시간
    ttl = r.ttl(daily_users_key)
    print(f"⏰ TTL 설정: {ttl}초 남음")

def set_operations_example():
    """Set 고급 연산 예제"""
    print("\n🔧 Set 고급 연산 시연")
    print("-" * 40)
    
    # 1. 랜덤 요소 제거 및 반환
    test_set_key = "test_set"
    test_elements = ['apple', 'banana', 'cherry', 'date', 'elderberry']
    r.sadd(test_set_key, *test_elements)
    
    print("🎲 랜덤 요소 제거:")
    for i in range(3):
        random_element = r.spop(test_set_key)
        if random_element:
            print(f"  제거된 요소: {random_element.decode('utf-8')}")
    
    # 2. 랜덤 요소 조회 (제거하지 않음)
    remaining_elements = r.smembers(test_set_key)
    print(f"\n📋 남은 요소들:")
    for element in remaining_elements:
        print(f"  {element.decode('utf-8')}")
    
    # 3. 특정 요소 제거
    r.srem(test_set_key, 'date')
    print(f"\n🗑️ 'date' 요소 제거")
    
    # 4. 랜덤 요소 조회 (여러 개)
    random_elements = r.srandmember(test_set_key, 2)
    print(f"\n🎲 랜덤 요소 2개 조회:")
    for element in random_elements:
        print(f"  {element.decode('utf-8')}")

def set_intersection_example():
    """Set 교집합 연산 예제"""
    print("\n🔗 Set 교집합 연산 시연")
    print("-" * 40)
    
    # 1. 여러 그룹의 관심사 생성
    group1_key = "group1_interests"
    group2_key = "group2_interests"
    group3_key = "group3_interests"
    
    group1_interests = ['redis', 'python', 'database', 'api']
    group2_interests = ['redis', 'javascript', 'frontend', 'api']
    group3_interests = ['python', 'machine_learning', 'api', 'data']
    
    r.sadd(group1_key, *group1_interests)
    r.sadd(group2_key, *group2_interests)
    r.sadd(group3_key, *group3_interests)
    
    print("👥 그룹별 관심사:")
    print(f"  그룹1: {', '.join(group1_interests)}")
    print(f"  그룹2: {', '.join(group2_interests)}")
    print(f"  그룹3: {', '.join(group3_interests)}")
    
    # 2. 모든 그룹의 공통 관심사 (교집합)
    common_interests = r.sinter(group1_key, group2_key, group3_key)
    print(f"\n🔗 모든 그룹의 공통 관심사:")
    for interest in common_interests:
        print(f"  {interest.decode('utf-8')}")
    
    # 3. 그룹1과 그룹2의 공통 관심사
    group1_2_common = r.sinter(group1_key, group2_key)
    print(f"\n🔗 그룹1과 그룹2의 공통 관심사:")
    for interest in group1_2_common:
        print(f"  {interest.decode('utf-8')}")

def main():
    print("🔗 Redis Sets 자료구조 실습")
    print("=" * 60)
    
    # 각 예제 실행
    tag_management_example()
    unique_queue_example()
    recommendation_system_example()
    daily_users_example()
    set_operations_example()
    set_intersection_example()
    
    print("\n" + "=" * 60)
    print("🎉 Sets 실습 완료!")
    print("\n💡 핵심 포인트:")
    print("1. 중복 없는 유니크한 요소들 저장")
    print("2. 빠른 멤버 존재 여부 확인 (SISMEMBER)")
    print("3. 집합 연산으로 추천 시스템 구현")
    print("4. SPOP으로 랜덤 요소 제거")
    print("5. SINTER/SUNION/SDIFF로 집합 연산")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 프로그램 종료")
    except redis.ConnectionError:
        print("❌ Redis 연결 실패. Redis 서버가 실행 중인지 확인하세요.") 