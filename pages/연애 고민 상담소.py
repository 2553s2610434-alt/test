import streamlit as st
import google.generativeai as genai

# 페이지 기본 설정
st.set_page_config(
    page_title="연애 AI 처방전",
    page_icon="💌",
    layout="centered"
)

# 앱 제목 및 설명 (에러가 없는 안전한 표준 함수만 사용)
st.title("💌 연애 온도계 & AI 처방전")
st.write("말 못 할 연애 고민을 나누어주세요. AI가 상황을 분석하고 맞춤 처방전을 써드립니다.")
st.write("---")

# Secrets에서 API 키 안전하게 가져오기
api_key = st.secrets.get("GEMINI_API_KEY")

# API 설정 및 예외 처리
if api_key:
    try:
        genai.configure(api_key=api_key)
        # 요구사항에 명시된 gemini-2.5-flash-lite 모델 지정
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        api_ready = True
    except Exception as e:
        st.error(f"API 연결에 실패했습니다. 원인: {e}")
        api_ready = False
else:
    api_ready = False
    st.info("💡 배포 전이거나 API 키가 없는 상태입니다. (체험 모드로 작동 중)")

# 입력 양식 구성
st.subheader("📝 나의 연애 고민 작성하기")

# 1. 연애 단계 선택
stage = st.selectbox(
    "현재 어떤 단계인가요?",
    ["선택하세요", "썸 / 고백 준비", "연애 중", "권태기 / 갈등", "이별 후 / 재회 고민"]
)

# 2. 고민 내용 입력
story = st.text_area(
    "상황이나 고민을 자세히 적어주세요.",
    placeholder="예시: 연락 문제로 자주 싸우는데 어떻게 대화를 풀어야 할지 모르겠어요.",
    height=150
)

# 3. 버튼 클릭 시 로직 수행
if st.button("🌡️ 연애 온도 측정 및 조언 받기"):
    if stage == "선택하세요":
        st.warning("현재 연애 단계를 선택해주세요.")
    elif not story.strip():
        st.warning("고민 내용을 입력해주세요.")
    else:
        with st.spinner("AI 상담사가 신중하게 분석하고 있습니다..."):
            
            # AI에게 보낼 프롬프트 구성
            prompt = f"""
            너는 다정하면서도 현실적인 조언을 주는 전문 연애 상담사야.
            다음 사용자의 연애 고민을 분석해서 답변해줘.

            [사용자 상황]
            - 연애 단계: {stage}
            - 상세 고민: {story}

            [답변 규칙]
            1. 현재 상황의 '연애 온도(0% ~ 100%)'와 그렇게 판단한 이유를 간결하게 설명해줄 것.
            2. 상대방의 심리와 현재 문제의 핵심 원인을 분석해줄 것.
            3. 사용자가 바로 실천할 수 있는 현실적인 행동 지침 2-3가지를 제안해줄 것.
            4. 존댓말로 작성하되, 친구처럼 친근하고 진심 어린 톤앤매너를 유지할 것.
            """
            
            if api_ready:
                try:
                    # AI 모델 결과 생성
                    response = model.generate_content(prompt)
                    
                    st.success("✨ 분석이 완료되었습니다!")
                    st.write("---")
                    st.markdown(response.text)
                    st.write("---")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"답변 생성 중 에러가 발생했습니다: {e}")
            else:
                # API 키가 등록되지 않았을 때 작동하는 안전한 데모 화면
                st.write("---")
                st.info("현재 API 키가 등록되지 않아 샘플 답변이 제공됩니다. Secrets 설정을 완료하시면 실제 AI 조언을 보실 수 있습니다.")
                st.markdown(f"""
                ### 🌡️ 예상 연애 온도: **40%**
                *이유: 소통의 타이밍이 엇갈려 서운함이 쌓이고 있는 상태입니다.*

                ### 🔍 핵심 상황 분석
                * 입력해주신 **[{stage}]** 단계에서는 서로의 진심을 오해하는 경우가 많습니다. 상대방이 악의가 없다 하더라도, 표현 방식의 차이로 인해 서운함이 증폭되었을 가능성이 큽니다.

                ### 💊 추천 행동 처방전
                1. **내 감정 먼저 정리하기:** 감정이 격해진 상태에서 대화하기보다, 내가 정확히 어떤 부분에서 서운했는지 생각 정리하기.
                2. **'나' 화법으로 대화 시도하기:** "너 왜 그래?"가 아니라 "네가 그렇게 행동할 때 내 마음이 조금 슬펐어"라고 부드럽게 전달해보기.
                """)
                st.write("---")
