import redis
import time

"""
[예시 시나리오]
🗺️ 위치 기반 서비스
    1. 주변 매장 검색
    2. 라이더/기사 배차
    3. 거리 계산
    4. 지리적 범위 검색

특징:
- 좌표 기반 데이터 저장
- 거리 계산 및 범위 검색
- 내부적으로 GeoHash 사용
- 지구 반경 계산 지원
"""

# Redis 연결
r = redis.Redis(host='localhost', port=6379, db=0)

def store_location_example():
    """매장 위치 등록 예제"""
    print("🗺️ 매장 위치 등록 시스템 시연")
    print("-" * 40)
    
    store_locations_key = "store_locations"
    
    # 1. 편의점 위치 등록 (경도, 위도, 매장명)
    stores = [
        (127.0276, 37.5665, "convenience_store_1"),    # 서울 강남
        (127.0244, 37.5663, "convenience_store_2"),    # 서울 강남
        (126.9780, 37.5665, "convenience_store_3"),    # 서울 서초
        (127.0017, 37.5642, "convenience_store_4"),    # 서울 용산
        (127.0150, 37.5510, "convenience_store_5"),    # 서울 마포
        (127.0400, 37.5800, "convenience_store_6"),    # 서울 성동
        (126.9500, 37.5500, "convenience_store_7"),    # 서울 영등포
        (127.0600, 37.5700, "convenience_store_8")     # 서울 광진
    ]
    
    print("🏪 편의점 위치 등록:")
    for longitude, latitude, store_name in stores:
        r.geoadd(store_locations_key, longitude, latitude, store_name)
        print(f"  {store_name}: ({longitude}, {latitude})")
    
    # 2. 등록된 매장 수 확인
    store_count = r.zcard(store_locations_key)
    print(f"\n📊 등록된 매장 수: {store_count}개")

def nearby_search_example():
    """주변 매장 검색 예제"""
    print("\n🔍 주변 매장 검색 시스템 시연")
    print("-" * 40)
    
    store_locations_key = "store_locations"
    
    # 1. 현재 위치에서 2km 내 편의점 검색
    current_lon = 127.0276
    current_lat = 37.5665
    radius = 2  # 2km
    
    print(f"📍 현재 위치: ({current_lon}, {current_lat})")
    print(f"🔍 {radius}km 내 편의점 검색:")
    
    nearby_stores = r.georadius(store_locations_key, current_lon, current_lat, radius, 'km', withdist=True)
    
    for store, distance in nearby_stores:
        store_name = store.decode('utf-8')
        print(f"  {store_name}: {distance:.2f}km")
    
    # 2. 1km 내 편의점 검색 (더 가까운 범위)
    print(f"\n🔍 1km 내 편의점 검색:")
    nearby_stores_1km = r.georadius(store_locations_key, current_lon, current_lat, 1, 'km', withdist=True)
    
    for store, distance in nearby_stores_1km:
        store_name = store.decode('utf-8')
        print(f"  {store_name}: {distance:.2f}km")

def distance_calculation_example():
    """거리 계산 예제"""
    print("\n📏 거리 계산 시스템 시연")
    print("-" * 40)
    
    store_locations_key = "store_locations"
    
    # 1. 두 매장 간의 거리 계산
    store1 = "convenience_store_1"
    store2 = "convenience_store_2"
    
    distance_km = r.geodist(store_locations_key, store1, store2, 'km')
    distance_m = r.geodist(store_locations_key, store1, store2, 'm')
    
    print(f"📏 {store1} ↔ {store2} 거리:")
    print(f"  {distance_km:.3f} km")
    print(f"  {distance_m:.1f} m")
    
    # 2. 여러 매장 간의 거리 계산
    stores = ["convenience_store_1", "convenience_store_3", "convenience_store_5"]
    
    print(f"\n📏 매장 간 거리 매트릭스:")
    for i, store_a in enumerate(stores):
        for j, store_b in enumerate(stores):
            if i < j:  # 중복 계산 방지
                distance = r.geodist(store_locations_key, store_a, store_b, 'km')
                print(f"  {store_a} ↔ {store_b}: {distance:.3f} km")

def position_lookup_example():
    """좌표 조회 예제"""
    print("\n📍 좌표 조회 시스템 시연")
    print("-" * 40)
    
    store_locations_key = "store_locations"
    
    # 1. 특정 매장의 좌표 조회
    store_name = "convenience_store_1"
    position = r.geopos(store_locations_key, store_name)
    
    if position and position[0]:
        lon, lat = position[0]
        print(f"📍 {store_name} 좌표:")
        print(f"  경도: {lon}")
        print(f"  위도: {lat}")
    
    # 2. 여러 매장의 좌표 조회
    stores = ["convenience_store_1", "convenience_store_2", "convenience_store_3"]
    positions = r.geopos(store_locations_key, *stores)
    
    print(f"\n📍 여러 매장 좌표:")
    for store, pos in zip(stores, positions):
        if pos:
            lon, lat = pos
            print(f"  {store}: ({lon}, {lat})")
        else:
            print(f"  {store}: 좌표 없음")

