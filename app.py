import streamlit as st
import google.generativeai as genai
import random
from datetime import datetime

# ====================================================================
# 1. 페이지 기본 설정 (가장 최상단 필수 배치)
# ====================================================================
st.set_page_config(
    page_title="파스텔 밤하늘 감정 보관함",
    page_icon="🌙",
    layout="centered"
)

# ====================================================================
# 2. 몽환적인 밤하늘 그라데이션 및 실시간 열기구 상승 애니메이션 CSS 효과
# ====================================================================
st.markdown('''
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

/* 명언 배너 상자 커스텀 */
div.stAlert {
    background-color: rgba(255, 255, 255, 0.6) !important;
    border: 1px solid #D6BCF7 !important;
    border-radius: 15px !important;
}

/* 버튼을 달빛 느낌의 파스텔 노랑/보라 톤으로 커스텀 */
.stButton>button {
    background-color: #FAE19C !important; 
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
.mood-box, div[data-testid="stForm"] {
    background-color: rgba(255, 255, 255, 0.75) !important;
    border-radius: 18px !important;
    padding: 2rem !important;
    border: 1px solid rgba(214, 188, 247, 0.3) !important;
    box-shadow: 0 8px 20px rgba(108, 91, 123, 0.05) !important;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(5px);
}

/* 🎈 몽환적인 열기구 상승 애니메이션 핵심 레이아웃 효과 */
@keyframes flyUp {
    0% { transform: translateY(100vh) scale(0.5); opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { transform: translateY(-120vh) scale(1.2); opacity: 0; }
}
.hot-air-balloon {
    position: fixed;
    left: 45%;
    bottom: -10vh;
    font-size: 80px;
    animation: flyUp 4s linear forwards;
    z-index: 9999;
    pointer-events: none;
}
</style>
''', unsafe_allow_html=True)

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
    "“때로는 실패가 우리를 올바른 길
