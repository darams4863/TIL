import redis
import time

"""
[예시 시나리오]
📅 출석 체크 시스템
    1. 사용자별 일일 출석 체크
    2. 이벤트 참여자 관리
    3. 플래그 기반 상태 관리
    4. 대규모 boolean 데이터 처리

특징:
- 비트 단위로 데이터 저장 (메모리 효율적)
- 최대 2^32 비트 관리 가능 (512MB)
- 0/1 상태 저장에 최적화
- 빠른 집계 연산 지원
"""

# Redis 연결
r = redis.Redis(host='localhost', port=6379, db=0)

def attendance_check_example():
    """사용자 출석 체크 시스템 예제"""
    print("📅 출석 체크 시스템 시연")
    print("-" * 40)
    
    user_id = 1001
    month = "2024:01"
    attendance_key = f"user:{user_id}:attendance:{month}"
    
    # 1. 출석 체크 (1일 = 1비트)
    attendance_dates = [0, 5, 10, 15, 20, 25, 30]  # 1월 1일, 6일, 11일, 16일, 21일, 26일, 31일
    
    print(f"👤 사용자 {user_id}의 1월 출석 체크:")
    for day in attendance_dates:
        r.setbit(attendance_key, day, 1)
        print(f"  ✅ {day+1}일 출석 체크")
    
    # 2. 특정 날짜 출석 여부 확인
    check_dates = [0, 1, 5, 10, 15]
    print(f"\n📋 출석 여부 확인:")
    for day in check_dates:
        is_attended = r.getbit(attendance_key, day)
        status = "출석" if is_attended else "미출석"
        print(f"  {day+1}일: {status}")
    
    # 3. 전체 출석 일수 계산
    total_attendance = r.bitcount(attendance_key)
    print(f"\n📊 전체 출석 일수: {total_attendance}일")

def event_participation_example():
    """이벤트 참여자 관리 예제"""
    print("\n🎉 이벤트 참여자 관리 시스템 시연")
    print("-" * 40)
    
    event_key = "event:summer:participants"
    
    # 1. 이벤트 참여자 등록
    participants = [1001, 1002, 1005, 1008, 1010, 1015, 1020]
    non_participants = [1003, 1004, 1006, 1007, 1009]
    
    print("🎉 이벤트 참여자 등록:")
    for user_id in participants:
        r.setbit(event_key, user_id, 1)
        print(f"  ✅ 사용자 {user_id} 참여 등록")
    
    for user_id in non_participants:
        r.setbit(event_key, user_id, 0)
        print(f"  ❌ 사용자 {user_id} 미참여")
    
    # 2. 참여자 수 확인
    participant_count = r.bitcount(event_key)
    print(f"\n📊 총 참여자 수: {participant_count}명")
    
    # 3. 특정 사용자 참여 여부 확인
    check_users = [1001, 1003, 1005, 1007, 1010]
    print(f"\n👥 참여 여부 확인:")
    for user_id in check_users:
        is_participating = r.getbit(event_key, user_id)
        status = "참여" if is_participating else "미참여"
        print(f"  사용자 {user_id}: {status}")

def flag_management_example():
    """플래그 기반 상태 관리 예제"""
    print("\n🚩 플래그 기반 상태 관리 시스템 시연")
    print("-" * 40)
    
    # 1. 주문 상태 플래그 관리
    order_status_key = "order:status:flags"
    
    # 주문별 상태 설정 (0=미확인, 1=처리중, 2=완료, 3=취소)
    orders = [
        (1001, 1),  # 주문 1001: 처리중
        (1002, 2),  # 주문 1002: 완료
        (1003, 0),  # 주문 1003: 미확인
        (1004, 1),  # 주문 1004: 처리중
        (1005, 3),  # 주문 1005: 취소
    ]
    
    print("📦 주문 상태 플래그 설정:")
    for order_id, status in orders:
        # 2비트씩 사용하여 4가지 상태 표현
        bit_offset = order_id * 2
        r.setbit(order_status_key, bit_offset, status & 1)
        r.setbit(order_status_key, bit_offset + 1, (status >> 1) & 1)
        
        status_names = ["미확인", "처리중", "완료", "취소"]
        print(f"  주문 {order_id}: {status_names[status]}")
    
    # 2. 주문 상태 확인
    print(f"\n📋 주문 상태 확인:")
    for order_id, expected_status in orders:
        bit_offset = order_id * 2
        bit1 = r.getbit(order_status_key, bit_offset)
        bit2 = r.getbit(order_status_key, bit_offset + 1)
        actual_status = bit1 | (bit2 << 1)
        
        status_names = ["미확인", "처리중", "완료", "취소"]
        print(f"  주문 {order_id}: {status_names[actual_status]}")