def delivery_rider_example():
    """배달 라이더 배차 예제"""
    print("\n🚚 배달 라이더 배차 시스템 시연")
    print("-" * 40)
    
    available_riders_key = "available_riders"
    
    # 1. 가용 라이더 위치 등록
    riders = [
        (127.0276, 37.5665, "rider_001"),
        (127.0244, 37.5663, "rider_002"),
        (126.9780, 37.5665, "rider_003"),
        (127.0017, 37.5642, "rider_004"),
        (127.0150, 37.5510, "rider_005")
    ]
    
    print("🚚 가용 라이더 위치 등록:")
    for longitude, latitude, rider_id in riders:
        r.geoadd(available_riders_key, longitude, latitude, rider_id)
        print(f"  {rider_id}: ({longitude}, {latitude})")
    
    # 2. 고객 위치에서 500m 내 라이더 검색
    customer_lon = 127.0276
    customer_lat = 37.5665
    search_radius = 0.5  # 500m
    
    print(f"\n👤 고객 위치: ({customer_lon}, {customer_lat})")
    print(f"🔍 {search_radius}km 내 라이더 검색:")
    
    nearby_riders = r.georadius(available_riders_key, customer_lon, customer_lat, search_radius, 'km', withdist=True)
    
    if nearby_riders:
        for rider, distance in nearby_riders:
            rider_id = rider.decode('utf-8')
            distance_m = distance * 1000  # km를 m로 변환
            print(f"  {rider_id}: {distance_m:.0f}m")
    else:
        print("  근처에 가용 라이더가 없습니다.")

def geographic_range_example():
    """지리적 범위 검색 예제"""
    print("\n🗺️ 지리적 범위 검색 시스템 시연")
    print("-" * 40)
    
    store_locations_key = "store_locations"
    
    # 1. 사각형 영역 검색 (경도, 위도 범위)
    min_lon = 127.0000
    max_lon = 127.0300
    min_lat = 37.5600
    max_lat = 37.5700
    
    print(f"🗺️ 사각형 영역 검색:")
    print(f"  경도: {min_lon} ~ {max_lon}")
    print(f"  위도: {min_lat} ~ {max_lat}")
    
    # GEOSEARCH 명령어 사용 (Redis 6.2+)
    try:
        stores_in_box = r.geosearch(store_locations_key, longitude=127.0150, latitude=37.5650, 
                                   width=0.03, height=0.01, unit='km')
        
        print(f"\n📦 영역 내 매장:")
        for store in stores_in_box:
            store_name = store.decode('utf-8')
            print(f"  {store_name}")
    except:
        # 구버전 Redis를 위한 대안
        print("  (GEOSEARCH 명령어를 지원하지 않는 Redis 버전입니다)")

def geohash_example():
    """GeoHash 예제"""
    print("\n🔢 GeoHash 시스템 시연")
    print("-" * 40)
    
    store_locations_key = "store_locations"
    
    # 1. 특정 매장의 GeoHash 조회
    store_name = "convenience_store_1"
    geohash = r.geohash(store_locations_key, store_name)
    
    if geohash and geohash[0]:
        hash_value = geohash[0].decode('utf-8')
        print(f"🔢 {store_name}의 GeoHash:")
        print(f"  {hash_value}")
    
    # 2. 여러 매장의 GeoHash 조회
    stores = ["convenience_store_1", "convenience_store_2", "convenience_store_3"]
    geohashes = r.geohash(store_locations_key, *stores)
    
    print(f"\n🔢 여러 매장의 GeoHash:")
    for store, hash_val in zip(stores, geohashes):
        if hash_val:
            hash_str = hash_val.decode('utf-8')
            print(f"  {store}: {hash_str}")
        else:
            print(f"  {store}: GeoHash 없음")

def main():
    print("🗺️ Redis Geospatial 자료구조 실습")
    print("=" * 60)
    
    # 각 예제 실행
    store_location_example()
    nearby_search_example()
    distance_calculation_example()
    position_lookup_example()
    delivery_rider_example()
    geographic_range_example()
    geohash_example()
    
    print("\n" + "=" * 60)
    print("🎉 Geospatial 실습 완료!")
    print("\n💡 핵심 포인트:")
    print("1. 좌표 기반 데이터 저장 및 검색")
    print("2. 거리 계산 및 범위 검색")
    print("3. 내부적으로 GeoHash 사용")
    print("4. 위치 기반 서비스 구현에 최적")
    print("5. 지구 반경 계산 지원")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 프로그램 종료")
    except redis.ConnectionError:
        print("❌ Redis 연결 실패. Redis 서버가 실행 중인지 확인하세요.") 