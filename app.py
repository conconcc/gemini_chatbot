import streamlit as st
import google.generativeai as genai

# Gemini API 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
except Exception as e:
    st.error("API 키 설정에 문제가 있습니다. Streamlit Cloud에서 환경 변수를 확인해주세요.")
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title="Gemini 챗봇",
    page_icon="🤖"
)

# 제목과 설명
st.title("Gemini 챗봇 🤖")
st.markdown("""
이 챗봇은 Google의 Gemini AI를 활용한 대화형 assistant입니다.
자유롭게 질문해 주세요!
""")

# 세션 상태 초기화 (대화 기록 저장용)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 내용 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 받기
if prompt := st.chat_input("메시지를 입력해주세요"):
    # 입력 길이 제한 확인
    if len(prompt) > 1000:
        st.error("메시지가 너무 깁니다. 1000자 이내로 입력해주세요.")
        st.stop()
    
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 사용자 메시지 화면에 표시
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Gemini API에 전달할 메시지 형식으로 변환
    gemini_messages = []
    for message in st.session_state.messages:
        role = "model" if message["role"] == "assistant" else message["role"]
        gemini_messages.append({"role": role, "parts": [message["content"]]})
    
    # Gemini API 호출 및 응답 처리
    try:
        with st.spinner('응답을 생성하고 있습니다...'):
            response = model.generate_content(gemini_messages)
            if not response or not response.text:
                raise Exception("응답이 비어있습니다.")
            assistant_response = response.text
        
        # 챗봇 응답 화면에 표시
        with st.chat_message("assistant"):
            st.markdown(assistant_response)
        
        # 응답을 대화 기록에 추가
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    
    except Exception as e:
        # 에러 발생 시 사용자에게 알림
        with st.chat_message("assistant"):
            st.error(f"죄송합니다. 오류가 발생했습니다: {str(e)}")
        st.session_state.messages.append({"role": "assistant", "content": f"오류 발생: {str(e)}"})
