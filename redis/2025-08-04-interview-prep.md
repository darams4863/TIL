질문:
“Redis가 싱글 스레드 모델임에도 높은 성능을 보장하는 이유가, 단순히 인메모리라서 디스크 I/O가 없기 때문이라는 걸 제외하면 다른 이유가 있을까요?”

답변 예시:
“네, 단순히 메모리 기반이라는 점 외에도 Redis가 높은 성능을 낼 수 있는 몇 가지 중요한 이유가 있습니다.

첫 번째는 싱글 스레드 이벤트 루프 구조입니다.
Redis는 한 번에 하나의 명령만 처리하기 때문에 락(lock) 경합이 전혀 없고, 멀티스레드에서 발생하는 문맥 전환 비용도 발생하지 않습니다. 이 덕분에 CPU 캐시 효율이 높아져 요청을 매우 빠르게 처리할 수 있습니다.

두 번째는 I/O Multiplexing 기법입니다.
Redis는 내부적으로 epoll(리눅스)이나 kqueue(맥) 같은 이벤트 감시 시스템을 사용합니다.
수천, 수만 개의 클라이언트 연결을 동시에 유지하면서도, 읽기·쓰기 준비가 된 소켓만 이벤트 큐로 보내 처리하기 때문에, 싱글 스레드임에도 비효율 없이 네트워크 I/O를 처리할 수 있습니다.

마지막으로 최적화된 자료구조와 명령 설계도 큰 역할을 합니다.
예를 들어 Skip List + Hash Table 기반의 Sorted Set이나, 압축된 RDB/AOF 저장 방식, 메모리 친화적인 내부 구조 덕분에 명령 대부분이 O(1) 또는 O(log n)으로 동작해요.

정리하면,
① 락 경합이 없는 싱글 스레드 이벤트 루프,
② I/O Multiplexing 기반 비동기 네트워크 처리,
③ 메모리 친화적 자료구조
이 세 가지가 결합되어 Redis는 멀티스레드 없이도 초당 수십만 요청을 처리할 수 있습니다.”




===
•	Redis가 싱글 스레드인데 왜 빠른가요?
•	Redis는 CPU를 몇 코어나 활용하나요?
•	Redis에서 다중 연결 처리 방식은 어떻게 동작하나요? (epoll/I/O Multiplexing)
•	Redis가 단일 스레드라면 대규모 트래픽에서 병목은 어디서 생길까요?
•	“실제 프로젝트에서 Redis를 큐로 사용했다고 하셨는데, Pub/Sub 대신 List를 쓴 이유가 뭔가요?”
•	“유실 없는 메시지 처리가 필요했다면 Stream이 더 적합한데, List 사용의 장단점을 설명해 주세요.”
•	“Redis 성능을 최대한 활용하려면 어떤 점을 주의해야 하나요?”
→ 여기서 싱글 스레드 + I/O Multiplexing 이해도가 나오면 플러스 점수
•	epoll이 무엇인지 아시나요?
•	논블로킹 I/O와 싱글 스레드 이벤트 루프의 관계를 설명해보세요.
•	Redis는 CPU 바운드보다는 메모리/네트워크 바운드인데, 이를 모니터링하거나 최적화하려면 어떤 방법이 있나요?
•	Redis 멀티스레드 I/O가 어떤 구조로 동작하는지 아세요?
→ (IO 쓰레드가 accept, read, write만 담당하고, 실제 커맨드는 싱글 스레드 처리)
•	AOF와 RDB를 혼합 모드로 쓸 때 성능/복구 트레이드오프는요?
•	Eviction 정책과 키 만료 전략을 운영에 맞게 조정해본 경험 있나요?
•	Redis를 세션 스토어로 쓸 때 장애 복구 시 유저 로그인이 풀리는 이슈는 어떻게 대비하나요?

1.	Redis Cluster에서 Hash Slot 16384개인 이유?
→ 이거 답변 못하면 바로 초보 티남
2.	TTL 수백만 개 걸린 상태에서 latency 튀는 원인?
→ Active Expiration, Fork Copy-on-write, Memory Fragmentation까지 설명해야 함
3.	Redlock의 단점?
→ GC pause, network partition, clock drift까지 알아야 함


이벤트 루프, Fork latency, TTL storm, replication delay, cluster failover, eviction, RDB fork spike
-> 트레이드 오프와 해결 방향 ? 

- 다양한 자료구조를 실무에서 어떻게 활용해봤나요?
→ 예: Sorted Set으로 랭킹 구현, Stream으로 작업 큐


- Redis를 캐시로 쓸 때 주의할 점은 뭔가요?
→ TTL 관리, Eviction 정책, big/hot key 문제


- epoll이 이벤트 루프에서 동작하는 방식 


# TTL/Expiration/Active-Lazy 차이

# Eviction 정책도 정책 이름과 동작 원리까지 정리 (깊게 안 들어가도 됨)

# 	big key/hot key는 개념만 보고 실습으로 체득




