import streamlit as st
import google.generativeai as genai

# 1. 페이지 기본 설정 및 테마 감성 추가
st.set_page_config(
    page_title="연애 온도계 & AI 처방전",
    page_icon="❤️",
    layout="centered"
)

# 간단한 커스텀 CSS로 연애 앱 분위기 연출
st.markdown("""
    <style>
    .main { background-color: #fff9fa; }
    h1 { color: #ff4b6e; }
    .stButton>button { background-color: #ff4b6e; color: white; border-radius: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("❤️ 연애 온도계 & AI 처방전")
st.subtitle("말 못 할 연애 고민, AI가 온도를 측정하고 처방전을 써드려요.")
st.write("---")

# 2. Gemini API 인증 및 초기화 (Secrets 안전 처리)
# Streamlit Cloud의 Secrets 또는 로컬의 secrets.toml에서 키를 가져옵니다.
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    # 가장 빠르고 효율적인 모델인 gemini-2.5-flash-lite 설정
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
else:
    st.warning("⚠️ API 키가 등록되지 않았습니다. 현재는 '체험 모드(예시 답변)'로 작동합니다. AI 기능을 온전히 쓰시려면 우측 사이드바나 Secrets 설정을 확인해주세요.")

# 사이드바에 API 키 안내 및 앱 소개
with st.sidebar:
    st.header("💘 앱 정보")
    st.write("이 앱은 **gemini-2.5-flash-lite**를 사용하여 당신의 연애 고민을 분석합니다.")
    if not api_key:
        st.info("💡 **팁:** Streamlit Community Cloud 배포 시 Advanced Settings -> Secrets에 `GEMINI_API_KEY = '내키'`를 입력하면 정상 작동합니다.")

# 3. 사용자 입력 화면 구성
st.subheader("📝 나의 연애 상황 입력하기")

# 단계 선택 (차별화된 맥락 파악)
stage = st.selectbox(
    "현재 어떤 단계인가요?",
    ["선택하세요", "💗 썸 / 고백 유예기", "👩‍❤️‍👨 달달한 연애 중", "🥶 권태기 / 말다툼 / 위기", "💔 이별 후 / 재회 고민"]
)

# 디테일한 상황 입력
story = st.text_area(
    "최근 있었던 일이나 상대방의 태도, 카톡 내용 등을 자세히 적어주세요.",
    placeholder="예시: 썸남이랑 3번째 데이트를 했는데, 헤어질 때 연락하겠다더니 6시간째 선톡이 없어요. 밀당인가요 식은 걸까요?",
    height=150
)

# 4. 분석하기 버튼 및 로직
if st.button("🌡️ 연애 온도 측정 & 처방전 받기"):
    if stage == "선택하세요":
        st.error("현재 연애 단계를 선택해주세요!")
    elif not story.strip():
        st.error("고민 내용을 입력해주세요!")
    else:
        with st.spinner("AI 연애 코치가 상황을 분석 중입니다... 🔍"):
            
            # 프롬프트 엔지니어링: 일관된 출력 형식을 위한 가이드라인 제공
            prompt = f"""
            너는 연애 심리 상담 전문가이자 위트 있고 공감 능력이 뛰어난 연애 코치야.
            다음 사용자 상황을 분석해서 답변해줘.

            [사용자 상황]
            - 연애 단계: {stage}
            - 상세 고민: {story}

            [답변 규칙]
            1. 현재 상황에 맞는 '연애 온도(0°C ~ 100°C)'를 숫자로 정하고 이유를 한 줄로 설명해줘.
            2. 상대방의 심리를 족집게처럼 분석해줘.
            3. 앞으로 사용자가 취해야 할 행동 지침(처방전)을 구체적인 행동 요령 2-3가지로 나누어 제안해줘.
            4. 다정하면서도 뼈를 때리는(팩트 폭행) 친근한 반말(혹은 해요체) 톤앤매너를 유지해줘. 너무 딱딱하게 쓰지 마.
            """
            
            if api_key:
                try:
                    # AI 모델 호출
                    response = model.generate_content(prompt)
                    
                    # 결과 출력
                    st.success("✨ 분석이 완료되었습니다!")
                    st.write("---")
                    st.markdown(response.text)
                    st.write("---")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"AI 호출 중 오류가 발생했습니다: {e}")
                    st.info("잠시 후 다시 시도하거나 API 키 권한을 확인해주세요.")
            else:
                # API 키가 없을 때 작동하는 오프라인 예시 데모 (초보자 오류 방지 및 체험용)
                st.info("💡 API 키가 없는 상태이므로 준비된 모범 처방전 샘플을 보여드립니다.")
                st.write("---")
                st.markdown(f"""
                ### 🌡️ 예상 연애 온도: **35°C (미지근함)**
                *이유: 관심은 있으나 확실한 한 방이 부족하거나, 상대방이 밀당 중일 확률이 높음!*

                ### 🕵️ 상대방 심리 분석
                * 입력해주신 단계 **({stage})**의 특성상, 상대방은 현재 당신의 마음을 탐색하고 있거나 본인의 감정에 확신이 서지 않았을 수 있습니다. 혼자 전전긍긍하기보단 상대방의 평소 행동 패턴을 복기해볼 필요가 있어요.

                ### 💊 AI 연애 처방전
                1. **선톡에 연연하지 말기:** 먼저 연락이 오는지 안 오는지 폰만 붙잡고 있으면 본인 멘탈만 상합니다. 취미 생활이나 본인 일에 집중하세요.
                2. **가벼운 질문 던지기:** 하루 뒤에도 연락이 없다면, 무거운 주제 대신 "오늘 날씨 되게 좋더라! 맛점했어?" 같은 가벼운 톡으로 대화를 자연스럽게 리드해보세요.
                """)
                st.write("---")
streamlit
google-generativeai
GEMINI_API_KEY = "AI_Studio에서_발급받은_실제_API_키"
