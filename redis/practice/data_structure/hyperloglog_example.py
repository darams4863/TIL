import redis
import time

"""
[예시 시나리오]
📊 대용량 데이터 집계 시스템
    1. 일일 UV(Unique Visitor) 집계
    2. 광고 클릭 수 추정
    3. 이벤트 참여자 수 추정
    4. 월간 통계 병합

특징:
- 대용량 데이터의 유니크 개수 추정
- 메모리 사용량 고정 (12KB)
- 약 ±0.81% 오차
- 데이터 보호 (개별 데이터 조회 불가)
"""

# Redis 연결
r = redis.Redis(host='localhost', port=6379, db=0)

def daily_uv_example():
    """일일 UV(Unique Visitor) 집계 예제"""
    print("📊 일일 UV 집계 시스템 시연")
    print("-" * 40)
    
    daily_uv_key = "daily_uv:2024:01:30"
    
    # 1. 일일 방문자 IP 추가
    visitor_ips = [
        '192.168.1.100',
        '192.168.1.101',
        '192.168.1.102',
        '192.168.1.103',
        '192.168.1.104',
        '192.168.1.100',  # 중복 IP (카운트에 영향 없음)
        '192.168.1.105',
        '192.168.1.106',
        '192.168.1.101',  # 중복 IP (카운트에 영향 없음)
        '192.168.1.107'
    ]
    
    print("👥 일일 방문자 IP 추가:")
    for ip in visitor_ips:
        r.pfadd(daily_uv_key, ip)
        print(f"  {ip}")
    
    # 2. 방문자 수 추정
    estimated_uv = r.pfcount(daily_uv_key)
    actual_uv = len(set(visitor_ips))  # 실제 유니크 IP 수
    print(f"\n📊 방문자 수 추정:")
    print(f"  추정된 UV: {estimated_uv}명")
    print(f"  실제 UV: {actual_uv}명")
    print(f"  오차: {abs(estimated_uv - actual_uv)}명")
    
    # 3. 메모리 사용량 확인
    memory_usage = r.memory_usage(daily_uv_key)
    print(f"💾 메모리 사용량: {memory_usage} bytes")

def ad_click_tracking_example():
    """광고 클릭 수 추적 예제"""
    print("\n🎯 광고 클릭 수 추적 시스템 시연")
    print("-" * 40)
    
    ad_clicks_key = "ad_clicks:summer_campaign"
    
    # 1. 광고 클릭 이벤트 추가
    click_events = [
        'user_001',
        'user_002',
        'user_003',
        'user_004',
        'user_005',
        'user_001',  # 중복 클릭 (카운트에 영향 없음)
        'user_006',
        'user_007',
        'user_002',  # 중복 클릭 (카운트에 영향 없음)
        'user_008',
        'user_009',
        'user_010'
    ]
    
    print("🎯 광고 클릭 이벤트 추가:")
    for user_id in click_events:
        r.pfadd(ad_clicks_key, user_id)
        print(f"  {user_id}")
    
    # 2. 클릭한 유니크 사용자 수 추정
    estimated_clicks = r.pfcount(ad_clicks_key)
    actual_clicks = len(set(click_events))
    print(f"\n📊 클릭한 유니크 사용자 수:")
    print(f"  추정된 클릭 수: {estimated_clicks}명")
    print(f"  실제 클릭 수: {actual_clicks}명")
    print(f"  오차: {abs(estimated_clicks - actual_clicks)}명")

def event_participation_example():
    """이벤트 참여자 수 추정 예제"""
    print("\n🎉 이벤트 참여자 수 추정 시스템 시연")
    print("-" * 40)
    
    event_key = "event:summer_festival"
    
    # 1. 이벤트 참여자 등록
    participants = []
    for i in range(1000):  # 1000명의 참여자 시뮬레이션
        user_id = f"user_{i:04d}"
        participants.append(user_id)
        r.pfadd(event_key, user_id)
    
    # 중복 참여 시도 (실제로는 무시됨)
    duplicate_participants = ['user_0001', 'user_0005', 'user_0010']
    for user_id in duplicate_participants:
        r.pfadd(event_key, user_id)
    
    print(f"🎉 이벤트 참여자 등록 완료:")
    print(f"  등록된 참여자: {len(participants)}명")
    print(f"  중복 참여 시도: {len(duplicate_participants)}명")
    
    # 2. 참여자 수 추정
    estimated_participants = r.pfcount(event_key)
    actual_participants = len(set(participants))
    print(f"\n📊 참여자 수 추정:")
    print(f"  추정된 참여자: {estimated_participants}명")
    print(f"  실제 참여자: {actual_participants}명")
    print(f"  오차: {abs(estimated_participants - actual_participants)}명")
    print(f"  오차율: {abs(estimated_participants - actual_participants) / actual_participants * 100:.2f}%")