1.	RDB와 AOF의 차이와 장단점은?
2.	RDB + AOF 혼용 모드의 동작 방식을 설명해보세요.
3.	Redis 복제가 비동기라면 어떤 문제가 발생할 수 있나요?
4.	Replica 초기 동기화 과정과 PSYNC의 차이점은?
5.	Sentinel과 Cluster의 차이와 장애 처리 방식은?
6.	Fork 시 발생하는 latency spike는 왜 생기나요?





## 6. 면접 질문 예시

### 6.1 기본 질문
1. **RDB와 AOF의 차이점은?**
2. **Redis 복제에서 데이터 유실이 발생할 수 있는 경우는?**
3. **Sentinel과 Cluster의 차이점은?**

### 6.2 심화 질문
1. **Fork 시 메모리 사용량이 2배가 되는 이유는?**
2. **복제 지연이 발생하는 원인과 해결 방법은?**
3. **Redis Cluster에서 16384개 슬롯인 이유는?**
4. **Sentinel과 Cluster의 차이점과 언제 사용해야 하나?**
5. **클러스터에서 MGET 명령어가 실패하는 이유는?**
6. **해시 태그를 사용하는 이유와 주의사항은?**

### 6.3 실무 질문
1. **대용량 Redis에서 RDB 저장 시 성능 저하를 어떻게 해결하나?**
2. **복제 환경에서 읽기 일관성을 어떻게 보장하나?**
3. **네트워크 파티션 시 데이터 불일치를 어떻게 처리하나?**




Q: "웹소켓 대신 Redis Pub/Sub을 사용하면 좋은 점은?"

A: "웹소켓 대신 Redis Pub/Sub을 사용하면 크게 3가지 장점이 있습니다.

첫째, 서버 부하 분산입니다. 웹소켓은 각 클라이언트마다 개별 연결을 유지해야 하는데, 
클라이언트가 많아지면 서버 메모리 사용량이 급증합니다. 
반면 Redis Pub/Sub은 애플리케이션 서버가 메시지 발행만 담당하고, 
Redis가 브로드캐스트를 처리하므로 서버 부하가 일정합니다.

둘째, 확장성입니다. 웹소켓으로 서버를 2대 운영하면 복잡한 로드밸런싱이 필요하고, 
서버 간 메시지 전달도 별도 구현해야 합니다. 
Redis Pub/Sub은 서버가 추가되어도 Redis가 자동으로 모든 구독자에게 메시지를 전달해주므로 확장이 쉽습니다.

셋째, 개발 복잡도 감소입니다. 웹소켓은 연결 관리, 브로드캐스트 로직, 연결 해제 처리 등 
복잡한 코드가 필요한 반면, Redis Pub/Sub은 단순히 publish 명령어 하나로 모든 구독자에게 메시지를 전달할 수 있습니다.

실제로 제가 작업한 프로젝트에서 실시간 알림 시스템을 구현할 때, 
처음에는 웹소켓으로 했는데 사용자가 늘어나면서 서버 부하가 심해졌습니다. 
Redis Pub/Sub으로 변경하니 서버 부하가 크게 줄어들고, 새로운 알림 타입을 추가할 때도 코드 수정이 최소화되었습니다.

단, Redis Pub/Sub은 단방향 통신에 적합하고, 양방향 실시간 통신이 필요한 경우에는 웹소켓이 더 적합합니다. 
예를 들어 채팅처럼 클라이언트에서 서버로 즉시 응답이 필요한 경우는 웹소켓을 사용하는 것이 좋습니다."

-> 꼬리질문 예상
	•	“그럼 Redis Pub/Sub 대신 Stream을 쓰면 뭐가 다른가요?”
	•	“Redis Pub/Sub 구조에서 서버가 재시작하면 메시지는 어떻게 되나요?”
	•	“WebSocket과 Redis Pub/Sub을 같이 써야 하는 경우는 언제인가요?”
	•	“Kafka 같은 메시지 큐와 비교하면 장단점은 뭐가 있나요?”





🔹 면접 예상 질문

1️⃣ Pub/Sub 관련
	1.	Redis Pub/Sub의 기본 동작 원리를 설명해보세요.
	2.	Pub/Sub의 장점과 단점을 각각 설명해보세요.
	3.	구독자가 오프라인 상태일 때 메시지는 어떻게 되나요?
	4.	Pub/Sub에서 특정 구독자에게만 메시지를 보내려면 어떻게 해야 할까요?
	5.	Pub/Sub의 실무 활용 사례를 말해보세요.

2️⃣ Stream 관련
	1.	Redis Stream의 특징과 Pub/Sub과의 차이점은 무엇인가요?
	2.	Consumer Group의 동작 원리를 설명해보세요.
	3.	Stream에서 메시지 재처리가 필요한 경우 어떻게 대응하나요?
	4.	Pending 상태란 무엇이며 어떻게 관리하나요?
	5.	XADD, XREAD, XACK 명령어 각각의 역할을 설명해보세요.

