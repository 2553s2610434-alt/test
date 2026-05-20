import streamlit as st
st.title('천안오성고등학교 화이팅')
st.write('바이브코딩 재미있다!!')
import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="스케줄 메이커", page_icon="📅")

st.title("📅 스케줄 만들기")

# 세션 상태 초기화
if "schedules" not in st.session_state:
    st.session_state.schedules = []

# 입력 폼
with st.form("schedule_form"):
    title = st.text_input("일정 제목")
    schedule_date = st.date_input("날짜", value=date.today())
    time = st.time_input("시간")
    memo = st.text_area("메모")

    submitted = st.form_submit_button("추가하기")

    if submitted:
        if title:
            st.session_state.schedules.append({
                "제목": title,
                "날짜": schedule_date.strftime("%Y-%m-%d"),
                "시간": time.strftime("%H:%M"),
                "메모": memo
            })
            st.success("일정이 추가되었습니다!")
        else:
            st.warning("일정 제목을 입력하세요.")

# 일정 표시
st.subheader("📌 등록된 일정")

if st.session_state.schedules:
    df = pd.DataFrame(st.session_state.schedules)
    st.dataframe(df, use_container_width=True)
else:
    st.info("등록된 일정이 없습니다.")
