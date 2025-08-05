import redis
import threading
import time

# 구독자 (별도 스레드)
def subscriber():
    r = redis.Redis(host='localhost', port=6379, db=0)
    pubsub = r.pubsub()
    pubsub.subscribe('news:tech')
    
    print("구독자 시작: news:tech 채널을 구독 중...")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            # 바이트를 문자열로 디코드
            data = message['data'].decode('utf-8')
            print(f"수신: {data}")
            break  # 첫 번째 메시지 수신 후 종료

# 발행자
def publisher():
    r = redis.Redis(host='localhost', port=6379, db=0)
    time.sleep(2)  # 구독자가 준비될 때까지 대기
    print("발행자: 메시지 발행 중...")
    r.publish('news:tech', '새로운 AI 기술 발표')
    print("발행자: 메시지 발행 완료")

# 실행
print("Redis Pub/Sub 테스트 시작")
threading.Thread(target=subscriber).start()
publisher()
print("테스트 완료")