def large_scale_boolean_example():
    """대규모 boolean 데이터 처리 예제"""
    print("\n🏭 대규모 boolean 데이터 처리 시스템 시연")
    print("-" * 40)
    
    # 1. 1억개 상품의 재고 여부 관리
    inventory_key = "product:inventory:flags"
    
    # 샘플 데이터 (실제로는 1억개)
    sample_products = [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010]
    
    print("📦 상품 재고 상태 설정:")
    for product_id in sample_products:
        # 랜덤하게 재고 있음/없음 설정
        import random
        has_stock = random.choice([True, False])
        r.setbit(inventory_key, product_id, 1 if has_stock else 0)
        status = "재고있음" if has_stock else "재고없음"
        print(f"  상품 {product_id}: {status}")
    
    # 2. 재고 있는 상품 수 계산
    in_stock_count = r.bitcount(inventory_key)
    print(f"\n📊 재고 있는 상품 수: {in_stock_count}개")
    
    # 3. 첫 번째 재고 있는 상품 찾기
    first_in_stock = r.bitpos(inventory_key, 1)
    if first_in_stock != -1:
        print(f"🔍 첫 번째 재고 있는 상품 ID: {first_in_stock}")
    else:
        print("🔍 재고 있는 상품이 없습니다.")

def bitfield_example():
    """비트필드 고급 기능 예제"""
    print("\n🔧 비트필드 고급 기능 시연")
    print("-" * 40)
    
    # 1. 사용자 권한 플래그 관리 (8비트)
    user_permissions_key = "user:permissions"
    
    # 권한 비트: [읽기][쓰기][삭제][관리자][VIP][프리미엄][베타][알림]
    user_id = 1001
    permissions = 0b11010101  # 읽기, 쓰기, 삭제, VIP, 베타, 알림 권한
    
    # 8비트 정수로 설정
    r.bitfield(user_permissions_key).set('u8', user_id * 8, permissions).execute()
    print(f"👤 사용자 {user_id} 권한 설정: {bin(permissions)}")
    
    # 2. 권한 확인
    result = r.bitfield(user_permissions_key).get('u8', user_id * 8).execute()
    actual_permissions = result[0]
    print(f"📋 실제 권한: {bin(actual_permissions)}")
    
    # 3. 개별 권한 확인
    permission_names = ["읽기", "쓰기", "삭제", "관리자", "VIP", "프리미엄", "베타", "알림"]
    print(f"\n🔐 개별 권한 확인:")
    for i, name in enumerate(permission_names):
        has_permission = (actual_permissions >> i) & 1
        status = "✅" if has_permission else "❌"
        print(f"  {name}: {status}")

def main():
    print("🔢 Redis Bitmaps 자료구조 실습")
    print("=" * 60)
    
    # 각 예제 실행
    attendance_check_example()
    event_participation_example()
    flag_management_example()
    large_scale_boolean_example()
    bitfield_example()
    
    print("\n" + "=" * 60)
    print("🎉 Bitmaps 실습 완료!")
    print("\n💡 핵심 포인트:")
    print("1. 비트 단위로 데이터 저장하여 메모리 효율적")
    print("2. 출석 체크, 이벤트 참여 등 boolean 상태 관리에 최적")
    print("3. BITCOUNT로 빠른 집계 연산")
    print("4. BITPOS로 첫 번째 1/0 비트 위치 찾기")
    print("5. BITFIELD로 비트 단위 정수 읽기/쓰기")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 프로그램 종료")
    except redis.ConnectionError:
        print("❌ Redis 연결 실패. Redis 서버가 실행 중인지 확인하세요.") 