def monthly_statistics_example():
    """월간 통계 병합 예제"""
    print("\n📈 월간 통계 병합 시스템 시연")
    print("-" * 40)
    
    # 1. 일별 UV 데이터 생성
    daily_keys = []
    for day in range(1, 8):  # 1주일 데이터
        daily_key = f"daily_uv:2024:01:{day:02d}"
        daily_keys.append(daily_key)
        
        # 각 일별로 100-200명의 방문자 시뮬레이션
        import random
        daily_visitors = random.randint(100, 200)
        for i in range(daily_visitors):
            visitor_id = f"visitor_{day}_{i}"
            r.pfadd(daily_key, visitor_id)
        
        daily_count = r.pfcount(daily_key)
        print(f"  {daily_key}: {daily_count}명")
    
    # 2. 월간 통계 생성
    monthly_key = "monthly_uv:2024:01"
    
    # 일별 데이터를 월간 데이터에 병합
    r.pfmerge(monthly_key, *daily_keys)
    
    # 3. 월간 UV 추정
    monthly_uv = r.pfcount(monthly_key)
    print(f"\n📊 월간 UV 추정:")
    print(f"  월간 UV: {monthly_uv}명")
    
    # 4. 개별 일별 합계와 비교
    daily_sum = sum(r.pfcount(key) for key in daily_keys)
    print(f"  일별 합계: {daily_sum}명")
    print(f"  중복 제거 효과: {daily_sum - monthly_uv}명")

def hll_operations_example():
    """HyperLogLog 고급 연산 예제"""
    print("\n🔧 HyperLogLog 고급 연산 시연")
    print("-" * 40)
    
    # 1. 여러 HLL 비교
    hll1_key = "hll_test_1"
    hll2_key = "hll_test_2"
    
    # HLL1에 데이터 추가
    for i in range(100):
        r.pfadd(hll1_key, f"item_{i}")
    
    # HLL2에 데이터 추가 (일부 중복)
    for i in range(50, 150):  # 50개 중복
        r.pfadd(hll2_key, f"item_{i}")
    
    count1 = r.pfcount(hll1_key)
    count2 = r.pfcount(hll2_key)
    
    print(f"📊 개별 HLL 카운트:")
    print(f"  HLL1: {count1}개")
    print(f"  HLL2: {count2}개")
    
    # 2. 병합된 HLL 카운트
    merged_key = "hll_merged"
    r.pfmerge(merged_key, hll1_key, hll2_key)
    merged_count = r.pfcount(merged_key)
    
    print(f"\n🔗 병합된 HLL 카운트:")
    print(f"  병합 결과: {merged_count}개")
    print(f"  개별 합계: {count1 + count2}개")
    print(f"  중복 제거 효과: {count1 + count2 - merged_count}개")

def memory_efficiency_example():
    """메모리 효율성 비교 예제"""
    print("\n💾 메모리 효율성 비교 시연")
    print("-" * 40)
    
    # 1. HyperLogLog로 10만개 데이터 저장
    hll_key = "hll_large_dataset"
    for i in range(100000):
        r.pfadd(hll_key, f"data_{i}")
    
    hll_count = r.pfcount(hll_key)
    hll_memory = r.memory_usage(hll_key)
    
    print(f"📊 HyperLogLog (10만개 데이터):")
    print(f"  추정된 개수: {hll_count}개")
    print(f"  메모리 사용량: {hll_memory} bytes")
    
    # 2. Set으로 같은 데이터 저장 (비교용)
    set_key = "set_large_dataset"
    for i in range(1000):  # Set은 메모리 제한으로 1000개만
        r.sadd(set_key, f"data_{i}")
    
    set_count = r.scard(set_key)
    set_memory = r.memory_usage(set_key)
    
    print(f"\n📊 Set (1000개 데이터):")
    print(f"  정확한 개수: {set_count}개")
    print(f"  메모리 사용량: {set_memory} bytes")
    
    print(f"\n💡 메모리 효율성:")
    print(f"  HLL (10만개): {hll_memory} bytes")
    print(f"  Set (1000개): {set_memory} bytes")
    print(f"  HLL이 Set보다 {set_memory / hll_memory:.1f}배 메모리 효율적")

def main():
    print("📊 Redis HyperLogLog 자료구조 실습")
    print("=" * 60)
    
    # 각 예제 실행
    daily_uv_example()
    ad_click_tracking_example()
    event_participation_example()
    monthly_statistics_example()
    hll_operations_example()
    memory_efficiency_example()
    
    print("\n" + "=" * 60)
    print("🎉 HyperLogLog 실습 완료!")
    print("\n💡 핵심 포인트:")
    print("1. 대용량 데이터의 유니크 개수 추정")
    print("2. 메모리 사용량 고정 (12KB)")
    print("3. 약 ±0.81% 오차 허용")
    print("4. PFMERGE로 여러 HLL 병합")
    print("5. 데이터 보호 (개별 데이터 조회 불가)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 프로그램 종료")
    except redis.ConnectionError:
        print("❌ Redis 연결 실패. Redis 서버가 실행 중인지 확인하세요.") 