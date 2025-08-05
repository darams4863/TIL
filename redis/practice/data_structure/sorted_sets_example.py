import redis
import time

"""
[예시 시나리오]
🏆 실시간 랭킹 시스템
    1. 게임 점수판
    2. 인기 상품 순위
    3. 우선순위 큐
    4. 지연 큐 구현

특징:
- Score(가중치) 기반 정렬
- Value는 중복 불가, Score는 중복 가능
- Score 순으로 오름차순 정렬
- 빠른 순위 조회 및 범위 검색
"""

# Redis 연결
r = redis.Redis(host='localhost', port=6379, db=0)

def game_leaderboard_example():
    """게임 점수판 예제"""
    print("🏆 게임 점수판 시스템 시연")
    print("-" * 40)
    
    leaderboard_key = "game:leaderboard"
    
    # 1. 플레이어 점수 등록
    players = [
        ('player_001', 1250),
        ('player_002', 980),
        ('player_003', 2100),
        ('player_004', 750),
        ('player_005', 1800),
        ('player_006', 1450),
        ('player_007', 900),
        ('player_008', 1950)
    ]
    
    print("🎮 플레이어 점수 등록:")
    for player, score in players:
        r.zadd(leaderboard_key, {player: score})
        print(f"  {player}: {score}점")
    
    # 2. 상위 3명 조회 (높은 점수 순)
    top_players = r.zrevrange(leaderboard_key, 0, 2, withscores=True)
    print(f"\n🥇 상위 3명:")
    for i, (player, score) in enumerate(top_players, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        print(f"  {medal} {i}위: {player.decode('utf-8')} - {int(score)}점")
    
    # 3. 특정 플레이어 순위 확인
    player_id = 'player_003'
    rank = r.zrevrank(leaderboard_key, player_id)
    score = r.zscore(leaderboard_key, player_id)
    print(f"\n📊 {player_id} 순위: {rank + 1}위 ({int(score)}점)")
    
    # 4. 점수 범위 조회 (1000점 이상)
    high_scorers = r.zrangebyscore(leaderboard_key, 1000, '+inf', withscores=True)
    print(f"\n🎯 1000점 이상 플레이어:")
    for player, score in high_scorers:
        print(f"  {player.decode('utf-8')}: {int(score)}점")

def popular_products_example():
    """인기 상품 순위 예제"""
    print("\n🔥 인기 상품 순위 시스템 시연")
    print("-" * 40)
    
    popular_key = "products:popular"
    
    # 1. 상품별 좋아요 수 등록
    products = [
        ('product_001', 1234),  # 좋아요 수
        ('product_002', 567),
        ('product_003', 890),
        ('product_004', 2345),
        ('product_005', 678),
        ('product_006', 1456),
        ('product_007', 789),
        ('product_008', 2100)
    ]
    
    print("📦 상품별 좋아요 수 등록:")
    for product, likes in products:
        r.zadd(popular_key, {product: likes})
        print(f"  {product}: {likes}개 좋아요")
    
    # 2. 인기 상품 TOP 5
    top_products = r.zrevrange(popular_key, 0, 4, withscores=True)
    print(f"\n🔥 인기 상품 TOP 5:")
    for i, (product, likes) in enumerate(top_products, 1):
        print(f"  {i}위: {product.decode('utf-8')} - {int(likes)}개 좋아요")
    
    # 3. 특정 상품 순위 확인
    product_id = 'product_004'
    rank = r.zrevrank(popular_key, product_id)
    likes = r.zscore(popular_key, product_id)
    print(f"\n📊 {product_id} 순위: {rank + 1}위 ({int(likes)}개 좋아요)")
    
    # 4. 좋아요 수 범위 조회 (1000개 이상)
    popular_range = r.zrangebyscore(popular_key, 1000, '+inf', withscores=True)
    print(f"\n💖 1000개 이상 좋아요 받은 상품:")
    for product, likes in popular_range:
        print(f"  {product.decode('utf-8')}: {int(likes)}개")

def priority_queue_example():
    """우선순위 큐 예제"""
    print("\n⚡ 우선순위 큐 시스템 시연")
    print("-" * 40)
    
    priority_queue_key = "priority_queue"
    
    # 1. 작업별 우선순위 등록 (낮은 숫자가 높은 우선순위)
    tasks = [
        ('urgent_task_001', 1),    # 긴급 (우선순위 1)
        ('normal_task_001', 5),    # 일반 (우선순위 5)
        ('urgent_task_002', 1),    # 긴급 (우선순위 1)
        ('low_task_001', 10),      # 낮음 (우선순위 10)
        ('normal_task_002', 5),    # 일반 (우선순위 5)
        ('urgent_task_003', 2),    # 긴급 (우선순위 2)
        ('low_task_002', 10),      # 낮음 (우선순위 10)
        ('normal_task_003', 5)     # 일반 (우선순위 5)
    ]
    
    print("📋 작업별 우선순위 등록:")
    for task, priority in tasks:
        r.zadd(priority_queue_key, {task: priority})
        priority_name = "긴급" if priority <= 2 else "일반" if priority <= 5 else "낮음"
        print(f"  {task}: {priority_name} (우선순위 {priority})")
    
    # 2. 우선순위 순으로 작업 처리
    print(f"\n⚡ 우선순위 순 작업 처리:")
    while r.zcard(priority_queue_key) > 0:
        # 가장 높은 우선순위(낮은 점수) 작업 가져오기
        next_task = r.zrange(priority_queue_key, 0, 0, withscores=True)
        if next_task:
            task, priority = next_task[0]
            task_name = task.decode('utf-8')
            priority_name = "긴급" if priority <= 2 else "일반" if priority <= 5 else "낮음"
            print(f"  처리 중: {task_name} ({priority_name})")
            
            # 작업 처리 후 큐에서 제거
            r.zrem(priority_queue_key, task)
            time.sleep(0.2)  # 처리 시간 시뮬레이션

def delay_queue_example():
    """지연 큐 구현 예제"""
    print("\n⏰ 지연 큐 시스템 시연")
    print("-" * 40)
    
    delay_queue_key = "delay_queue"
    
    # 1. 지연 실행할 작업 등록 (실행 시간을 score로 사용)
    current_time = int(time.time())
    delayed_tasks = [
        ('email_job_001', current_time + 5),   # 5초 후 실행
        ('email_job_002', current_time + 10),  # 10초 후 실행
        ('email_job_003', current_time + 3),   # 3초 후 실행
        ('email_job_004', current_time + 8),   # 8초 후 실행
        ('email_job_005', current_time + 15)   # 15초 후 실행
    ]
    
    print("⏰ 지연 실행 작업 등록:")
    for task, execute_time in delayed_tasks:
        r.zadd(delay_queue_key, {task: execute_time})
        delay = execute_time - current_time
        print(f"  {task}: {delay}초 후 실행")
    
    # 2. 실행할 시점이 된 작업 조회
    print(f"\n📧 실행할 시점이 된 작업 조회:")
    for i in range(3):  # 3번 체크
        current_time = int(time.time())
        ready_tasks = r.zrangebyscore(delay_queue_key, 0, current_time)
        
        if ready_tasks:
            print(f"  체크 {i+1}: {len(ready_tasks)}개 작업 실행 가능")
            for task in ready_tasks:
                task_name = task.decode('utf-8')
                print(f"    실행: {task_name}")
                r.zrem(delay_queue_key, task)
        else:
            print(f"  체크 {i+1}: 실행할 작업 없음")
        
        time.sleep(2)  # 2초 대기

def ranking_operations_example():
    """랭킹 고급 연산 예제"""
    print("\n🔧 랭킹 고급 연산 시연")
    print("-" * 40)
    
    test_key = "test_ranking"
    
    # 1. 점수 업데이트
    r.zadd(test_key, {'player_A': 100, 'player_B': 200, 'player_C': 150})
    print("📊 초기 점수:")
    scores = r.zrange(test_key, 0, -1, withscores=True)
    for player, score in scores:
        print(f"  {player.decode('utf-8')}: {int(score)}점")
    
    # 2. 점수 증가
    r.zincrby(test_key, 50, 'player_A')  # player_A 점수 50 증가
    print(f"\n📈 player_A 점수 50 증가 후:")
    scores = r.zrange(test_key, 0, -1, withscores=True)
    for player, score in scores:
        print(f"  {player.decode('utf-8')}: {int(score)}점")
    
    # 3. 특정 범위의 순위 조회
    print(f"\n📋 100-200점 범위 플레이어:")
    range_players = r.zrangebyscore(test_key, 100, 200, withscores=True)
    for player, score in range_players:
        print(f"  {player.decode('utf-8')}: {int(score)}점")
    
    # 4. 역순 범위 조회 (높은 점수 순)
    print(f"\n📋 150점 이상 플레이어 (높은 점수 순):")
    high_players = r.zrevrangebyscore(test_key, '+inf', 150, withscores=True)
    for player, score in high_players:
        print(f"  {player.decode('utf-8')}: {int(score)}점")
    
    # 5. 특정 점수 범위의 개수
    count_100_200 = r.zcount(test_key, 100, 200)
    print(f"\n📊 100-200점 범위 플레이어 수: {count_100_200}명")

def main():
    print("🏆 Redis Sorted Sets 자료구조 실습")
    print("=" * 60)
    
    # 각 예제 실행
    game_leaderboard_example()
    popular_products_example()
    priority_queue_example()
    delay_queue_example()
    ranking_operations_example()
    
    print("\n" + "=" * 60)
    print("🎉 Sorted Sets 실습 완료!")
    print("\n💡 핵심 포인트:")
    print("1. Score 기반 정렬로 랭킹 시스템 구현")
    print("2. ZREVRANGE로 높은 점수 순 조회")
    print("3. ZRANGEBYSCORE로 점수 범위 검색")
    print("4. 우선순위 큐와 지연 큐 구현 가능")
    print("5. ZINCRBY로 점수 업데이트")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 프로그램 종료")
    except redis.ConnectionError:
        print("❌ Redis 연결 실패. Redis 서버가 실행 중인지 확인하세요.") 