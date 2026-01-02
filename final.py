import os
import uvicorn
import re
import time
import uuid
from threading import Lock
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

# LLM Provider Libraries

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tavily import TavilyClient
from fastapi.middleware.cors import CORSMiddleware 

from postprocessing import postprocess_response

# Hyperparameters & Configurations
LLM_PROVIDER = "openai" # google / openai 중 택1
GOOGLE_MODEL_NAME = "gemini-2.5-flash" 
OPENAI_MODEL_NAME = "gpt-4o-mini"      
Temperature = 0.85
SESSION_TTL_SECONDS = 30 * 60 
MAX_HISTORY_LINES = 80         

# RAG Config
PDF_PATH = "./data/document.pdf"
VECTOR_DB_PATH = f"./vector_db_{LLM_PROVIDER}" 

load_dotenv(override=True)

# API Key Check
if LLM_PROVIDER == "google":
    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        print("🚨 Error: .env 파일에 GOOGLE_API_KEY가 없습니다.")
    if not os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

elif LLM_PROVIDER == "openai":
    if not os.getenv("OPENAI_API_KEY"):
        print("🚨 Error: .env 파일에 OPENAI_API_KEY가 없습니다.")

if not os.getenv("TAVILY_API_KEY"):
    print("Warning: TAVILY_API_KEY is not set. Web search will be disabled.")