3️⃣ 종합/응용 질문
	1.	Redis Pub/Sub과 Stream 중 실시간 알림 시스템에 적합한 것은 무엇이며, 그 이유는?
	2.	로그 수집 및 장애 재처리가 필요한 경우 어떤 방식을 선택할까요?
	3.	Kafka 대신 Redis Stream을 사용하는 장단점을 설명해보세요.
	4.	Pub/Sub과 Stream을 하이브리드로 구성해야 한다면 어떤 구조를 설계하겠습니까?
	5.	Stream의 Consumer Group에서 하나의 Consumer가 죽었을 때 메시지는 어떻게 처리되나요?





stream > consumer group 관련 
🔹 면접 답변 포인트
	1.	Consumer Group의 역할
“Stream 메시지를 여러 Consumer가 안전하게 분산 처리할 수 있도록 하는 구조이며, ACK 기반으로 유실 없이 재처리가 가능합니다.”
	2.	Consumer 장애 시 동작
“ACK 안 된 메시지는 Pending 상태로 남고, 다른 Consumer가 XCLAIM으로 가져와 처리합니다.”
	3.	운영 시 주의점
“ACK 관리, XPENDING 확인, XTRIM으로 메모리 관리가 필요합니다.”




레디스 pub/sub vs stream vs queue 관련 면접 질문 
1️⃣ Redis Pub/Sub
	1.	Pub/Sub의 메시지 전달 보장 수준은? (Lv.1)
	2.	구독자가 오프라인일 경우 메시지는 어떻게 되나요? (Lv.1)
	3.	Redis Cluster 환경에서 Pub/Sub을 사용할 때 주의할 점은? (Lv.2)
	4.	Pub/Sub을 이용해 채팅 시스템을 만든다면 어떤 문제가 생길 수 있고, 이를 어떻게 해결할 수 있나요? (Lv.2)
	5.	실시간 알림 시스템에서 Pub/Sub 대신 Kafka를 선택할 이유는 무엇일까요? (Lv.3)
⸻
2️⃣ Redis Stream
	1.	Redis Stream과 Pub/Sub의 가장 큰 차이점은 무엇인가요? (Lv.1)
	2.	Stream에서 Consumer Group이 하는 역할은 무엇인가요? (Lv.1)
	3.	Stream 메시지를 처리 중 Consumer가 죽으면 어떤 일이 발생하나요? (Lv.2)
	4.	Pending Entry List(PEL)가 무엇이고, 장애 복구 시 어떻게 활용할 수 있나요? (Lv.2)
	5.	Stream을 로그 수집 시스템으로 사용할 때 주의할 점은 무엇인가요? (Lv.3)
	6.	Kafka 대신 Redis Stream을 사용할 수 있는 시나리오와 한계는? (Lv.3)
⸻
3️⃣ Redis Queue (List)
	1.	Redis List 기반 Queue를 구현할 때 주의해야 할 점은? (Lv.1)
	2.	BLPOP/BRPOP과 RPOPLPUSH를 활용한 안전한 Queue 처리 방식은 무엇인가요? (Lv.2)
	3.	Consumer가 메시지를 처리하다 죽으면 메시지가 어떻게 되나요? (Lv.2)
	4.	Stream과 Queue의 차이점은 무엇이며, 언제 Queue를 선택하나요? (Lv.1)
⸻
4️⃣ 종합 / 응용 질문
	1.	실시간 채팅, 로그 수집, 결제 처리 각각에 어떤 방식을 쓰겠는지 선택하고 이유를 설명해보세요. (Lv.2)
	2.	Pub/Sub → Queue → Stream으로 발전하는 이유를 설계 관점에서 설명해보세요. (Lv.2)
	3.	Stream에서 ACK 기반 재처리 로직을 구현하지 않으면 어떤 문제가 생길까요? (Lv.2)
	4. 	대규모 트래픽 환경에서 Redis Pub/Sub을 사용하면 병목이 어디서 생길 수 있는지 설명해보세요. (Lv.3)








--- 
<details>
<summary>cf. reference</summary>

- https://jaehyuuk.tistory.com/216
- https://sunro1994.tistory.com/333#Redis%EB%A5%BC%20%ED%99%9C%EC%9A%A9%ED%95%98%EC%97%AC%20%EC%84%B8%EC%85%98%20%EC%A0%80%EC%9E%A5%EC%86%8C%EB%A1%9C%20%EC%82%AC%EC%9A%A9%ED%95%A0%20%EA%B2%BD%EC%9A%B0%EC%9D%98%20%EC%9E%A5%EC%A0%90%EA%B3%BC%20%EB%8B%A8%EC%A0%90%EC%9D%80%20%EB%AC%B4%EC%97%87%EC%9D%B8%EA%B0%80%EC%9A%94%3F-1-33

- [NHN FORWARD 2021](https://www.youtube.com/watch?v=92NizoBL4uA)
</details>