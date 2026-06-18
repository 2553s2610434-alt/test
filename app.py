import streamlit as st
import google.generativeai as genai
import random
from datetime import datetime
import time

# ====================================================================
# 1. 페이지 기본 설정 (가장 최상단 필수 배치)
# ====================================================================
st.set_page_config(
    page_title="파스텔 밤하늘 감정 보관함",
    page_icon="🌙",
    layout="centered"
)

# ====================================================================
# 2. 몽환적인 밤하늘 파스텔톤 커스텀 CSS (하늘색~보라색 그라데이션)
# ====================================================================
st.markdown("""
    <style>
    /* 배경을 하늘색과 보라색 사이의 몽환적인 파스텔 그라데이션으로 설정 */
    .stApp {
        background: linear-gradient(135deg, #E0ECF8 0%, #E8D7F1 50%, #D4E6F1 100%);
        background-attachment: fixed;
    }
    
    /* 타이틀 및 폰트 색상을 은은하고 깊은 밤하늘 보라색으로 설정 */
    h1 {
        color: #4A3B56 !important; 
        font-weight: 800;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
    }
    h3 {
        color: #5B6A8A !important;
    }
    
    /* 명언 배너 상자를 밤하늘의 빛나는 구름처럼 부드럽게 커스텀 */
    div.stAlert {
        background-color: rgba(255, 255, 255, 0.6) !important;
        border: 1px solid #D6BCF7 !important;
        border-radius: 15px !important;
    }
    
    /* 버튼을 달빛 느낌의 파스텔 노랑/보라 톤으로 커스텀 */
    .stButton>button {
        background-color: #FAE19C !important; /* 부드러운 달빛 노란색 */
        color: #4A3B56 !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        font-weight: bold !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #F3D17A !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1) !important;
    }
    
    /* 입력 폼 및 기록 보관함 카드를 깔끔하고 투명도 있는 흰색으로 정리 */
    div[data-testid="stForm"], .mood-box {
        background-color: rgba(255, 255, 255, 0.75) !important;
        border-radius: 18px !important;
        padding: 2rem !important;
        border: 1px solid rgba(214, 188, 247, 0.3) !important;
        box-shadow: 0 8px 20px rgba(108, 91, 123, 0.05) !important;
        margin-bottom: 1.2rem;
        backdrop-filter: blur(5px);
    }
    </style>
""", unsafe_allow_html=True)

# ====================================================================
# 3. 유명인들의 꿈과 용기에 관한 명언 데이터 세팅
# ====================================================================
FAMOUS_QUOTES = [
    "“꿈을 이루고자 하는 용기만 있다면 모든 꿈을 이룰 수 있다.” — 월트 디즈니",
    "“만약 한 사람이 교육을 소홀히 한다면, 그는 생이 다할 때까지 한 발을 절며 걷는 것이다.” — 플라톤",
    "“행복은 종종 당신이 열어둔 지도 몰랐던 문을 통해 살금살금 들어온다.” — 존 베리모어",
    "“당신이 성장할 때, 세상도 함께 성장한다.” — 존 F. 케네디",
    "“당신이 할 수 있다고 믿든, 할 수 없다고 믿든, 믿는 대로 될 것이다.” — 헨리 포드",
    "“우리가 걷는 길은 항상 옳은 길은 아니다. 그러나 계속 걷다 보면 그 길이 옳은 길이 될 수도 있다.” — 헨리 드루먼드",
    "“가장 위대한 영광은 결코 실패하지 않은 것이 아니라, 실패를 거듭하더라도 다시 일어서는 것이다.” — 넬슨 만델라",
    "“인생은 진리를 찾는 여정이다.” — 마하트마 간디",
    "“때로는 실패가 우리를 올바른 길로 인도할 수 있다.” — J.K. 롤링",
    "“위대한 일을 해내는 유일한 방법은 자신이 하는 일을 사랑하는 것이다.” — 스티브 잡스",
    "“너의 가치는 시험 점수나 다른 사람의 말 한마디로 결정되지 않아. 넌 존재 자체로 빛나.” — 오프라 윈프리",
    "“어제와 똑같이 살면서 다른 미래를 기대하는 것은 정신병 초기증세이다.” — 앨버트 아인슈타인",
    "“행동은 모든 성공의 기초적인 핵심 요건이다.” — 파블로 피카소"
]

# 화면 새로고침 시 명언 고정용 세션 관리
if "today_quote" not in st.session_state:
    st.session_state.today_quote = random.choice(FAMOUS_QUOTES)

# 데이터 휘발 방지를 위한 브라우저 세션 영구 연동 구조
if "mood_history" not in st.session_state:
    st.session_state.mood_history = [
        {"date": "2026-06-01", "mood": "🧠 불안/생각많음", "note": "진로에 대한 생각이 많아 밤하늘을 보며 뒤척였다."},
        {"date": "2026-06-15", "mood": "☁️ 평온/무덤덤", "note": "친구랑 가볍게 산책을 하고 나니 마음이 한결 편해졌다."}
    ]

# 새로 작성한 AI 답변을 임시 유지하기 위한 세션 공간
if "latest_ai_response" not in st.session_state:
    st.session_state.latest_ai_response = None

