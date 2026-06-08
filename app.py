import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import streamlit as st
from pathlib import Path
from dotenv import dotenv_values
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# 1. 페이지 초기 설정 및 테마 로드 (Premium UI CSS 주입)
st.set_page_config(
    page_title="상임법 RAG 챗봇",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS 주입
st.markdown("""
<style>
    /* Google Font Outfit */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Noto+Sans+KR:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', 'Outfit', sans-serif;
    }
    
    /* Main Background & Glassmorphism Sidebar */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    [data-testid="stSidebar"] {
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Header Styles */
    h1 {
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    
    /* Chat Bubble Custom Styling */
    .stChatMessage {
        border-radius: 16px !important;
        padding: 1rem !important;
        margin-bottom: 0.8rem !important;
        border: 1px solid rgba(255, 255, 255, 0.05);
        color: #ffffff !important;
    }
    
    .stChatMessage p, .stChatMessage span, .stChatMessage div, .stChatMessage li {
        color: #ffffff !important;
    }
    
    /* User Chat Bubble */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: rgba(56, 189, 248, 0.1) !important;
        border-left: 4px solid #38bdf8 !important;
    }
    
    /* Assistant Chat Bubble */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: rgba(30, 41, 59, 0.6) !important;
        border-left: 4px solid #818cf8 !important;
    }
    
    /* Hover Effects for interactive elements */
    .stButton>button {
        background: linear-gradient(90deg, #0284c7 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3) !important;
    }
    
    /* Source box styling */
    .source-box {
        background-color: rgba(15, 23, 42, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.8rem;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    
    /* Smooth Scroll */
    html {
        scroll-behavior: smooth;
    }
</style>
""", unsafe_allow_html=True)

# 2. API 키 로드
BASE_DIR = Path(__file__).resolve().parent

# 1) OS 환경변수 또는 Streamlit Secrets에서 우선 탐색 (배포 환경용)
api_key = os.environ.get("GEMINI_API_KEY")

# st.secrets 지원 여부 확인 후 로드
if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass

# 2) 찾지 못한 경우 로컬 ChatbotAPI.env 파일에서 로드 (로컬 개발용)
if not api_key:
    env_path = BASE_DIR / "ChatbotAPI.env"
    if env_path.exists():
        env_values = dotenv_values(env_path)
        api_key = env_values.get("GEMINI_API_KEY")

if not api_key:
    st.error("🔑 API 키를 찾을 수 없습니다. 로컬의 경우 ChatbotAPI.env 파일을 확인해 주시고, 클라우드 배포인 경우 Secrets 설정을 확인해 주세요.")
    st.stop()

os.environ["GOOGLE_API_KEY"] = api_key

# 3. 데이터베이스 및 RAG 모델 로드 함수 (캐싱 적용)
@st.cache_resource
def load_rag_system():
    db_dir = BASE_DIR / "chromadb_store"
    if not db_dir.exists():
        return None, None
    
    # vectorize.py 와 동일한 모델과 설정 적용
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2",
        google_api_key=api_key
    )
    vectordb = Chroma(
        persist_directory=str(db_dir),
        embedding_function=embeddings
    )
    
    # 챗봇용 LLM 로드 (Gemini 1.5 Flash 사용 - 일일 1,500회 무료 쿼터 제공)
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0.1,  # 정밀한 사실 기반 답변을 위해 온도를 낮춤
        max_output_tokens=1024,
        google_api_key=api_key,
        max_retries=6
    )
    
    return vectordb, llm

vectordb, llm = load_rag_system()

# 사이드바 구성
with st.sidebar:
    st.title("⚙️ 설정 및 도구")
    st.markdown("---")
    
    # DB 상태 표시
    if vectordb is not None:
        db_count = vectordb._collection.count()
        st.success(f"데이터베이스 연결 성공\n(총 {db_count}개 청크 적재됨)")
    else:
        st.warning("⚠️ 백데이터 데이터베이스(chromadb_store)가 존재하지 않습니다. 먼저 `python scripts/vectorize.py`를 실행해 주세요.")
        
    st.markdown("---")
    
    # RAG 검색 설정
    k_value = st.slider("참조할 단락 개수 (K)", min_value=2, max_value=8, value=4, step=1)
    show_sources = st.checkbox("답변 시 참조 출처 표시", value=True)
    
    st.markdown("---")
    # 대화 초기화 버튼
    if st.button("🔄 대화 기록 초기화"):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("<p style='font-size: 0.8rem; color: #64748b;'>상가건물 임대차보호법 RAG 챗봇 v1.0</p>", unsafe_allow_html=True)

