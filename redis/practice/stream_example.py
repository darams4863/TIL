import redis
import threading
import time
import json
from datetime import datetime

""" 
[예시 시나리오]
🏬 온라인 쇼핑몰
	1.	유저가 상품을 주문함 (이벤트 발생)
	2.	이벤트 스트리밍 시스템이 이벤트를 기록하면서 흘려보냄
	3.	다양한 Consumer가 같은 이벤트를 다르게 활용
	•	주문 처리 시스템 → 결제/배송 처리
	•	추천 시스템 → 유저 행동 기반 추천 업데이트
	•	통계/데이터 분석 → 일 매출 집계
	•	알람/푸시 → “주문 완료” 메시지 전송

이때 이벤트 스트림을 로그처럼 기록해두면,
나중에 새로운 시스템(예: AI 분석)이 붙어도 과거 주문 기록부터 재처리 가능.
""" 

# Redis 연결
r = redis.Redis(host='localhost', port=6379, db=0)

# 이벤트 스트림 이름
STREAM_NAME = 'order:events'

def create_consumer_group():
    """Consumer Group 생성"""
    try:
        r.xgroup_create(STREAM_NAME, 'order_processors', id='0', mkstream=True)
        print("✅ Consumer Group 'order_processors' 생성 완료")
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            print("ℹ️ Consumer Group 'order_processors' 이미 존재")
        else:
            print(f"❌ Consumer Group 생성 실패: {e}")

def order_producer():
    """주문 이벤트 생산자 (사용자가 주문하는 시뮬레이션)"""
    print("🛒 주문 이벤트 생산자 시작...")
    
    orders = [
        {
            'user_id': 1001,
            'product_id': 'P001',
            'quantity': 2,
            'total_amount': 50000,
            'timestamp': datetime.now().isoformat()
        },
        {
            'user_id': 1002,
            'product_id': 'P002',
            'quantity': 1,
            'total_amount': 30000,
            'timestamp': datetime.now().isoformat()
        },
        {
            'user_id': 1003,
            'product_id': 'P003',
            'quantity': 3,
            'total_amount': 75000,
            'timestamp': datetime.now().isoformat()
        }
    ]
    
    for i, order in enumerate(orders, 1):
        # 주문 이벤트를 스트림에 추가
        event_data = {
            'event_type': 'order_created',
            'order_data': json.dumps(order),
            'order_id': f'ORDER_{i:03d}'
        }
        
        msg_id = r.xadd(STREAM_NAME, event_data)
        print(f"📦 주문 이벤트 발행: {msg_id} - {order['user_id']}번 고객이 {order['product_id']} 주문")
        time.sleep(1)  # 1초 간격으로 주문
    
    print("✅ 모든 주문 이벤트 발행 완료")

def payment_processor(consumer_name):
    """결제/배송 처리 Consumer"""
    print(f"💳 결제/배송 처리 Consumer ({consumer_name}) 시작...")
    
    while True:
        try:
            # Consumer Group에서 메시지 읽기
            messages = r.xreadgroup(
                'order_processors', consumer_name,
                {STREAM_NAME: '>'}, count=1, block=1000
            )
            
            if messages:
                for stream, msgs in messages:
                    for msg_id, data in msgs:
                        order_data = json.loads(data[b'order_data'])
                        print(f"💳 [{consumer_name}] 결제 처리 중: {data[b'order_id'].decode()} - {order_data['total_amount']}원")
                        
                        # 결제 처리 시뮬레이션
                        time.sleep(0.5)
                        
                        # ACK 전송 (처리 완료)
                        r.xack(STREAM_NAME, 'order_processors', msg_id)
                        print(f"✅ [{consumer_name}] 결제 완료: {data[b'order_id'].decode()}")
            
        except KeyboardInterrupt:
            print(f"🛑 [{consumer_name}] 결제 처리 중단")
            break

def recommendation_processor(consumer_name):
    """추천 시스템 Consumer"""
    print(f"🎯 추천 시스템 Consumer ({consumer_name}) 시작...")
    
    while True:
        try:
            messages = r.xreadgroup(
                'order_processors', consumer_name,
                {STREAM_NAME: '>'}, count=1, block=1000
            )
            
            if messages:
                for stream, msgs in messages:
                    for msg_id, data in msgs:
                        order_data = json.loads(data[b'order_data'])
                        print(f"🎯 [{consumer_name}] 추천 업데이트: {order_data['user_id']}번 고객의 {order_data['product_id']} 구매 패턴 분석")
                        
                        # 추천 시스템 업데이트 시뮬레이션
                        time.sleep(0.3)
                        
                        r.xack(STREAM_NAME, 'order_processors', msg_id)
                        print(f"✅ [{consumer_name}] 추천 업데이트 완료")
            
        except KeyboardInterrupt:
            print(f"🛑 [{consumer_name}] 추천 처리 중단")
            break

