# 무도연애상담소 (Infinite Challenge Dating Coach)

무한도전 멤버들의 페르소나를 재현한 AI 연애 상담 챗봇입니다. RAG와 Web Search 기능을 통해 현실적이고 최신 트렌드에 맞는 조언을 제공합니다.

## 주요 기능

- **멀티 페르소나**: 박명수(현실 호통), 노홍철(긍정 광기), 유재석(배려 잔소리) 등 7명의 캐릭터 완벽 구현
- **RAG 기반 상담**: `document.pdf` (연애 매뉴얼/캐릭터 분석) 문서를 참조하여 깊이 있는 조언 제공
- **실시간 웹 검색**: Tavily API를 연동하여 2025년 최신 데이트 코스, 맛집, 트렌드 정보 제공
- **강력한 후처리**: AI의 기계적인 말투를 제거하고 캐릭터 특유의 말투(유행어, 호칭 등)를 강제 적용
- **문맥 유지**: 세션 ID를 통해 이전 대화 내용을 기억하고 연속적인 상담 가능

## 기술 스택

### Language & Framework
- Python 3.12.8
- FastAPI + Uvicorn

### AI & Data
- LangChain (OpenAI / Google Gemini)
- FAISS (Local Vector DB)
- Tavily Search API (Web Search)
- OpenAI / Google Embeddings

## 프로젝트 구조

```text
Mudo-Love-Coach/
├── data/
│   └── document.pdf         # RAG용 지식 문서 (필수)
├── vector_db_google/        # 생성된 벡터 인덱스 (Google용)
├── vector_db_openai/        # 생성된 벡터 인덱스 (OpenAI용)
│
├── final.py                 # 메인 API 서버 (FastAPI)
├── postprocessing.py        # 말투 교정 및 후처리 모듈
├── client.py                # 터미널용 테스트 클라이언트
├── test_rag.py              # 기능별 시나리오 테스트 스크립트
├── requirements.txt         # 의존성 목록
└── README.md                # 프로젝트 설명서
```

## 설치 및 실행
### 1. 환경 설정
```bash

# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정 (.env)
프로젝트 루트 경로에 .env 파일을 생성하고 아래 키를 입력하세요.
```bash
# [선택 1] Google Gemini 사용 시
GOOGLE_API_KEY=your_google_api_key_here

# [선택 2] OpenAI GPT 사용 시
OPENAI_API_KEY=sk-your_openai_api_key_here

# [필수] 웹 검색 기능 사용 시
TAVILY_API_KEY=tvly-your_tavily_api_key_here
```

### 3. 서버 실행
서버 시작 시 data/document.pdf가 존재하면 자동으로 벡터 DB를 생성합니다.
```bash
python final.py
```
- 서버 주소: http://localhost:8000
- Swagger API 문서: http://localhost:8000/docs

### 4. 테스트 실행
별도의 터미널을 열어 클라이언트를 실행합니다.
```bash
# 대화형 채팅 클라이언트
python client.py

# 기능별 자동 테스트 시나리오
python test_rag.py
```


## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/` | 서버 상태 및 버전 확인 |	
| POST | `/chat` | 캐릭터와 대화 (세션, RAG, 검색 포함) |
| POST | `/reset_session` | 특정 세션의 대화 내역 초기화 |


### /chat 요청 예시

```json
{
  "session_id": "optional-uuid",
  "user_gender": "남성",
  "character": "박명수",
  "message": "형님, 여자친구랑 싸웠는데 화해할 방법 좀 알려주세요."
}
```

### /chat 응답 예시

```json
{
  "session_id": "generated-uuid",
  "response": "야! 니가 잘못했네! 무조건 빌어! ...농담이고, 맛있는 거 사가서 진심으로 사과해.",
  "web_search_used": false,
  "rag_used": true
}
```

## 캐릭터 설정 (Character Info)
final.py 내부에서 캐릭터별 설정을 수정할 수 있습니다.

- 박명수: 현실적, 호통, 츤데레, "늦었다고 생각할 때가 진짜 늦은 거다"

- 노홍철: 긍정 과잉, 광기, 'th' 발음, "좋아~ 가는 거야!"

- 유재석: 배려, 진행병, 잔소리, "아니 그게 아니고..."

- 정준하, 정형돈, 하하, 광희: 각 멤버별 고유 페르소나 적용

