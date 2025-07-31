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




--- 
> cf. reference 
- https://jaehyuuk.tistory.com/216
- https://sunro1994.tistory.com/333#Redis%EB%A5%BC%20%ED%99%9C%EC%9A%A9%ED%95%98%EC%97%AC%20%EC%84%B8%EC%85%98%20%EC%A0%80%EC%9E%A5%EC%86%8C%EB%A1%9C%20%EC%82%AC%EC%9A%A9%ED%95%A0%20%EA%B2%BD%EC%9A%B0%EC%9D%98%20%EC%9E%A5%EC%A0%90%EA%B3%BC%20%EB%8B%A8%EC%A0%90%EC%9D%80%20%EB%AC%B4%EC%97%87%EC%9D%B8%EA%B0%80%EC%9A%94%3F-1-33