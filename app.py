
Gemini와의 대화
스트림릿으로 제미나이 챗봇을 만들어줘.

- 고민상담 챗봇이야





- 모델은 gemini-2.5-flash-lite 사용



- API 키는 secrets로 불러오기



- 채팅 기록 유지, 오류 처리 포함



- requirements.txt 내용도 알려줘 

스트림릿(Streamlit)과 구글의 최신 모델인 gemini-2.5-flash-lite를 활용하여 만든 따뜻한 고민상담 챗봇 코드입니다.

요청하신 대로 채팅 기록 유지(Session State), API 키 보안 관리(Secrets), 그리고 예외 처리(Error Handling)를 모두 포함하여 직관적이고 깔끔하게 구성했습니다.

1. 프로젝트 구조
프로젝트 폴더를 생성하고 다음과 같이 파일 구조를 만들어 주세요.

Plaintext
your-project-folder/
│
├── .streamlit/
│   └── secrets.toml      # API 키 저장 파일 (보안)
├── app.py                # 스트림릿 메인 코드
└── requirements.txt      # 필요 라이브러리 목록
2. 환경 설정 파일
.streamlit/secrets.toml
스트림릿은 .streamlit/secrets.toml 파일을 통해 API 키를 안전하게 관리합니다. 이 파일에 구글 AI 스튜디오에서 발급받은 API 키를 넣어주세요.

Ini, TOML
GOOGLE_API_KEY = "your_actual_gemini_api_key_here"
⚠️ 주의: 이 파일은 민감한 정보를 담고 있으므로, GitHub 등에 업로드할 때 .gitignore에 반드시 추가해 주세요.

requirements.txt
프로젝트 실행에 필요한 라이브러리 목록입니다.

Plaintext
streamlit>=1.30.0
google-genai>=0.1.1
(참고: 최신 Gemini 모델들을 안정적으로 지원하는 구글의 공식 새 SDK인 google-genai를 사용합니다.)

3. 메인 소스 코드 (app.py)
스트림릿의 대화형 UI(st.chat_message, st.chat_input)를 활용한 전체 코드입니다. 고민상담소에 어울리는 따뜻한 페르소나를 시스템 지침(System Instruction)으로 주입했습니다.

Python
import streamlit as rm
import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="마음 정원 - 고민상담 챗봇", page_icon="🌱", layout="centered")
st.title("🌱 마음 정원 고민상담소")
st.caption("누구에게도 말하지 못했던 고민, 편하게 이야기해 보세요. 당신의 이야기를 귀 기울여 듣겠습니다.")

# 2. API 키 로드 및 클라이언트 초기화
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("API 키가 설정되지 않았습니다. `.streamlit/secrets.toml` 파일을 확인해 주세요.")
    st.stop()

try:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.error(f"클라이언트 초기화 중 오류가 발생했습니다: {e}")
    st.stop()

# 3. 세션 상태(Session State)로 채팅 기록 유지
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요. 오늘 어떤 고민이 있으신가요? 마음 속 이야기를 들려주세요."}
    ]

# 4. 기존 대화 기록을 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 사용자 입력 받기
if user_input := st.chat_input("여기에 고민을 나누어 주세요..."):
    
    # 사용자의 메시지를 화면에 표시 및 세션에 저장
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 챗봇의 답변 생성 공간 마련
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("💭 당신의 이야기를 생각하는 중입니다...")
        
        try:
            # 6. Gemini API 호출 (System Instruction으로 페르소나 설정)
            # 대화 기록 유지를 위해 세션에 있던 메시지들을 Gemini 형식으로 변환하여 전달합니다.
            contents = [
                types.Content(
                    role="user" if m["role"] == "user" else "model",
                    parts=[types.Part.from_text(text=m["content"])]
                ) for m in st.session_state.messages[:-1] # 방금 넣은 user_input 직전까지의 대화
            ]
            # 현재 입력된 유저 메시지 추가
            contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_input)]))

            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "당신은 공감 능력이 매우 뛰어나고 따뜻한 전문 심리 상담사입니다. "
                        "사용자의 말에 깊이 공감하고, 절대 비난하거나 섣부른 판단을 내리지 마세요. "
                        "위로가 되는 부드러운 어조를 사용하고, 사용자가 스스로 마음을 정리할 수 있도록 "
                        "도와주는 따뜻한 질문을 덧붙여 주세요. 답변은 너무 길지 않고 다정하게 작성해 주세요."
                    ),
                    temperature=0.7,
                )
            )
            
            # 답변 출력 및 세션 저장
            ai_response = response.text
            message_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except APIError as ae:
            # Gemini API 관련 오류 처리
            error_msg = f"API 오류가 발생했습니다: {ae.message}"
            message_placeholder.markdown(f"⚠️ {error_msg}")
            st.error(f"상세 에러 내용: {ae}")
        except Exception as e:
            # 기타 일반 오류 처리
            error_msg = "죄송합니다. 메시지를 처리하는 도중 예기치 못한 에러가 발생했습니다."
            message_placeholder.markdown(f"⚠️ {error_msg}")
            st.error(f"상세 에러 내용: {e}")
