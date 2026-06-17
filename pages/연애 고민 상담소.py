import streamlit as st
import google.generativeai as genai
import re

# 1. 페이지 설정 및 디자인 (분홍빛 테마)
st.set_page_config(page_title="연애 온도계 & AI 처방전", page_icon="🌡️")

st.markdown("""
    <style>
    .main {
        background-color: #FFF0F5;
    }
    .stButton>button {
        background-color: #FF69B4;
        color: white;
        border-radius: 20px;
        border: none;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FF1493;
        color: white;
    }
    h1, h2, h3 {
        color: #D02090;
    }
    .status-box {
        padding: 20px;
        border-radius: 15px;
        background-color: white;
        border: 2px solid #FFC0CB;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. API 키 설정 및 예외 처리
def get_ai_response(prompt):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        # 사용 가능한 최신 모델 사용 (1.5-flash는 빠르고 안정적입니다)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except KeyError:
        return "오류: Secrets에 GEMINI_API_KEY가 설정되지 않았습니다."
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"

# 3. 앱 헤더
st.title("💖 연애 온도계 & AI 처방전")
st.write("당신의 연애 고민을 들려주세요. AI 상담사가 온도를 측정하고 처방전을 써드립니다.")

# 4. 입력 섹션
with st.container():
    st.markdown('<div class="status-box">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        counselor_style = st.selectbox(
            "상담사의 말투를 선택해줘",
            ["다정한 언니 (공감과 위로)", "냉철한 형 (팩폭과 논리)", "츤데레 친구 (틱틱대지만 진심)"]
        )
    with col2:
        relation_status = st.selectbox(
            "현재 우리의 관계는?",
            ["짝사랑", "썸 타는 중", "연애 중", "권태기/싸움", "이별 후 재회 고민"]
        )
    
    user_story = st.text_area("어떤 고민이 있는지 자세히 알려줘 (예: 카톡 답장이 5시간째 없어요...)", height=150)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 5. 분석 로직
if st.button("연애 온도 측정 및 처방전 받기"):
    if not user_story.strip():
        st.warning("먼저 고민 내용을 입력해줘!")
    else:
        with st.spinner("AI 상담사가 당신의 이야기를 분석 중..."):
            # 프롬프트 구성
            prompt = f"""
            너는 연애 상담 전문가야. 아래의 정보를 바탕으로 사용자의 연애 고민을 상담해줘.
            
            1. 상담사 말투: {counselor_style}
            2. 현재 관계: {relation_status}
            3. 사용자의 고민: {user_story}
            
            [응답 형식]
            1. 연애 온도: 0도에서 100도 사이로 측정하고 그 이유를 짧게 설명해줘.
            2. 심리 분석: 상대방과 사용자의 심리 상태 분석.
            3. 처방전: 앞으로 어떻게 행동해야 할지 구체적인 대책(Action Plan) 3가지를 제시해줘.
            
            [말투 지침]
            - {counselor_style}에 맞춰서 대답해줘. 
            - 다정한 언니는 '~했구나, 그랬어?' 같은 부드러운 말투.
            - 냉철한 형은 '~이다, ~해라' 같은 단호하고 논리적인 말투.
            - 츤데레 친구는 '야, 너 바보냐?' 처럼 툭툭 던지지만 마지막엔 따뜻한 말투.
            """
            
            result = get_ai_response(prompt)
            
            if "오류" in result:
                st.error(result)
            else:
                st.write("---")
                # 온도 추출 시도 (정규표현식)
                temp_match = re.search(r"(\d+)도", result)
                temp_val = int(temp_match.group(1)) if temp_match else 50
                
                # 온도계 시각화
                st.subheader("🌡️ 연애 온도계")
                st.progress(temp_val / 100)
                st.markdown(f"### 현재 온도는 **{temp_val}°C** 입니다.")
                
                st.write("---")
                
                # 결과 출력
                st.subheader("💊 AI 맞춤 처방전")
                st.markdown(result)
                
                st.balloons()

# 하단 정보
st.caption("© 2024 연애 온도계 & AI 처방전. All rights reserved.")
