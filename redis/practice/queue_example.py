import redis
import threading
import time
import json
from datetime import datetime

"""
[예시 시나리오]
📧 이메일 발송 시스템
    1. 사용자가 이메일 발송 요청 (생산자)
    2. 이메일 큐에 작업 추가
    3. 이메일 워커들이 큐에서 작업을 가져와서 처리 (소비자)
    4. 여러 워커가 동시에 작업 처리 (분산 처리)

특징:
- FIFO (First In, First Out) 보장
- 블로킹 방식으로 효율적인 메시지 처리
- 간단한 구조로 빠른 구현 가능
"""

# Redis 연결
r = redis.Redis(host='localhost', port=6379, db=0)

# 이메일 큐 이름
EMAIL_QUEUE = 'email_queue'
PRIORITY_QUEUE = 'priority_email_queue'

def email_producer():
    """이메일 발송 요청 생산자"""
    print("📧 이메일 발송 요청 생산자 시작...")
    
    emails = [
        {
            'to': 'user1@example.com',
            'subject': '환영합니다!',
            'body': '서비스에 가입해주셔서 감사합니다.',
            'priority': 'normal',
            'timestamp': datetime.now().isoformat()
        },
        {
            'to': 'user2@example.com',
            'subject': '주문 확인',
            'body': '주문이 성공적으로 접수되었습니다.',
            'priority': 'high',
            'timestamp': datetime.now().isoformat()
        },
        {
            'to': 'user3@example.com',
            'subject': '뉴스레터',
            'body': '이번 주 새로운 소식을 확인해보세요.',
            'priority': 'normal',
            'timestamp': datetime.now().isoformat()
        },
        {
            'to': 'user4@example.com',
            'subject': '긴급 알림',
            'body': '계정 보안을 위해 비밀번호를 변경해주세요.',
            'priority': 'high',
            'timestamp': datetime.now().isoformat()
        },
        {
            'to': 'user5@example.com',
            'subject': '배송 완료',
            'body': '주문하신 상품이 배송되었습니다.',
            'priority': 'normal',
            'timestamp': datetime.now().isoformat()
        }
    ]
    
    for i, email in enumerate(emails, 1):
        # 우선순위에 따라 다른 큐에 추가
        if email['priority'] == 'high':
            r.lpush(PRIORITY_QUEUE, json.dumps(email))
            print(f"📧 우선순위 이메일 추가: {email['to']} - {email['subject']}")
        else:
            r.lpush(EMAIL_QUEUE, json.dumps(email))
            print(f"📧 일반 이메일 추가: {email['to']} - {email['subject']}")
        
        time.sleep(0.5)  # 0.5초 간격으로 이메일 추가
    
    print("✅ 모든 이메일 발송 요청 완료")

def email_worker(worker_name, queue_name, is_priority=False):
    """이메일 발송 워커 (소비자)"""
    queue_type = "우선순위" if is_priority else "일반"
    print(f"📧 {queue_type} 이메일 워커 ({worker_name}) 시작...")
    
    while True:
        try:
            # 블로킹 방식으로 메시지 대기 (1초 타임아웃)
            result = r.brpop(queue_name, timeout=1)
            
            if result:
                queue_name, message_data = result
                email = json.loads(message_data.decode('utf-8'))
                
                print(f"📧 [{worker_name}] 이메일 발송 중: {email['to']} - {email['subject']}")
                
                # 이메일 발송 시뮬레이션 (처리 시간)
                if is_priority:
                    time.sleep(0.3)  # 우선순위는 빠르게 처리
                else:
                    time.sleep(0.8)  # 일반 이메일은 조금 느리게
                
                print(f"✅ [{worker_name}] 이메일 발송 완료: {email['to']}")
            
            # 큐가 비어있고 더 이상 메시지가 없을 때 종료
            if not result and r.llen(queue_name) == 0:
                print(f"🛑 [{worker_name}] 큐가 비어있어 종료")
                break
                
        except KeyboardInterrupt:
            print(f"🛑 [{worker_name}] 이메일 발송 중단")
            break

