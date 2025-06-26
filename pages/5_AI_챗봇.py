"""
AI 챗봇 페이지
탄소 배출 데이터 분석을 위한 AI 챗봇 인터페이스
"""

import streamlit as st
import sys
import os
from datetime import datetime

# 상위 디렉토리의 agent 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agent.carbon_rag_agent import get_carbon_agent, initialize_agent
except ImportError as e:
    st.error(f"RAG 에이전트 모듈을 불러올 수 없습니다: {e}")
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title="AI 챗봇 - 탄소 데이터 분석",
    page_icon="🤖",
    layout="wide"
)

# 커스텀 CSS (기존 main.py 스타일과 일치)
st.markdown("""
<style>
    .main-header {
        font-size: 36px;
        font-weight: bold;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e, #2ca02c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 40px;
    }
    .chat-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .chat-message {
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
    }
    .user-message {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        margin-left: 20%;
    }
    .assistant-message {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        margin-right: 20%;
    }
    .data-info-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 15px 0;
        border-left: 5px solid #1f77b4;
    }
    .example-queries {
        background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_query' not in st.session_state:
    st.session_state.current_query = ""
if 'auto_submit' not in st.session_state:
    st.session_state.auto_submit = False

# 타이틀
st.markdown('<h1 class="main-header">🤖 AI 챗봇 - 탄소 데이터 분석</h1>', unsafe_allow_html=True)

# 에이전트 초기화
@st.cache_resource
def load_agent():
    """RAG 에이전트 로드 (캐시 사용)"""
    return get_carbon_agent()

# 에이전트 로드
try:
    agent = load_agent()
except Exception as e:
    st.error(f"에이전트 초기화 실패: {e}")
    st.stop()

# 데이터 정보 표시
st.markdown("""
<div class="data-info-card">
    <h3>📊 데이터 정보</h3>
</div>
""", unsafe_allow_html=True)

data_info = agent.get_available_data_info()
st.markdown(data_info)

# 예시 질문들
st.markdown("""
<div class="example-queries">
    <h3>💡 예시 질문들</h3>
</div>
""", unsafe_allow_html=True)

example_queries = [
    "📈 총배출량의 연도별 변화 추이는?",
    "🏭 에너지 산업과 수송 산업의 배출량 비교",
    "📊 2017년과 2021년의 배출량 차이는?",
    "🔍 가장 많이 배출하는 분야는?",
    "📉 감축률이 가장 높은 연도는?",
    "🌍 전체 데이터에서 평균 배출량은?"
]

def process_example_query(query):
    """예시 질문 처리 함수"""
    # 즉시 질문 처리
    try:
        with st.spinner("🤔 AI가 데이터를 분석하고 있습니다..."):
            response, visualization = agent.ask(query)
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if visualization:
                st.session_state.chat_history.append((query, response, timestamp, visualization))
            else:
                st.session_state.chat_history.append((query, response, timestamp))
    except Exception as e:
        st.error(f"❌ 오류가 발생했습니다: {e}")
    
    # 상태 초기화 및 페이지 새로고침
    st.session_state.current_query = ""
    st.session_state.auto_submit = False
    st.rerun()  # 답변이 즉시 보이도록 페이지 새로고침

col1, col2 = st.columns(2)
with col1:
    for i, query in enumerate(example_queries[:3]):
        if st.button(query, key=f"example_{i}"):
            process_example_query(query)

with col2:
    for i, query in enumerate(example_queries[3:], 3):
        if st.button(query, key=f"example_{i}"):
            process_example_query(query)

# 채팅 인터페이스
st.markdown("""
<div class="chat-container">
    <h3>💬 AI 챗봇과 대화하기</h3>
    <p>탄소 배출 데이터에 대해 궁금한 것을 물어보세요!</p>
</div>
""", unsafe_allow_html=True)

# 채팅 히스토리 표시
for i, chat_item in enumerate(st.session_state.chat_history):
    # 채팅 항목이 튜플인지 확인 (기존 호환성)
    if len(chat_item) == 3:
        user_msg, assistant_msg, timestamp = chat_item
        visualization = None
    elif len(chat_item) == 4:
        user_msg, assistant_msg, timestamp, visualization = chat_item
    else:
        continue
    
    st.markdown(f"""
    <div class="chat-message user-message">
        <strong>🙋‍♂️ 사용자:</strong> {user_msg}
        <br><small>{timestamp}</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="chat-message assistant-message">
        <strong>🤖 AI 어시스턴트:</strong> {assistant_msg}
    </div>
    """, unsafe_allow_html=True)
    
    # 시각화가 있는 경우 표시
    if visualization:
        try:
            import base64
            import io
            from PIL import Image
            
            # base64 디코딩하여 이미지 표시
            img_data = base64.b64decode(visualization)
            img = Image.open(io.BytesIO(img_data))
            
            # 크기를 900x600으로 고정
            resized_img = img.resize((900, 600), Image.Resampling.LANCZOS)
            
            st.image(resized_img, caption="AI가 생성한 데이터 시각화", width=900)
        except Exception as viz_error:
            st.warning(f"시각화 표시 중 오류: {viz_error}")

def handle_input_change():
    """입력 변경 시 처리 함수 (엔터키 처리)"""
    if st.session_state.chat_input.strip():
        query = st.session_state.chat_input.strip()
        process_query(query)

def process_query(query):
    """질문 처리 함수"""
    if query.strip():
        try:
            # 로딩 표시와 함께 처리
            with st.spinner("🤔 AI가 데이터를 분석하고 있습니다..."):
                # 에이전트에게 질문
                response, visualization = agent.ask(query)
                
                # 채팅 히스토리에 추가
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if visualization:
                    st.session_state.chat_history.append((query, response, timestamp, visualization))
                else:
                    st.session_state.chat_history.append((query, response, timestamp))
                
                # 입력창 초기화
                st.session_state.chat_input = ""
                st.session_state.auto_submit = False
                st.session_state.current_query = ""
                
                # 페이지 새로고침으로 입력창 초기화 반영
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ 오류가 발생했습니다: {e}")
            st.session_state.auto_submit = False

# 질문 입력 (답변 후 자동으로 비워짐)
user_input = st.text_input(
    "질문을 입력하세요 (엔터키로 바로 전송):",
    value=st.session_state.get("chat_input", ""),  # 세션 상태에서 값 가져오기
    key="chat_input",
    placeholder="예: 2021년 총배출량은 얼마인가요?",
    on_change=handle_input_change
)

# 예시 질문은 process_example_query에서 즉시 처리됨

# 질문 처리 버튼 (엔터키 외 추가 옵션)
if st.button("🚀 질문하기", key="ask_button"):
    if user_input.strip():
        process_query(user_input)
    else:
        st.warning("질문을 입력해주세요.")

# 무한 루프 방지를 위해 제거됨

# 채팅 히스토리 초기화 버튼
if st.session_state.chat_history:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🗑️ 채팅 히스토리 초기화", key="clear_history"):
            st.session_state.chat_history = []
            st.rerun()

# 플로팅 챗봇 버튼 제거됨

# 질문창은 항상 유지 (초기화하지 않음) 