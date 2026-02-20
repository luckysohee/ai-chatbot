# google에서 제공하는 LLM API 사용하기
# Goolge AI Studio 플랫폼 사이트에서 키발급

# 라이브러리 설치
#pip install -q -U google-genai

#0. api_key 노출되면 안됨. 별도의 환경변수파일.env에 저장하여 dotenv모듈로 불러서 적용
# 단, 우리의 챗봇을 streamlit cloud에 배포 예정. 이곳은 .env 설정 못함.
# 그래서 streamlit에서 제공하는 비밀값을 저장하는 속성 secrets 활용 [secrets에 등록된 값들은 .streamlit폴더 안에 secrets.toml파일로 등록. 이 파일은 Github를 통해 배포되면 안됨. 노출되면 일정시간 후 정지. 다시 키발급 필요.]
import streamlit as st
if "GEMINI_API_KEY" in st.secrets:
    api_key=st.secrets["GEMINI_API_KEY"]

#1. 라이브러리사용
from google import genai
#2. 요청 사용자 객체 생성
client=genai.Client(api_key=api_key)

# 답변에 참고할 데이터를 리턴해주는 함수 만들기
import datetime
def get_today():
    """이 함수는 오늘의 날짜에 대한 답변에 사용됩니다."""
    now=datetime.datetime.now()
    return now({'location':'korea seoul', 'year':now.year,'month':now.month, 'day':now.day})

# 응답 제어를 위한 하이퍼파라미터 설정
from google.genai import types
config=types.GenerateContentConfig(
    max_output_tokens=10000,
    response_mime_type='text/plain',
    system_instruction='넌 밝고밝디 밝은 명랑소녀야. 넌 최대 100글자 안에서 어린이도 이해할 수 있게 뭐든 설명해.',
    #system_instruction='넌 모든 대답을 개조식으로해.'
    #system_instruction='넌 불량고등학생이야. 비속어 적당히 사용하고 100글자 안에 말해.',
    # 응답할때 특정 기능함수를 참고하여 답변.
    tools=[get_today]
)

# '질문'을 파라미터로 받아서 GET AI 로 응답한 글씨를 리턴해주는 기능함수 만들기
def get_ai_response(question):
    response=client._models.generate_content(
        model="gemini-3-flash-preview",
        #model="gemini-2.5-flash",
        contents=question,
        #모델의 응답방법을 설정하기 - 하이퍼 파라미터 설정
        config=config
    )
    return response.text




#----------------------------------------------
#3. 채팅 UI 만들기

#1) 페이지 기본설정 - 브라우저 택영역에 표시되는 내용.
st.set_page_config(
    page_title='AI 히히',
    page_icon='./logo/챗봇소녀.png',
    )

#2) HEADER 영역 (레이아웃  : 이미지 + 제목 영역 가로 배치)
col1, col2=st.columns([1.2,4.8])

with col1:
    st.image("./logo/챗봇소녀.png", width=200)

with col2:
    #제목(h1)+서브안내글씨(p) [색상을 다르게.. 하려면 HTML코드로 구현]
    st.markdown(
        """
        <h1 style='margin-bottom:0;'>AI 명량소녀</h1>
        <p style='margin-top:0; color:gray'>이 챗봇은 모든 답변을 밝고 명랑하게 합니다. 샤라랑~</p>
        """,
        unsafe_allow_html=True
    )

#구분선
st.markdown("---")

#3) 채팅 UI 구현

#a. messages라는 이름의 변수가 session_state에 존재하는지 확인. 후 없으면 첫 문장 지정
if "messages" not in st.session_state:
    st.session_state.messages=[
        {'role':'assistant','content':'무엇이든 물어보세요. 샤라랑~'}
    ]

#b. session_state에 저장된 "messages"의 메세지들을 채팅 UI로 그려내기
for msg in st.session_state.messages:
    st.chat_message(msg['role']).write(msg['content'])

#c. 사용자 채팅메세지를 입력받아 session_state에 저장하고 UI 갱신
question=st.chat_input('질문 입력해보셔요. 샤라랑~')
if question:
    question=question.replace('\n','  \n')
    st.session_state.messages.append({'role':'user','content':question})
    st.chat_message('user').write(question)

    #응답 - AI 응답요구기능 함수 호출... 응답대기 시간동안 보여줄 스피너 프로그래스 요소 필요
    with st. spinner('AI가 응답 중입니다.'):
        response=get_ai_response(question)
        st.session_state.messages.append({'role':'assistant','content':response})
        st.chat_message('assistant').write(response)

#-----------------------------------------------------------------
# streamlit 웹앱 배포
#1. streamlit community cloud 배포
#2. GitHub에 프로젝트 업로드
#3. new app을 통해 앱을 만들어 GitHub 저장소와 연결
#4. 자동 배포됨.