# ====================================================================
# 4. 들어오자마자 명언 띄우기
# ====================================================================
st.info(f"✨🌙 **오늘 밤, 너의 하늘에 뜬 위로의 별 하나**\n\n{st.session_state.today_quote}")

# ====================================================================
# 5. 메인 화면 타이틀
# ====================================================================
st.title("🌌 감정 보관함")
st.markdown("---")

# ====================================================================
# 6. Gemini API 독립 초기화
# ====================================================================
api_ready = False
try:
    gemini_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    api_ready = True
except KeyError:
    st.error("⚠️ Secrets 설정에 'GEMINI_API_KEY'가 누락되었습니다. 스트림릿 관리자 페이지 설정을 확인해 주세요.")
except Exception as init_err:
    st.error(f"⚠️ API 연동 초기화 에러: {init_err}")

# ====================================================================
# 7. 이모지 기분 기록 구역
# ====================================================================
st.write("🌙 **오늘 밤, 내 마음의 날씨 조각**")

selected_mood = st.selectbox(
    "지금 이 순간, 네 감정을 가장 잘 표현하는 이모지는 뭐야?",
    ["😊 행복/뿌듯", "☁️ 평온/무덤덤", "😭 슬픔/지침", "😡 화남/답답", "🧠 불안/생각많음"],
    key="user_mood_select"
)

mood_note = st.text_area(
    "밤하늘에 편지를 쓰듯, 속에 담아둔 고민과 마음의 짐을 털어내봐.",
    placeholder="예시: 하고 싶은 꿈이 있는데 부모님이 반대하셔서 속상해요. 디즈니 명언처럼 용기를 내고 싶지만 불안감이 앞서요...",
    height=120,
    key="user_mood_note"
)

# 제출 버튼
submit_btn = st.button(label="밤하늘로 편지 띄우기 🚀", key="submit_mood_button")

# ====================================================================
# 8. 제출 처리 및 몽환적인 열기구 상승 모션 구현
# ====================================================================
if submit_btn:
    if not mood_note.strip():
        st.warning("이야기를 조금이라도 적어주셔야 마음 상담 선생님이 밤하늘의 답장을 보낼 수 있어요!")
    elif not api_ready:
        st.error("⚠️ API 키 설정에 문제가 있어 마음 처방전을 생성할 수 없습니다.")
    else:
        # 1. 데이터 저장 (세션 스토리지에 확실하게 누적)
        today_str = datetime.today().strftime('%Y-%m-%d')
        st.session_state.mood_history.append({
            "date": today_str,
            "mood": selected_mood,
            "note": mood_note
        })
        
        # 2. 몽환적인 열기구 상승 모션 애니메이션 작동
        motion_placeholder = st.empty()
        for frame in range(4):
            up_effect = "\n" * (4 - frame)
            down_effect = "\n" * frame
            motion_placeholder.markdown(f"""
            <div style="text-align:center; font-size: 40px; background-color: rgba(255,255,255,0.4); padding: 20px; border-radius:15px;">
                {up_effect}✨ 🎈 🧸 ✨<br>
                <span style="font-size:16px; color:#4A3B56; font-weight:bold;">네 감정을 가득 채운 열기구가 밤하늘을 향해 둥실둥실 오르는 중...</span>
                {down_effect}
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.7)
        motion_placeholder.empty()

        # 3. AI 상담 편지 생성 및 저장
        with st.spinner("마음 사서함 선생님이 달빛 아래에서 네 일기를 읽고 답장을 쓰고 있어..."):
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
            4. 마지막은 마음이 한결 가벼워질 수 있는 감성 가득한 위로와 응원으로 끝맺어 주세요.
            """
            
            try:
                response = model.generate_content(system_prompt)
                st.session_state.latest_ai_response = response.text
            except Exception as api_err:
                st.error(f"답장을 생성하는 중 API 오류가 발생했습니다: {api_err}")

# AI 답변 출력 고정 렌더링
if st.session_state.latest_ai_response:
    st.markdown("---")
    st.success("✉️ **달빛을 타고 도착한 위로의 편지**")
    st.write(st.session_state.latest_ai_response)
    st.snow()  # 반짝이는 밤하늘 입자 효과

# ====================================================================
# 9. 이번 달 마음 조각 모아보기 타임라인
# ====================================================================
st.markdown("---")
st.subheader("📅 이번 달 마음 조각 모아보기")

current_month = datetime.today().strftime('%Y-%m')
st.caption(f"현재 기준 월: **{current_month}** 에 밤하늘로 보낸 소중한 기록입니다.")

if st.session_state.mood_history:
    this_month_data = [item for item in st.session_state.mood_history if item["date"].startswith(current_month)]
    
    if not this_month_data:
        st.info("이번 달에 아직 기록된 기분이 없어요. 첫 감정 조각을 채워보세요!")
    else:
        for item in reversed(this_month_data):
            st.markdown(f"""
            <div class="mood-box">
                <span style="color:#5B6A8A; font-weight:bold;">🌙 {item['date']}</span> | 
                <span style="background-color:#E8D7F1; color:#4A3E56; padding:3px 10px; border-radius:10px; font-size:14px; font-weight:bold;">{item['mood']}</span>
                <p style="margin-top:12px; color:#444444; font-size:15px; line-height:1.6;">💬 {item['note']}</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("기록된 감정 조각이 없습니다.")
