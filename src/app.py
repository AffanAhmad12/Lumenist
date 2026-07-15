from admin_panel import show_admin_panel
from chat import answer_question
from ingest_upload import process_upload_files
from streamlit_mic_recorder import mic_recorder
from auth import authenticate
from signup import register_user
import speech_recognition as sr
import streamlit as st 
import json
import io
import base64
import os

#background--
def set_bakground(image_path):
    with open(image_path,"rb") as f:
        data= base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp{{
                background-image: url("data:image/png;base64,{data}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
    }}  
    [data-testid="stAppViewContainer"] {{
        background: transparent;
    }}
    [data-testid= "stHeader"]{{
        background: transparent;
    }}
    [data-testid="stSidebar"]{{
        background: rgba(0,0,30,0.85);
    }}
    </style>
    """, unsafe_allow_html=True)
    

set_bakground("background.png")

st.markdown("""
    <style>
    iframe[title="streamlit_mic_recorder.mic_recorder"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    div:has(> iframe[title="streamlit_mic_recorder.mic_recorder"]) {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

#  Login page
if "username" not in st.session_state:
    col1, col2 =st.columns([1, 5])
    with col1:
     st.image("chatbot.png", width=100)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.title("Welcome to Lumenist")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        st.subheader("Please login to continue")
        username_input = st.text_input("Username:", key= "login_username")
        password_input = st.text_input("Password:", type="password", key="login_password")
         
        if st.button("Login"):
            if username_input.strip() and password_input.strip():
                role = authenticate(username_input, password_input)
                if role:
                    st.session_state["username"] = username_input.strip()
                    st.session_state["role"] = role
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            else:
                st.warning("Please enter both username and password.")
    with tab2:
        st.subheader("Create a new account")
        new_username = st.text_input("Username:", key="signup_username")
        new_password = st.text_input("Password:",type="password", key="signup_password")
        
        if st.button("Create Account"):
            if not new_username.strip() or not new_password.strip():
                st.error("Please fill in both username and password.")
            else:
                success, message = register_user(new_username.strip(),new_password)
                if success:
                    st.success(message)
                else:
                    st.error(message)
    st.stop() 
# Reset chat History 

username = st.session_state["username"]
role = st.session_state["role"]


if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

#After login page
username = st.session_state["username"]

col1, col2 = st.columns([3, 30])
with col1:
    st.markdown("<br>", unsafe_allow_html=True)
    st.image("chatbot.png", width=80)

with col2:
    
        st.title("Lumenist - HR Policy Assistant")
        


col1, col2 = st.columns([10,21])
with col1:
  st.markdown("<h5>Powered by Lumelight</h5>", unsafe_allow_html=True)

with col2:
       
        st.image("lumelight_logo.jpeg", width=35)


st.caption(f"logged in as :{username}")


# --- Sidebar---
if "show_upload"not in st.session_state:
    st.session_state["show_upload"]= False

#making arrow
arrow = "▼ Add documents to knowledge base" if st.session_state["show_upload"]else "▶ Add documents to knowledge base"

if st.sidebar.button(arrow, key="upload_toggle"):
    st.session_state["show_upload"]= not st.session_state["show_upload"]
    st.rerun()
    
if st.session_state["show_upload"]:
 uploaded_files = st.sidebar.file_uploader(
    "upload PDF , DOCX, or TXT files",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
)

 if uploaded_files and st.sidebar.button("Process & Add"):
    with st.spinner("Processing files ...."):
        summary = process_upload_files(uploaded_files, role=role)
    for item in summary:
        st.sidebar.success(f"{item['file']}: {item['chunks_added']} chunks added({item['department']})")

#admin approval
with st.sidebar:
 if st.session_state.get("role") == "ADMIN":
    with st.expander("Admin Panel"):
        show_admin_panel()
#history
if  st.session_state["chat_history"]:
    st.sidebar.header("Chat History")
    for i , item in enumerate(reversed(st.session_state["chat_history"])):
        with st.sidebar.expander(f"Q{len(st.session_state['chat_history']) - i}: {item['question'][:40]}..."):
            st.write(f"**Question:**{item['question']}")
            st.write(f"**Answer:**{item['answer']}")

#logout--
st.sidebar.markdown(f"**Logged in as:** {username}")
st.sidebar.markdown(f"**Role:** {role}")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# main area
st.header("Ask a question")

# two columns — text input + mic button side by side
col1, col2 = st.columns([8, 1])

with col1:
    typed_query = st.text_input("Type your question here:", key="text_input")

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    audio = mic_recorder(
        start_prompt="🎤",
        stop_prompt="⏹️",
        just_once=True,
        key="mic"
    )


#which input to use
query = None


if audio:
    with st.spinner("Transcribing..."):
        try:
            import tempfile
            from pydub import AudioSegment
            
            # save raw webm audio to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_webm:
                tmp_webm.write(audio["bytes"])
                webm_path = tmp_webm.name
            
            # convert webm to wav using pydub
            wav_path = webm_path.replace(".webm", ".wav")
            AudioSegment.from_file(webm_path, format="webm").export(wav_path, format="wav")
            
            # now read the wav file
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
            
            query = recognizer.recognize_google(audio_data)
            st.info(f"🎤 You said: {query}")
            
            # cleanup temp files
            os.remove(webm_path)
            os.remove(wav_path)
            
        except sr.UnknownValueError:
            st.warning("Could not understand audio. Please try again.")
        except sr.RequestError as e:
            st.error(f"Speech recognition unavailable: {e}")
        except Exception as e:
            st.error(f"Audio error: {e}")

elif typed_query:
    query = typed_query

if query:
    with st.spinner("Searching..."):
        result = answer_question(query, username, role)

    st.subheader("Answer")
    st.write(result["answer"])

    if result["sources"]:
        st.subheader("Sources")
        for source in result["sources"]:
            st.write(f"-- {source}")

    st.session_state["chat_history"].append({
        "question": query,
        "answer": result["answer"]
    })
    
