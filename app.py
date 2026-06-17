import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 디자인
st.set_page_config(
    page_title="마음나침반 - AI 연애 상담소",
    page_icon="💖",
    layout="centered"
)

# 간단한 커스텀 스타일 적용 (핑크 톤 테마)
st.markdown("""
    <style>
    .main-title { font-size: 2.2rem; font-weight: bold; color: #FF4B4B; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 1.1rem; color: #666; text-align: center; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💖 마음나침반 AI 연애 상담소</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">말하기 어려운 연애 고민, AI 카운셀러가 따뜻하고 솔직하게 들어드릴게요.</div>', unsafe_allow_html=True)

# 2. API 키 설정 및 예외 처리
# Streamlit Cloud의 Secrets 기능을 사용하거나, 로컬 테스트용 설정을 지원합니다.
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # 로컬 테스트 시 사이드바에서 입력 가능하도록 예외 처리
    api_key = st.sidebar.text_input("Gemini API Key를 입력하세요", type="password")

if not api_key:
    st.info("💡 앱을 시작하려면 Streamlit Secrets 또는 사이드바에 'GEMINI_API_KEY'를 설정해주세요.", icon="🔑")
    st.stop()

# Gemini 모델 초기화
try:
    genai.configure(api_key=api_key)
    # 기획 요구사항에 따른 gemini-2.5-flash-lite 모델 지정
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
except Exception as e:
    st.error(f"API 초기화 중 오류가 발생했습니다: {e}")
    st.stop()

# 3. 사용자 입력 화면 구성
st.subheader("📋 나의 연애 상황 입력하기")

# 상황 선택 (차별화 포인트)
situation_type = st.selectbox(
    "현재 어떤 상황이신가요?",
    ["선택해주세요", "💘 짝사랑 - 고백 타이밍이나 마음을 알고 싶어요", "💬 썸 - 연인으로 발전하고 싶어요", "👩‍❤️‍👨 연애 중 - 갈등이 있거나 더 잘 지내고 싶어요", "😭 이별/미련 - 마음을 정리하거나 재회를 원해요"]
)

# 입력 폼
with st.form("love_counsel_form"):
    gender_age = st.text_input("본인과 상대방의 성별/나이대 (예: 20대 중반 여성 / 20대 후반 남성)", placeholder="예: 20대 중반 여성 / 20대 후반 남성")
    context = st.text_area(
        "자세한 고민 내용을 적어주세요.",
        placeholder="상황, 두 분의 대화 패턴, 최근에 있었던 서운한 점 등을 자세히 적어주실수록 정확한 분석이 가능합니다.",
        height=150
    )
    
    # 조언 스타일 선택
    advice_style = st.radio(
        "원하시는 조언 스타일은?",
        ["공감 중심 (따뜻한 위로와 격려)", "팩트 폭행 (현실적이고 직설적인 피드백)", "전략 중심 (구체적인 행동 지침과 멘트 추천)"],
        horizontal=True
    )
    
    submit_button = st.form_submit_button(label="💝 AI 카운셀러에게 상담 받기")

# 4. 상담 로직 실행
if submit_button:
    if situation_type == "선택해주세요":
        st.warning("현재 어떤 상황인지 (짝사랑, 썸, 연애 등) 선택해주세요!")
    elif not context.strip():
        st.warning("고민 내용을 입력해주세요!")
    else:
        with st.spinner("AI 카운셀러가 고민을 신중하게 분석하고 있습니다...⏳"):
            # 프롬프트 엔지니어링 (선택된 옵션에 따른 맞춤형 지시)
            prompt = f"""
            너는 연애 심리학을 전공한 다정하고 명쾌한 전문 연애 상담사야. 
            아래 내담자의 고민을 듣고 진심을 다해 상담해줘.

            [내담자 정보]
            - 상황: {situation_type}
            - 당사자 정보: {gender_age if gender_age else "정보 미입력"}
            - 원하는 조언 스타일: {advice_style}
            
            [고민 내용]
            {context}

            [답변 규칙]
            1. 첫 시작은 내담자의 마음을 따뜻하게 공감해주는 한 문장으로 시작할 것.
            2. 조언 스타일({advice_style})의 특징을 100% 반영하여 답변할 것. (예: 팩트 폭행이면 돌려 말하지 말고 현실을 짚어줄 것)
            3. 답변은 다음 3가지 섹션으로 나누어 가독성 좋게 마크다운 문법으로 출력할 것:
               - ### 🔍 상황 분석 및 심리 파악
               - ### 💡 맞춤형 연애 솔루션
               - ### 💬 추천 대화 멘트 (상대방에게 보내기 좋은 카톡이나 대화 예시 1~2개)
            """
            
            try:
                response = model.generate_content(prompt)
                
                st.success("✨ AI 카운셀러의 진단이 완료되었습니다!")
                st.markdown("---")
                st.markdown(response.text)
                st.markdown("---")
                st.caption("※ 본 상담은 AI의 분석이므로 참고용으로만 활용하시기 바랍니다. 당신의 사랑을 응원합니다! 🌸")
                
            except Exception as e:
                st.error(f"⚠️ 답변을 생성하는 중 오류가 발생했습니다. (원인: {e})")
