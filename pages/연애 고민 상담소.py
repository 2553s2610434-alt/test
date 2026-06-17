import streamlit as st
import google.generativeai as genai
import random

# 1. 페이지 설정 및 분홍빛 스타일 시트 적용
st.set_page_config(
    page_title="연애 온도계 & AI 처방전",
    page_icon="💖",
    layout="centered"
)

# 완벽한 분홍빛 테마를 위한 CSS 주입
st.markdown("""
    <style>
    .main { background-color: #FFF0F5; }
    h1 { color: #FF69B4 !important; font-family: 'Malgun Gothic', sans-serif; }
    h3 { color: #FF1493 !important; }
    .stButton>button {
        background-color: #FF69B4;
        color: white !important;
        border-radius: 12px;
        border: none;
        font-weight: bold;
        height: 3em;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #FF1493;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💖 연애 온도계 & AI 처방전")
st.write("말 못 할 연애 고민, 원하는 스타일의 상담사에게 털어놓으세요!")
st.write("---")

# 2. 안전한 API 키 로드 및 초기화
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # 요청하신 가장 최신의 가볍고 빠른 gemini-2.5-flash-lite 모델 지정
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
    except Exception as e:
        st.warning(f"AI 모델 초기화 중 문제가 발생했습니다: {e}. 시스템 모드로 전환합니다.")
        api_key = None

# 3. UI 입력 양식
col1, col2 = st.columns(2)
with col1:
    tone = st.selectbox(
        "🔮 상담사 말투 선택",
        ["다정한 언니 (공감 만렙)", "팩폭 담당 형 (뼈 때리는 현실 조언)", "츤데레 친구 (틱틱대며 챙겨줌)"]
    )
with col2:
    status = st.selectbox(
        "👩‍❤️‍👨 현재 관계 상태",
        ["짝사랑/고백 고민", "달달한 썸", "연애 중", "권태기/싸움", "이별/재회 고민"]
    )

story = st.text_area(
    "💌 연애 고민을 자세히 적어주세요",
    placeholder="예시: 연하 남친이 요즘 들어 피곤하다며 카톡 답장도 성의 없고 주말 데이트도 미뤄요. 마음이 식은 걸까요?",
    height=150
)

# 4. 핵심 실행 로직
if st.button("🌡️ 연애 온도 측정 및 처방전 받기"):
    if not story.strip():
        st.error("고민 내용을 입력해주세요!")
    else:
        with st.spinner("AI 상담사가 상황을 면밀히 분석하고 있습니다..."):
            
            # API 키가 정상 등록되어 있을 때 (AI 모드)
            if api_key:
                prompt = f"""
                너는 연애 심리 전문가이자 상담사야. 아래 조건에 맞게 유저의 연애 고민을 상담해줘.

                [정보]
                - 현재 관계: {status}
                - 유저의 고민: {story}
                - 원하는 상담사 스타일: {tone}

                [출력 형식 가이드라인]
                1. 첫 줄에는 무조건 "이 관계의 연애 온도는 [숫자]% 입니다." 라는 문장이 정확히 포함되게 작성해줘. (예: 이 관계의 연애 온도는 35% 입니다.)
                2. 그 다음 줄부터 {tone}의 페르소나에 100% 빙의해서 친근한 반말(또는 해요체)로 상대방의 심리 분석과 앞으로 해야 할 구체적인 처방전(대책)을 위트 있게 작성해줘.
                """
                
                try:
                    response = model.generate_content(prompt)
                    ai_text = response.text
                    
                    # 텍스트에서 안전하게 숫자만 추출하여 온도계 연출 (파싱 실패 방지 가드)
                    predicted_temp = 50  # 기본값
                    for word in ai_text.split():
                        if '%' in word:
                            clean_word = "".join(filter(str.isdigit, word))
                            if clean_word:
                                predicted_temp = int(clean_word)
                                break
                    
                    # 결과 화면 UI 구현
                    st.success("🎯 처방전이 도착했습니다!")
                    st.subheader("🌡️ 우리의 연애 온도계")
                    st.progress(min(max(predicted_temp / 100.0, 0.0), 1.0))
                    st.write(f"현재 두 분의 온도는 **{predicted_temp}°C** 입니다.")
                    
                    st.write("---")
                    st.subheader("💊 맞춤 처방전 리포트")
                    st.markdown(ai_text)
                    st.balloons()
                    
                except Exception as api_error:
                    st.error(f"AI 호출 중 오류가 발생했습니다: {api_error}")
                    st.info("안전 모드(자체 알고리즘)로 전환하여 기본 처방전을 발행합니다.")
                    api_key = None  # 아래 안전 모드로 진입 유도
            
            # API 키가 없거나 통신 실패 시 작동하는 안전 모드 (Fallback)
            if not api_key:
                fallback_temp = random.randint(15, 75)
                st.warning("💡 현재 체험 모드(또는 시스템 안전 모드)로 작동 중입니다.")
                
                st.subheader("🌡️ 우리의 연애 온도계")
                st.progress(fallback_temp / 100.0)
                st.write(f"현재 예상 온도는 **{fallback_temp}°C** 입니다.")
                
                st.write("---")
                st.subheader("💊 시스템 기본 처방전")
                st.write(f"**[{tone}] 스타일의 임시 처방:**")
                st.write(f"현재 입력하신 **'{status}'** 상태는 감정의 완급 조절이 극도로 필요한 시기야. 상대방의 사소한 행동 하나에 너무 일희일비하지 마! 연락의 빈도보다는 한 번을 하더라도 밀도 있는 대화를 나누는 걸 추천해. 자세한 개인 맞춤형 처방을 원하시면 배포 환경의 `GEMINI_API_KEY`를 다시 확인해줘!")