# 메인 헤더
st.title("⚖️ 상임법 전문 질의응답 챗봇")
st.markdown("내가 제공한 백데이터(상가임대차 보호법 전문, 상담 사례집, 주요 판례 등)에 근거하여 관련 법률 질문에 답변해 드립니다.")
st.markdown("---")

# 대화 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 기록 렌더링
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"] and show_sources:
            with st.expander("📚 참조된 백데이터 확인"):
                for idx, src in enumerate(message["sources"]):
                    st.markdown(f"**[{idx+1}] {src['source']}** (유사도 스코어: {src['score']:.4f})")
                    st.caption(src["content"])

# 사용자 입력 처리
if question := st.chat_input("상가건물 임대차보호법에 대해 질문해 보세요 (예: 임차인의 권리금 회수 기회 보장 기간은?)"):
    # 사용자 질문 화면 렌더링 및 저장
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})
    
    # RAG 답변 생성
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        if vectordb is None or llm is None:
            ans = "오류: 데이터베이스가 정상적으로 설정되지 않았습니다. 관리자에게 문의하세요."
            response_placeholder.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
        else:
            # 1. 유사한 법률 데이터 검색 (Similarity Search with Scores)
            # Chroma의 similarity_search_with_relevance_scores 사용
            docs_with_scores = vectordb.similarity_search_with_relevance_scores(question, k=k_value)
            
            # 2. Context 구성 및 출처 추출
            context_list = []
            sources_info = []
            
            for doc, score in docs_with_scores:
                context_list.append(doc.page_content)
                sources_info.append({
                    "source": doc.metadata.get("source", "알 수 없음"),
                    "page": doc.metadata.get("page", None),
                    "content": doc.page_content,
                    "score": score
                })
                
            context = "\n\n".join(context_list)
            
            # 3. 시스템 프롬프트 작성 (백데이터 중심 제약조건 부여)
            system_prompt = """당신은 상가건물 임대차보호법(상임법) 전문 상담 챗봇입니다.
반드시 아래에 주어진 법률 데이터(Context)만을 근거로 삼아 사용자의 질문에 답변하십시오.

[핵심 제약 조건]
1. 제공된 법률 데이터(Context)에 직접적으로 언급되거나 유추할 수 있는 내용만 사실에 입각하여 답변하십시오.
2. 제공된 데이터만으로 사용자의 질문에 대해 확실하게 답변할 수 없거나 관련 내용이 존재하지 않는 경우, 절대로 임의로 지어내거나 외부 인터넷 검색을 하거나 사전 훈련된 일반 상식으로 답변하지 마십시오. 반드시 정확하게 아래 문장만을 출력해야 합니다:
   "제공된 백데이터에서 관련 정보를 찾을 수 없습니다."
3. 만약 관련된 내용이 일부 있지만 확실하지 않은 정보가 섞여있다면, 확실한 부분만 제공된 백데이터를 인용하여 기술하고 확실치 않은 부분은 언급하지 않거나 찾을 수 없었다고 덧붙여 말하십시오.
4. 법률 조항이나 판례 등을 언급할 경우 구체적인 조항번호나 출처를 명시하십시오.

제공된 법률 데이터 (Context):
{context}"""

            # 4. LLM 체인 호출
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{question}")
            ])
            
            chain = prompt | llm
            
            with st.spinner("백데이터에서 조문을 조회하고 답변을 준비하는 중입니다..."):
                stream_res = chain.stream({"context": context, "question": question})
                
            # 5. 최종 답변 실시간 스트리밍 출력 (사용자 체감 속도 극대화)
            answer = ""
            for chunk in stream_res:
                content = chunk.content
                if isinstance(content, str):
                    answer += content
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, str):
                            answer += item
                        elif isinstance(item, dict) and "text" in item:
                            answer += item["text"]
                response_placeholder.markdown(answer + " ▌")
            response_placeholder.markdown(answer)
            
            # 6. 소스 및 답변 세션 저장
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources_info
            })
            
            # 7. 출처 박스 렌더링
            if sources_info and show_sources:
                with st.expander("📚 참조된 백데이터 확인"):
                    for idx, src in enumerate(sources_info):
                        page_str = f" p.{src['page']}" if src['page'] else ""
                        st.markdown(f"**[{idx+1}] {src['source']}{page_str}** (유사도 스코어: {src['score']:.4f})")
                        st.caption(src["content"])
                        
            # 화면 리런으로 상태 동기화
            st.rerun()