def queue_monitor():
    """큐 상태 모니터링"""
    print("📊 큐 상태 모니터링 시작...")
    
    while True:
        try:
            normal_count = r.llen(EMAIL_QUEUE)
            priority_count = r.llen(PRIORITY_QUEUE)
            
            print(f"📊 큐 상태: 일반 이메일 {normal_count}개, 우선순위 이메일 {priority_count}개")
            
            # 모든 큐가 비어있으면 종료
            if normal_count == 0 and priority_count == 0:
                print("📊 모든 큐가 비어있음 - 모니터링 종료")
                break
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("🛑 모니터링 중단")
            break

def demonstrate_fifo():
    """FIFO 동작 시연"""
    print("\n🔄 FIFO (First In, First Out) 동작 시연")
    
    # 테스트 큐 생성
    test_queue = 'test_fifo_queue'
    
    # 순서대로 메시지 추가
    messages = ['첫 번째', '두 번째', '세 번째', '네 번째', '다섯 번째']
    
    print("📝 메시지 추가 순서:")
    for msg in messages:
        r.lpush(test_queue, msg)
        print(f"  → {msg}")
    
    print("\n📖 메시지 읽기 순서 (FIFO):")
    while r.llen(test_queue) > 0:
        result = r.brpop(test_queue, timeout=1)
        if result:
            queue_name, message = result
            print(f"  ← {message.decode('utf-8')}")
    
    print("✅ FIFO 동작 확인 완료")

def demonstrate_lifo():
    """LIFO 동작 시연 (스택)"""
    print("\n🔄 LIFO (Last In, First Out) 동작 시연")
    
    # 테스트 큐 생성
    test_queue = 'test_lifo_queue'
    
    # 순서대로 메시지 추가
    messages = ['첫 번째', '두 번째', '세 번째', '네 번째', '다섯 번째']
    
    print("📝 메시지 추가 순서:")
    for msg in messages:
        r.rpush(test_queue, msg)  # 오른쪽에서 추가
        print(f"  → {msg}")
    
    print("\n📖 메시지 읽기 순서 (LIFO - 스택):")
    while r.llen(test_queue) > 0:
        result = r.brpop(test_queue, timeout=1)  # 오른쪽에서 제거
        if result:
            queue_name, message = result
            print(f"  ← {message.decode('utf-8')}")
    
    print("✅ LIFO 동작 확인 완료")

def main():
    print("📧 Redis Queue 이메일 발송 시스템 시작")
    print("=" * 60)
    
    # FIFO/LIFO 시연
    demonstrate_fifo()
    demonstrate_lifo()
    
    print("\n" + "=" * 60)
    print("📧 실제 이메일 발송 시스템 시작")
    
    # 이메일 생산자 시작
    producer_thread = threading.Thread(target=email_producer)
    producer_thread.start()
    
    # 잠시 대기 후 워커들 시작
    time.sleep(1)
    
    # 이메일 워커들 시작
    workers = [
        # 우선순위 이메일 워커 (빠른 처리)
        threading.Thread(target=email_worker, args=('priority_worker1', PRIORITY_QUEUE, True)),
        threading.Thread(target=email_worker, args=('priority_worker2', PRIORITY_QUEUE, True)),
        
        # 일반 이메일 워커
        threading.Thread(target=email_worker, args=('normal_worker1', EMAIL_QUEUE, False)),
        threading.Thread(target=email_worker, args=('normal_worker2', EMAIL_QUEUE, False)),
        threading.Thread(target=email_worker, args=('normal_worker3', EMAIL_QUEUE, False))
    ]
    
    for worker in workers:
        worker.start()
    
    # 큐 모니터링 시작
    monitor_thread = threading.Thread(target=queue_monitor)
    monitor_thread.start()
    
    # 생산자 완료 대기
    producer_thread.join()
    
    # 워커들이 메시지를 처리할 시간 대기
    print("\n⏳ 워커들이 이메일 발송 중...")
    time.sleep(3)
    
    # 모니터링 완료 대기
    monitor_thread.join()
    
    print("\n🎉 이메일 발송 시스템 시연 완료!")
    print("\n💡 핵심 포인트:")
    print("1. FIFO (First In, First Out) 순서 보장")
    print("2. 블로킹 방식으로 효율적인 메시지 처리")
    print("3. 우선순위 큐로 중요한 메시지 우선 처리")
    print("4. 여러 워커가 동시에 작업 처리 (분산 처리)")
    print("5. 간단한 구조로 빠른 구현 가능")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 프로그램 종료") 