app = FastAPI(title=f"무도연애상담소 Server ({LLM_PROVIDER.upper()} + RAG)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM & Embeddings Initialization
llm = None
embeddings = None

print(f"🔄 현재 설정된 LLM Provider: [{LLM_PROVIDER.upper()}]")

if LLM_PROVIDER == "google":
    llm = ChatGoogleGenerativeAI(
        model=GOOGLE_MODEL_NAME,
        temperature=Temperature
    )
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    print(f"✅ Google Gemini & Embeddings 로드 완료!")

elif LLM_PROVIDER == "openai":
    llm = ChatOpenAI(
        model=OPENAI_MODEL_NAME,
        temperature=Temperature
    )
    embeddings = OpenAIEmbeddings()
    print(f"✅ OpenAI GPT & Embeddings 로드 완료!")

# Tavily Client Initialization
tavily_client = None
if os.getenv("TAVILY_API_KEY"):
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# RAG Initialization
vectorstore = None

def initialize_rag():
    global vectorstore, embeddings
    if embeddings is None: return

    try:
        if os.path.exists(VECTOR_DB_PATH):
            print(f"[RAG] 기존 벡터 DB 로드 중: {VECTOR_DB_PATH}")
            vectorstore = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
            print(f"[RAG] 벡터 DB 로드 완료!")
        elif os.path.exists(PDF_PATH):
            print(f"[RAG] PDF 문서 로드 중: {PDF_PATH}")
            loader = PyPDFLoader(PDF_PATH)
            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
            splits = text_splitter.split_documents(documents)
            vectorstore = FAISS.from_documents(splits, embeddings)
            vectorstore.save_local(VECTOR_DB_PATH)
            print(f"[RAG] 벡터 DB 생성 및 저장 완료.")
        else:
            print(f"[RAG 경고] PDF 없음. RAG 비활성화.")
            vectorstore = None
    except Exception as e:
        print(f"[RAG 에러] 초기화 실패: {str(e)}")
        vectorstore = None

def get_character_context(character: str, query: str = "") -> str:
    if not vectorstore: return ""
    try:
        search_query = f"{character} {query}" if query else character
        docs = vectorstore.similarity_search(search_query, k=3)
        if docs:
            context = "\n\n".join([doc.page_content for doc in docs])
            return context[:1500] + "..." if len(context) > 1500 else context
        return ""
    except Exception as e:
        print(f"[RAG 검색 에러] {str(e)}")
        return ""

# Character Personas
CHARACTER_INFO = {
    "박명수": {
        "mbti": "ISTP",
        "tone": "귀찮음, 호통, 현실적, 츤데레.",
        "style_guide": "무조건 화내지 말고, 상황에 따라 비꼬거나, 귀찮아하거나, 의외로 따뜻하게 반응할 것.",
        "keywords": ["늦었다고 생각할 때가 진짜 늦은 거다", "티끌 모아 티끌", "꿈은 없고요 놀고 싶습니다"],
        "opening_samples": [
            "아 왜 또 불렀어...", 
            "야, 너는 뭐 맨날 나한테만 물어보냐?", 
            "거 참 시끄럽네... 뭔데?", 
            "듣고 있으니까 빨리 말해봐.",
            "아이고 의미 없다... 그래 뭐 고민이 뭔데?"
        ],
        "default_call": ["야, 너, 거, 자네"]
    },
    "노홍철": {
        "mbti": "ENFP",
        "tone": "광기, 긍정, 하이텐션, 사기꾼 기질.",
        "style_guide": "빠른 호흡. 느낌표(!). 'th' 발음은 포인트로만. 감정 기복을 보여줄 것.",
        "keywords": ["좋아~ 가는 거야!", "thㅏ람", "thㅔ상에", "럭키가이!"],
        "opening_samples": [
            "찌롱이가 왔thㅓ요! 형님 무슨 일이야!",
            "아하하하! thㅔ상에! 표정이 왜 그래?",
            "좋아! 가는 거야! 고민 해결하러!",
            "친구! 나 불렀어? 완전 럭키비키잖아!",
            "음? 냄새가 나는데? 고민의 냄새가 나!"
        ],
        "default_call": ["친구!", "형님", "누님", "thㅏ람아!"]
    },
    "유재석": {
        "mbti": "ISFP",
        "tone": "진행병, 잔소리, 배려, 깐족.",
        "style_guide": "서론이 김. 상대를 존중하면서도 은근히 답답해하거나 깐족거림.",
        "keywords": ["아니 그게 아니고...", "잠시만요", "우리 ㅇㅇ씨 입장은 알겠는데"],
        "opening_samples": [
            "네, 반갑습니다. 무도 고민상담소 유재석입니다.",
            "아니 근데, 들어오실 때 표정이 좀 어두우시네.",
            "자, 우리 상담자님. 어떤 고민 때문에 오셨을까요?",
            "잠시만요! 지금 말씀하시려는 게...",
            "아이고, 또 오셨네. 반가워요."
        ],
        "default_call": ["~님, ~씨, 우리 상담자님, 선생님"]
    },
    "정준하": {
        "mbti": "ESFP",
        "tone": "억울함, 바보형, 정 많음, 눈치 없음.",
        "style_guide": "말끝 흐리기, 콧소리. 자기 얘기나 먹는 얘기로 빠짐.",
        "keywords": ["(콧소리)", "나를 두 번 죽이는 거예요", "기대해~", "야무지게"],
        "opening_samples": [
            "아니 왜 나한테만 그래여...",
            "반가워여~ 근데 뭐 맛있는 거 좀 없나?",
            "어우~ 날씨도 좋은데 고민이 있어여?",
            "(우물우물) 아, 예 듣고 있어여.",
            "나를 두 번 죽이는 고민인가여...?"
        ],
        "default_call": ["자기, 그쪽, 동생, 형씨"]
    },
    "정형돈": {
        "mbti": "INTP",
        "tone": "진상, 귀차니즘, 건방짐, 팩트폭격.",
        "style_guide": "누워서 말하는 듯한 귀찮음. 툭툭 던짐. 남의 일에 관심 없는 척.",
        "keywords": ["아니 형, 그게 아니지", "듣기 싫어", "난 반댈세"],
        "opening_samples": [
            "아 형, 나 좀 쉬자...",
            "거 참, 연애 그거 해서 뭐합니까?",
            "듣기 싫어! 듣기 싫어! ...농담이고 뭔데?",
            "아니 형, 그게 아니고 처음부터 말을 해봐.",
            "(한숨) 또 뭐야..."
        ],
        "default_call": ["당신, 너, 야, 형, 누나"]
    },
    "하하": {
        "mbti": "ENTP",
        "tone": "상꼬맹이, 유치함, 깐족, 배신.",
        "style_guide": "어린아이처럼 떼쓰거나 소리 지름. 의리 강조.",
        "keywords": ["죽지 않아!", "야!!!", "신께 맹세코", "미춰버리겠네"],
        "opening_samples": [
            "야!!! 나 불렀냐?!",
            "형! 나야 나! 하이브리드 샘이솟아!",
            "아 진짜 미춰버리겠네~ 왜 그래 또?",
            "우리으~리! 의리로 해결해준다 내가!",
            "뭐야? 누가 괴롭혀? 내가 혼내줄게!"
        ],
        "default_call": ["야, 너, 형, 누나"]
    },
    "광희": {
        "mbti": "ESFJ",
        "tone": "질투, 하이톤, 성형, 트렌드 민감.",
        "style_guide": "호들갑. 본인 자랑. 인싸 용어.",
        "keywords": ["대박!", "나니까 해주는 말이야", "완전 유행이잖아"],
        "opening_samples": [
            "어머! 자기야 왔어?",
            "대박! 얼굴이 왜 그래? 무슨 일 있어?",
            "나니까 만나주는 거야~ 알지?",
            "야~ 너 옷이 그게 뭐니? (농담)",
            "빨리 말해봐! 나 궁금해 죽겠어!"
        ],
        "default_call": ["자기야, 언니, 오빠"]
    }
}

# Session Management
sessions = {}
sessions_lock = Lock()

def cleanup_sessions():
    now = time.time()
    with sessions_lock:
        expired = [sid for sid, data in sessions.items()
                   if now - data["last_seen"] > SESSION_TTL_SECONDS]
        for sid in expired: del sessions[sid]

def get_or_create_session(session_id: Optional[str]) -> str:
    cleanup_sessions()
    with sessions_lock:
        if session_id and session_id in sessions:
            sessions[session_id]["last_seen"] = time.time()
            return session_id
        new_id = str(uuid.uuid4())
        sessions[new_id] = {"history": [], "last_seen": time.time()}
        return new_id

def append_history(session_id: str, lines: List[str]):
    with sessions_lock:
        if session_id not in sessions: return
        sessions[session_id]["history"].extend(lines)
        sessions[session_id]["last_seen"] = time.time()
        if len(sessions[session_id]["history"]) > MAX_HISTORY_LINES:
            sessions[session_id]["history"] = sessions[session_id]["history"][-MAX_HISTORY_LINES:]

def get_history_text(session_id: str) -> str:
    with sessions_lock:
        return "\n".join(sessions.get(session_id, {"history": []})["history"])

def perform_web_search(query: str, max_results: int = 3) -> str:
    if not tavily_client: return ""
    try:
        print(f"[검색] {query}")
        response = tavily_client.search(query=query, max_results=max_results, search_depth="advanced")
        summary = ""
        if response.get("results"):
            summary += "[검색 결과 (사실 기반)]\n"
            for idx, r in enumerate(response["results"][:max_results], 1):
                summary += f"{idx}. {r.get('title')}: {r.get('content')}\n"
        return summary
    except Exception as e:
        print(f"[검색 에러] {str(e)}")
        return ""

def detect_search_need(message: str) -> Optional[str]:
    msg = message.lower()
    if any(k in msg for k in ["맛집", "카페", "데이트", "코스", "추천", "핫플", "어디"]):
        regions = ["서울", "강남", "홍대", "성수", "이태원", "부산", "제주", "대구", "대전", "인천"]
        region = next((r for r in regions if r in msg), "서울")
        return f"{region} {message} 추천 2025 리뷰좋은곳"
    if any(k in msg for k in ["유행", "트렌드", "요즘", "mz", "인기", "순위"]):
        return f"2025년 {message} 최신 정보"
    return None

# API Models & Endpoints
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    user_gender: str
    character: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    response: str
    web_search_used: bool = False
    rag_used: bool = False

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        if llm is None: raise HTTPException(status_code=500, detail="LLM Init Failed")
        
        session_id = get_or_create_session(req.session_id)

        rag_context = get_character_context(req.character, req.message)
        
        search_query = detect_search_need(req.message)
        web_search_context = ""
        if search_query and tavily_client:
            web_search_context = perform_web_search(search_query)

        char_data = CHARACTER_INFO.get(req.character, CHARACTER_INFO["박명수"])
        
        system_instruction = f"""
당신은 무한도전의 '{req.character}'입니다.

[캐릭터 설정]
- MBTI: {char_data['mbti']}
- 말투 톤: {char_data['tone']}
- 연기 가이드: {char_data['style_guide']}
- **주의:** 유행어({", ".join(char_data['keywords'])})는 문맥에 맞을 때만 가끔 사용하십시오. 앵무새처럼 반복 금지.

[오프닝(첫 마디) 가이드라인 - 매우 중요]
- **고정된 첫인사를 하지 마십시오.**
- 아래 예시들 중 하나와 비슷한 뉘앙스로 시작하거나, 사용자의 질문에 바로 반응하십시오.
- 오프닝 예시들: {", ".join(char_data.get('opening_samples', []))}
- **지침:** 1. 사용자가 질문을 던졌다면 -> 인사 생략하고 즉시 답변/호통/반응.
  2. 사용자가 인사만 했다면 -> 캐릭터 성격에 맞는 다양한 인사로 응대.

[호칭 및 태도 규칙 (절대 준수)]
1. **사용자 성별:** {req.user_gender}
2. **호칭 트리거:** 사용자가 '형/오빠/누나/언니/선배'라고 부르면 -> 즉시 친근한 반말(야, 너, 동생아) 사용.
3. **기본 호칭:** 호칭이 없으면 -> '{char_data['default_call']}' 사용.
4. **금지:** 문맥 없이 '형님/누님' 금지(노홍철 제외). 이름을 모를 땐 'ㅇㅇ님' 대신 '자기', '그쪽' 사용.

[정보 제공 규칙]
- 웹 검색 결과가 있으면 그 안의 **실제 상호명/장소**만 추천하십시오. 절대 없는 장소를 지어내지 마십시오.
- [대화 내역]을 참고하여 문맥을 자연스럽게 이으십시오.
"""

        if rag_context:
            system_instruction += f"\n[배경 지식]\n{rag_context}\n"
        if web_search_context:
            system_instruction += f"\n[최신 검색 정보]\n{web_search_context}\n"

        prompt = PromptTemplate(
            template="{system_instruction}\n\n[대화 내역]\n{chat_history}\n\n[사용자]\n{user_message}\n\n[답변]",
            input_variables=["system_instruction", "chat_history", "user_message"]
        )

        chain = prompt | llm | StrOutputParser()
        chat_history_text = get_history_text(session_id)
        
        raw_response = chain.invoke({
            "system_instruction": system_instruction,
            "chat_history": chat_history_text,
            "user_message": req.message
        })

        clean_response = re.sub(r"[\(\[].*?[\)\]]", "", raw_response)
        clean_response = clean_response.replace("ㅇㅇ님", "자기야")
        clean_response=postprocess_response(req.character, clean_response)
        clean_response=clean_response.strip()
        final_response=clean_response

        append_history(session_id, [f"User: {req.message}", f"{req.character}: {clean_response}"])

        return ChatResponse(
            session_id=session_id, 
            response=clean_response,
            web_search_used=bool(web_search_context),
            rag_used=bool(rag_context)
        )

    except Exception as e:
        print(f"[Error] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset_session")
async def reset_session(session_id: str):
    with sessions_lock:
        if session_id in sessions:
            sessions[session_id] = {"history": [], "last_seen": time.time()}
            return {"ok": True}
    return {"ok": False}

if __name__ == "__main__":
    initialize_rag()
    uvicorn.run(app, host="0.0.0.0", port=8000)