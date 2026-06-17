import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="스마트 공부 멘토링 룸", page_icon="📝")
st.title("📝 스마트 공부 멘토링 룸")
st.caption("gemini-2.5-flash-lite 모델로 작동하는 맞춤형 공부 조언 챗봇입니다.")

# 2. 챗봇의 페르소나 설정 (SyntaxError를 방지하기 위해 한 줄 문자열로 안전하게 정의)
SYSTEM_INSTRUCTION = "당신은 학생들의 학습 습관, 시간 관리, 과목별 공부법을 정성껏 상담해주는 전문 교육 멘토입니다. 사용자의 학습 고민을 진지하게 듣고, 구체적이고 실천 가능한 공부 전략과 동기부여 메시지를 제공해야 합니다. 상황에 따라 적절한 이모지를 사용하여 친근하고 격려하는 톤앤매너를 유지해주세요."

# 3. Streamlit Secrets에서 API 키 가져오기 및 초기화
try:
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("GitHub Secrets 또는 Streamlit 세팅에 'GEMINI_API_KEY'가 설정되지 않았습니다.")
        st.stop()
        
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"API 키 인증 중 오류가 발생했습니다: {e}")
    st.stop()

# 4. 세션 상태(Session State)로 채팅 기록 유지
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. 기존 채팅 기록 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. 사용자 입력 및 챗봇 답변 처리
if prompt := st.chat_input("공부법, 시간 관리 등 고민을 편하게 적어보세요..."):
    # 사용자가 입력한 메시지 화면에 표시 및 저장
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 챗봇의 답변 생성 과정
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("📚 고민을 분석하고 조언을 준비 중입니다...")
        
        try:
            # gemini-2.5-flash-lite 모델 설정
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash-lite",
                system_instruction=SYSTEM_INSTRUCTION
            )
            
            # 대화 맥락 유지용 기록 변환
            history = []
            for msg in st.session_state.messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["content"]]})
            
            # 대화 시작 및 답변 생성
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            
            # 결과 출력 및 저장
            full_response = response.text
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            error_msg = f"죄송합니다. 조언을 생성하는 중에 오류가 발생했어요. 😢 (오류 내용: {e})"
            message_placeholder.markdown(error_msg)
