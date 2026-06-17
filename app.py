import streamlit as streamlit
import google.generativeai as genai
import random
from datetime import datetime

# 1. 페이지 기본 설정 (가장 최상단 배치)
st.set_page_config(
    page_title="하루 조각: 파스텔 마음 일기",
    page_icon="🎨",
    layout="centered")
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
    }/* 버튼 스타일 디자인 */
    .stButton>button {
        background-color: #E8D7F1 !important; 
        color: #4A3E56 !important;
        border-radius: 15px !important;
        border: none !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: bold !important;
        transition: all 0.2s ease;
    }.stButton>button:hover {
        background-color: #D6BCF7 !important;
        transform: translateY(-1px);
    }
    /* 구조 박스 커스텀 */
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
if "today_quote" not in st.session_state:
    st.session_state.today_quote = random.choice(FAMOUS_QUOTES)

# 가상의 기분 저장소 초기화 (초보자용으로 별도 DB 연결 없이 세션 메모리에 저장 및 한 달 단위 연동)
if "mood_history" not in st.session_state:
    st.session_state.mood_history = [
        {"date": "2026-06-01", "mood": "😊 기쁨", "note": "모의고사 성적이 조금 올랐다!"},
        {"date": "2026-06-05", "mood": "😭 슬픔", "note": "친구랑 사소한 일로 다퍘다. 마음이 불편하다."}
    ]
    st.info(f"💌 **오늘 너를 안아줄 한 줄의 문장**\n\n{st.session_state.today_quote}")
    st.title("🎨 하루 조각: 파스텔 마음 일기")
st.write("오늘 네 마음에 머문 감정 이모지를 선택하고 무거운 짐을 이곳에 털어내보렴.")
st.markdown("---")
try:
    gemini_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
except KeyError:
    st.error("⚠️ Secrets 설정에 'GEMINI_API_KEY'가 누락되었습니다. 스트림릿 관리자 페이지 설정을 확인해 주세요.")
    st.stop()
except Exception as init_err:
    st.error(f"⚠️ 시스템 초기화 에러: {init_err}")
    st.stop()
    with st.form(key="mood_form", clear_on_submit=True):
    st.write("📝 **오늘의 기분 조각 맞추기**")
    selected_mood = st.selectbox(
        "지금 이 순간, 네 기분을 가장 잘 표현하는 이모지는 뭐야?",
        ["😊 행복/뿌듯", "☁️ 평온/무덤덤", "😭 슬픔/지침", "😡 화남/답답", "🧠 불안/생각많음"]
    )
    mood_note = st.text_area(
        "그 기분이 든 이유나 덜어내고 싶은 마음의 짐을 편하게 적어봐.",
        placeholder="예시: 학업 스트레스 때문에 숨이 턱 막히는 기분이에요. 누구에게도 말 못 해서 속상해요...",
        height=120
    )
    
    submit_btn = st.form_submit_button(label="기록하고 마음 처방전 받기 ✨")
    if submit_btn:
    if not mood_note.strip():
        st.warning("이유나 고민을 조금이라도 적어주셔야 마음 상담 샘이 답장을 보낼 수 있어요!")
    else:
        # 오늘 날짜 생성
        today_str = datetime.today().strftime('%Y-%m-%d')
        
        # 임시 세션 저장소에 추가 (새로고침 시 누적 유지됨)
        st.session_state.mood_history.append({
            "date": today_str,
            "mood": selected_mood,
            "note": mood_note
        })
        with st.spinner("마음 상담 선생님이 네 일기를 읽고 따뜻한 편지를 쓰고 있어..."):
            system_prompt = f"""
            당신은 청소년(중·고등학생)의 마음의 짐을 덜어주는 매우 부드럽고 다정한 상담 교사입니다.
            학생이 기록한 이모지 감정태그와 고민 내용을 바탕으로 따뜻한 처방 편지를 작성하세요.
            
            [학생의 오늘 상태]
            - 선택한 기분 이모지: {selected_mood}
            - 털어놓은 이야기: {mood_note}
            
            [답변 규칙]
            1. 절대 훈계하거나 '네가 더 노력해야지' 같은 조언, 설교를 엄금합니다.
            2. 첫 문장은 학생의 기분과 아픔에 대해 전적으로 공감하고 다독이는 대화로 시작하세요.
            3. 친근하고 따뜻한 존댓말 구어체(~했구나, ~그랬겠어요, ~해볼까요)를 유지하세요.
            4. 마지막은 마음이 한결 가벼워질 수 있는 감성 가득한 위로와 응원으로 끝맺어 주세요."""
            try:
                response = model.generate_content(system_prompt)
                st.markdown("---")
                st.success("✉️ **상담 선생님에게서 도착한 파스텔 위로 편지**")
                st.write(response.text)
                st.balloons()
            except Exception as api_err:
                st.error(f"답장을 불러오는 중 오류가 발생했습니다. (사유: {api_err})")
               st.markdown("---")
st.subheader("📅 이번 달 마음 조각 모아보기 (한 달 단위)")

current_month = datetime.today().strftime('%Y-%m')
st.caption(f"현재 기준 월: {current_month} 에 기록된 마음 데이터입니다.")
if st.session_state.mood_history:
    # 이번 달 데이터만 필터링하는 안전장치
    this_month_data = [item for item in st.session_state.mood_history if item["date"].startswith(current_month)]
    
    if not this_month_data:
        st.info("이번 달에 아직 기록된 기분이 없어요. 첫 감정 조각을 채워보세요!")
    else:
        for item in reversed(this_month_data):
            st.markdown(f"""
            <div class="mood-box">
                <span style="color:#6C5B7B; font-weight:bold;">📅 {item['date']}</span> | 
                <span style="background-color:#FFF5F5; padding:2px 8px; border-radius:8px;">{item['mood']}</span>
                <p style="margin-top:10px; color:#555555; font-size:15px;">💬 {item['note']}</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("마음 사서함에 기록된 기분이 아직 없습니다. 오늘부터 가볍게 시작해 보세요!")
    
