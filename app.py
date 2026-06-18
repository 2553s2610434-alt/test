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
# 2. 몽환적인 밤하늘 그라데이션 및 실시간 열기구 상승 애니메이션 CSS 효과
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
    </