def analytics_processor(consumer_name):
    """통계/데이터 분석 Consumer"""
    print(f"📊 통계 분석 Consumer ({consumer_name}) 시작...")
    
    while True:
        try:
            messages = r.xreadgroup(
                'order_processors', consumer_name,
                {STREAM_NAME: '>'}, count=1, block=1000
            )
            
            if messages:
                for stream, msgs in messages:
                    for msg_id, data in msgs:
                        order_data = json.loads(data[b'order_data'])
                        print(f"📊 [{consumer_name}] 매출 집계: {order_data['total_amount']}원 추가 - 일일 매출 업데이트")
                        
                        # 통계 집계 시뮬레이션
                        time.sleep(0.2)
                        
                        r.xack(STREAM_NAME, 'order_processors', msg_id)
                        print(f"✅ [{consumer_name}] 통계 업데이트 완료")
            
        except KeyboardInterrupt:
            print(f"🛑 [{consumer_name}] 통계 처리 중단")
            break

def notification_processor(consumer_name):
    """알림/푸시 Consumer"""
    print(f"🔔 알림 Consumer ({consumer_name}) 시작...")
    
    while True:
        try:
            messages = r.xreadgroup(
                'order_processors', consumer_name,
                {STREAM_NAME: '>'}, count=1, block=1000
            )
            
            if messages:
                for stream, msgs in messages:
                    for msg_id, data in msgs:
                        order_data = json.loads(data[b'order_data'])
                        print(f"🔔 [{consumer_name}] 알림 발송: {order_data['user_id']}번 고객에게 '주문 완료' 메시지 전송")
                        
                        # 알림 발송 시뮬레이션
                        time.sleep(0.4)
                        
                        r.xack(STREAM_NAME, 'order_processors', msg_id)
                        print(f"✅ [{consumer_name}] 알림 발송 완료")
            
        except KeyboardInterrupt:
            print(f"🛑 [{consumer_name}] 알림 처리 중단")
            break

def replay_events():
    """과거 이벤트 재처리 (새로운 시스템이 추가된 시나리오)"""
    print("\n🔄 새로운 AI 분석 시스템이 과거 이벤트 재처리 중...")
    
    # 스트림의 모든 메시지 읽기 (ID 0부터)
    messages = r.xread({STREAM_NAME: '0'}, count=10)
    
    if messages:
        for stream, msgs in messages:
            print(f"📚 총 {len(msgs)}개의 과거 이벤트 발견")
            
            for msg_id, data in msgs:
                order_data = json.loads(data[b'order_data'])
                print(f"🤖 AI 분석: {order_data['user_id']}번 고객의 {order_data['product_id']} 구매 패턴을 AI 모델에 학습")
                time.sleep(0.1)
            
            print("✅ AI 분석 시스템이 과거 이벤트 학습 완료")

def main():
    print("🏬 온라인 쇼핑몰 이벤트 스트리밍 시스템 시작")
    print("=" * 60)
    
    # Consumer Group 생성
    create_consumer_group()
    
    # 주문 이벤트 생산자 시작
    producer_thread = threading.Thread(target=order_producer)
    producer_thread.start()
    
    # 잠시 대기 후 Consumer들 시작
    time.sleep(2)
    
    # 다양한 Consumer들 시작
    consumers = [
        threading.Thread(target=payment_processor, args=('payment_worker1',)),
        threading.Thread(target=recommendation_processor, args=('recommendation_worker1',)),
        threading.Thread(target=analytics_processor, args=('analytics_worker1',)),
        threading.Thread(target=notification_processor, args=('notification_worker1',))
    ]
    
    for consumer in consumers:
        consumer.start()
    
    # 생산자 완료 대기
    producer_thread.join()
    
    # Consumer들이 메시지를 처리할 시간 대기
    print("\n⏳ Consumer들이 메시지 처리 중...")
    time.sleep(5)
    
    # 과거 이벤트 재처리 시연
    replay_events()
    
    print("\n🎉 이벤트 스트리밍 시스템 시연 완료!")
    print("\n💡 핵심 포인트:")
    print("1. 하나의 주문 이벤트가 여러 Consumer에게 분산 처리됨")
    print("2. 각 Consumer는 독립적으로 메시지를 처리하고 ACK를 보냄")
    print("3. 과거 이벤트를 ID 기반으로 재처리 가능")
    print("4. 새로운 시스템(AI 분석)이 추가되어도 과거 데이터 활용 가능")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 프로그램 종료") 