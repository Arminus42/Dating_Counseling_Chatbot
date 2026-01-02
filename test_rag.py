"""
무도연애상담소 종합 테스트
- 다양한 질문 시나리오
- 멀티턴 대화 테스트
- RAG 사용 확인
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def print_separator(title):
    """구분선 출력"""   
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_response(character, message, response_data):
    """응답 깔끔하게 출력"""
    print(f"\n👤 사용자: {message}")
    print(f"💬 {character}: {response_data['response']}")
    print(f"\n📊 상태: 웹검색={response_data['web_search_used']} | RAG={response_data['rag_used']}")


def test_simple_greeting():
    """테스트 1: 간단한 인사 (RAG 사용 확인)"""
    print_separator("테스트 1: 간단한 인사")
    
    payload = {
        "user_gender": "남성",
        "character": "박명수",
        "message": "형님 안녕하세요"
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=20)
    if response.status_code == 200:
        result = response.json()
        print_response("박명수", payload['message'], result)
        return result['session_id']
    else:
        print(f"❌ 에러: {response.status_code}")
        return None


def test_love_advice():
    """테스트 2: 연애 고민 상담 (RAG로 캐릭터 말투 확인)"""
    print_separator("테스트 2: 연애 고민 상담")
    
    scenarios = [
        ("박명수", "형님, 썸녀가 연락을 안 받아요. 어떻게 해야 할까요?"),
        ("노홍철", "형님! 짝사랑 중인데 고백해야 할까요?"),
        ("유재석", "재석이 형, 여자친구랑 싸웠는데 화해하고 싶어요"),
        ("정준하", "준하 형, 데이트 중에 실수했어요. 어떡하죠?"),
        ("정형돈", "형돈이 형, 연애하기 귀찮은데 해야 하나요?"),
        ("하하", "하하 형! 친구가 내 짝사랑 고백했대요!"),
        ("광희", "광희야, 첫 만남에서 좋은 인상 주는 법 알려줘"),
    ]
    
    for character, message in scenarios:
        payload = {
            "user_gender": "남성",
            "character": character,
            "message": message
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=20)
        if response.status_code == 200:
            result = response.json()
            print_response(character, message, result)
            time.sleep(0.5)


def test_date_course():
    """테스트 3: 데이트 코스 추천 (웹 검색 + RAG)"""
    print_separator("테스트 3: 데이트 코스 추천 (웹 검색 자동)")
    
    scenarios = [
        ("노홍철", "형님! 강남에서 데이트하기 좋은 곳 알려주세요!"),
        ("유재석", "성수동 카페 추천 좀 해주세요"),
        ("정준하", "홍대 근처 맛집 어디 가면 좋을까요?"),
    ]
    
    for character, message in scenarios:
        payload = {
            "user_gender": "남성",
            "character": character,
            "message": message
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print_response(character, message, result)
            time.sleep(0.5)


def test_trend_search():
    """테스트 4: 트렌드 검색 (웹 검색 + RAG)"""
    print_separator("테스트 4: 연애 트렌드 (웹 검색 자동)")
    
    scenarios = [
        ("박명수", "요즘 MZ세대는 어떻게 연애해?"),
        ("하하", "2025년 유행하는 데이트 방법 알려줘!"),
    ]
    
    for character, message in scenarios:
        payload = {
            "user_gender": "남성",
            "character": character,
            "message": message
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print_response(character, message, result)
            time.sleep(0.5)


def test_multiturn_conversation():
    """테스트 5: 멀티턴 대화 (세션 유지 + RAG)"""
    print_separator("테스트 5: 멀티턴 대화 - 박명수와 3턴")
    
    conversation = [
        "형님, 썸녀가 있는데 고백할까 말까 고민이에요",
        "근데 거절당하면 어떡하죠? 무서워요",
        "알겠어요 형님! 용기내서 고백해볼게요!"
    ]
    
    session_id = None
    
    for turn, message in enumerate(conversation, 1):
        print(f"\n--- 턴 {turn} ---")
        
        payload = {
            "session_id": session_id,
            "user_gender": "남성",
            "character": "박명수",
            "message": message
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=20)
        if response.status_code == 200:
            result = response.json()
            session_id = result['session_id']  # 세션 유지
            print_response("박명수", message, result)
            time.sleep(1)
        else:
            print(f"❌ 에러: {response.status_code}")
            break


def test_multiturn_nohoengchul():
    """테스트 6: 멀티턴 대화 - 노홍철과 4턴"""
    print_separator("테스트 6: 멀티턴 대화 - 노홍철과 4턴")
    
    conversation = [
        "형님! 데이트 코스 추천 좀 해주세요!",
        "강남이요! 강남에서 데이트할 거예요!",
        "분위기 좋은 곳이 좋아요!",
        "완전 감사합니다 형님!"
    ]
    
    session_id = None
    
    for turn, message in enumerate(conversation, 1):
        print(f"\n--- 턴 {turn} ---")
        
        payload = {
            "session_id": session_id,
            "user_gender": "남성",
            "character": "노홍철",
            "message": message
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            session_id = result['session_id']
            print_response("노홍철", message, result)
            time.sleep(1)


def test_multiturn_yoojaeseok():
    """테스트 7: 멀티턴 대화 - 유재석과 5턴 (길게)"""
    print_separator("테스트 7: 멀티턴 대화 - 유재석과 5턴")
    
    conversation = [
        "재석이 형, 여자친구랑 싸웠어요",
        "제가 약속 시간에 늦었거든요...",
        "30분 정도요. 그리고 연락도 안 했어요",
        "어떻게 사과해야 할까요?",
        "감사합니다 형님! 바로 연락해볼게요!"
    ]
    
    session_id = None
    
    for turn, message in enumerate(conversation, 1):
        print(f"\n--- 턴 {turn} ---")
        
        payload = {
            "session_id": session_id,
            "user_gender": "남성",
            "character": "유재석",
            "message": message
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=20)
        if response.status_code == 200:
            result = response.json()
            session_id = result['session_id']
            print_response("유재석", message, result)
            time.sleep(1)


def test_character_switching():
    """테스트 8: 캐릭터 변경 (같은 세션)"""
    print_separator("테스트 8: 캐릭터 변경 테스트")
    
    message = "연애 고민이 있어요"
    characters = ["박명수", "노홍철", "하하"]
    
    session_id = None
    
    for character in characters:
        payload = {
            "session_id": session_id,
            "user_gender": "남성",
            "character": character,
            "message": message
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=20)
        if response.status_code == 200:
            result = response.json()
            session_id = result['session_id']
            print_response(character, message, result)
            time.sleep(0.5)


def test_god_character():
    """테스트 9: 연애의 신 (RAG 미사용 확인)"""
    print_separator("테스트 9: 연애의 신 (RAG 미사용 확인)")
    
    payload = {
        "user_gender": "남성",
        "character": "연애의 신",
        "message": "신이시여, 짝사랑에서 벗어나고 싶습니다"
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=20)
    if response.status_code == 200:
        result = response.json()
        print_response("연애의 신", payload['message'], result)
        
        if not result['rag_used']:
            print("\n✅ 정상! 연애의 신은 RAG를 사용하지 않습니다.")
        else:
            print("\n⚠️ 버그! 연애의 신도 RAG를 사용했습니다.")


def test_rag_usage_summary():
    """테스트 10: RAG 사용 통계"""
    print_separator("테스트 10: RAG 사용 통계")
    
    characters = ["박명수", "노홍철", "유재석", "정준하", "정형돈", "하하", "광희", "연애의 신"]
    message = "안녕하세요"
    
    rag_stats = {"사용": 0, "미사용": 0}
    
    print("\n캐릭터별 RAG 사용 여부:\n")
    
    for character in characters:
        payload = {
            "user_gender": "남성",
            "character": character,
            "message": message
        }
        
        try:
            response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=15)
            if response.status_code == 200:
                result = response.json()
                rag_status = "✅ RAG 사용" if result['rag_used'] else "❌ RAG 미사용"
                print(f"  {character:10} : {rag_status}")
                
                if result['rag_used']:
                    rag_stats["사용"] += 1
                else:
                    rag_stats["미사용"] += 1
            else:
                print(f"  {character:10} : ⚠️ 에러")
        except Exception as e:
            print(f"  {character:10} : ⚠️ 에러")
    
    print(f"\n📊 통계:")
    print(f"  RAG 사용: {rag_stats['사용']}명")
    print(f"  RAG 미사용: {rag_stats['미사용']}명")
    
    if rag_stats["미사용"] == 1:  # 연애의 신만
        print("\n✅ 정상! 무도 멤버만 RAG 사용, 연애의 신은 미사용")
    else:
        print("\n⚠️ 확인 필요: RAG 설정을 다시 확인하세요")


def check_server():
    """서버 상태 확인"""
    print_separator("서버 상태 확인")
    
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print(f"✅ 서버 정상 작동")
            print(f"메시지: {response.json()['message']}")
            print("\n💡 서버 로그를 확인하세요:")
            print("   [RAG] 벡터 DB 로드 완료! ← 이 메시지가 있어야 합니다")
        else:
            print(f"⚠️ 서버 응답 이상: {response.status_code}")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {str(e)}")
        print("서버를 먼저 실행하세요: python redemption_rag.py")


if __name__ == "__main__":
    print("\n" + "🎬" * 35)
    print("   무도연애상담소 종합 테스트")
    print("   (다양한 질문 + 멀티턴 대화 + RAG 확인)")
    print("🎬" * 35)
    
    check_server()
    
    print("\n⏳ 테스트 시작... (약 2-3분 소요)\n")
    
    # 순차 실행
    test_simple_greeting()
    time.sleep(1)
    
    test_love_advice()
    time.sleep(1)
    
    test_date_course()
    time.sleep(1)
    
    test_trend_search()
    time.sleep(1)
    
    test_multiturn_conversation()
    time.sleep(1)
    
    test_multiturn_nohoengchul()
    time.sleep(1)
    
    test_multiturn_yoojaeseok()
    time.sleep(1)
    
    test_character_switching()
    time.sleep(1)
    
    test_god_character()
    time.sleep(1)
    
    test_rag_usage_summary()
    
    print("\n" + "=" * 70)
    print("✅ 모든 테스트 완료!")
    print("=" * 70)
    print("\n📊 확인사항:")
    print("1. RAG 사용 = True (무도 멤버)")
    print("2. RAG 사용 = False (연애의 신)")
    print("3. 웹 검색 = True (데이트 코스, 트렌드 질문)")
    print("4. 멀티턴 대화 시 문맥 이어짐 확인")
    print("\n💡 서버 로그에서 [RAG], [웹 검색] 메시지를 확인하세요!")