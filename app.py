import streamlit as streamlit
import google.generativeai as genai
import random
from datetime import datetime

# ====================================================================
# 1. 페이지 기본 설정 (가장 최상단 필수 배치)
# ====================================================================
st.set_page_config(
    page_title="하루 조각: 파스텔 마음 일기",
    page_icon="🎨",
    layout="centered"
)

# ====================================================================
# 2. 부드럽고 깔끔한 오가닉 파스텔톤 커스텀 CSS
# ====================================================================
st.markdown("""
    <style>
    /* 배경을 포근한 연보라/연민트 파스텔톤으로 설정 */
    .stApp {
        background-color: #F6F5FB; 
    }
    h1 {
        color: #6C5B7B !important; /* 차분한 파스텔 보라 */
        font-weight: 700;
    }
    h3 {
        color: #7A9A95 !important; /* 차분한 파스텔 민트 */
    }
    /* 버튼 스타일 디자인 */
    .stButton>button {
        background-color: #E8D7F1 !important; 
        color: #4A3E56 !important;
        border-radius: 15px !important;
        border: none !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: bold !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #D6BCF7 !important;
        transform: translateY(-1px);
    }
    /* 기록 보관함 카드 커스텀 */
    div[data-testid="stForm"], .mood-box {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        padding: 1.8rem !important;
        border: 1px solid #EAEAEA !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02) !important;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ====================================================================
# 3. 청소년을 위한 명언 데이터 세팅
# ====================================================================
FAMOUS_QUOTES = [
    "“만약 한 사람이 교육을 소홀히 한다면, 그는 생이 다할 때까지 한 발을 절며 걷는 것이다.” - 플라톤",
    "“만약 당신이 그것을 꿈꾼다면, 당신은 그것을 할 수 있다.” - 월트 디즈니",
    "“행복은 종종 당신이 열어둔 지도 몰랐던 문을 통해 살금살금 들어온다.” - 존 베리모어",
    "“당신이 성장할 때, 세상도 함께 성장한다.” - 존 F. 케네디",
    "“당신이 할 수 있다고 믿든, 할 수 없다고 믿든, 믿는 대로 될 것이다.” - 헨리 포드",
    "“우리가 걷는 길은 항상 옳은 길은 아니다. 그러나 계속 걷다 보면 그 길이 옳은 길이 될 수도 있다.” - 헨리 드루먼드",
    "“성공하려면 실패를 맛봐야 한다. 실패는 성공의 어머니다.” - 앨버트 아인슈타인",
    "“가장 위대한 영광은 결코 실패하지 않은 것이 아니라, 실패를 거듭하더라도 다시 일어서는 것이다.” - 넬슨 만델라",
    "“당신이 성공하기를 바라면, 다른 사람들을 돕고, 그들이 성공할 수 있도록 도와주세요.” - 부영우",
    "“성취하려면 대담하게 꿈꾸고, 끈질기게 실행해 나가야 한다.” - 월트 디즈니",
    "“인생은 진리를 찾는 여정이다.” - 마하트마 간디",
    "“우리가 어려움을 극복할 때, 우리는 더욱 강해진다.” - 스티브 버트튼",
    "“때로는 실패가 우리를 올바른 길로 인도할 수 있다.” - J.K. 롤링"
]

# 화면 새로고침 시 명언 고정용 세션 관리
if "today_quote" not in st.session_state:
    st.session_state.today_quote = random.choice(FAMOUS_QUOTES)

# 가상의 기분 저장소 초기화 (한 달 단위 누적용 샘플 데이터 제공)
if "mood_history" not in st.session_state:
    st.session_state.mood_history = [
        {"date": "2026-06-01", "mood": "😊 행복/뿌듯", "note": "모의고사 성적이 조금 올랐다!"},
        {"date": "2026-06-05", "mood": "😭 슬픔/지침", "note": "친구랑 사소한 일로 다퍘다. 마음이 온종일 무겁다."}
    ]

# ====================================================================
# 4. [원하는 기능] 들어오자마자 명언 띄우기
# ====================================================================
st.info(f"💌 **오늘 너를 안아줄 한 줄의 문장**\n\n{st.session_state.today_quote}")

# 5. 타이틀 표시
st.title("🎨 하루 조각: 파스텔 마음 일기")
st.write("오늘 네 마음에 머문 감정 이모지를 선택하고 무거운 짐을 이곳에 편하게 털어내보렴.")
st.markdown("---")

# ====================================================================
# 6. Gemini API 독립 초기화 (구조적 에러 완전 차단)
# ====================================================================
api_ready = False
try:
    gemini_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    api_ready = True
except KeyError:
    st.error("⚠️ Secrets 설정에 'GEMINI_API_KEY'가 누락되었습니다. 스트림릿 관리자 설정을 확인해 주세요.")
except Exception as init_err:
    st.error(f"⚠️ API 연동 초기화 에러: {init_err}")

# ====================================================================
# 7. 이모지 기분 기록 폼 (Form 독립 구조 설계)
# ====================================================================
with st.form(key="mood_form", clear_on_submit=True):
    st.write("📝 **오늘의 기분 조각 맞추기**")
    
    # 이모지 기분 선택기
    selected_mood = st.selectbox(
        "지금 이 순간, 네 기분을 가장 잘 표현하는 이모지는 뭐야?",
        ["😊 행복/뿌듯", "☁️ 평온/무덤덤", "😭 슬픔/지침", "😡 화남/답답", "🧠 불안/생각많음"]
    )
    
    # 이유 및 고민 기록 창
    mood_note = st.text_
