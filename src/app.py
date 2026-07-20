from admin_panel import show_admin_pannel, show_delete_pannel
from chat import answer_question
from ingest_upload import process_upload_files
from streamlit_mic_recorder import mic_recorder
from auth import authenticate
from signup import register_user
from history import get_user_history, clear_user_history
from gtts import gTTS
import speech_recognition as sr
import streamlit as st 
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
#Read out loud
def speak_answer(text, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")as tmp:
            tts.save(tmp.name)
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        os.remove(tmp_path)
        st.audio(audio_bytes, format="auto/mp3", autoplay=True)
    except Exception as e:
        st.warning(f"Could not play audio: {e}")
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
        with st.expander("Approve Pending Users"):
            show_admin_pannel()
        with st.expander("Remove Users"):
            show_delete_pannel()
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
tab_chat, tab_history = st.tabs(["💬 Chat", "📜 Full History"])

with tab_chat:
    st.header("Ask a question")
with tab_history:
    st.subheader("📜 Full Conversation History")
    full_history = get_user_history(username)

    if not full_history:
        st.info("No conversation history yet.")
    else:
        search_term = st.text_input("Search history", placeholder="Search by keyword", key = "history_search") 
        if search_term:
            term = search_term.lower()
            filtered = [
                h for h in full_history
                if term in h["question"].lower() or term in h["answer"].lower()
            ]
        else:
            filtered = full_history

        st.caption(f"Showing {len(filtered)} of {len(full_history)} conversations")

        with st.expander("⚠️ Clear all history"):
            st.warning("This permanently deletes all your saved conversation.")
            confirm = st.checkbox("I understand this cannot be undone", key="confirm_clear")
            if st.button("Clear History", disabled=not confirm):
                clear_user_history(username)
                st.success("History cleared.")
                st.rerun()

        st.divider()

        if not filtered:
            st.info("No conversation match your search.")

        else:
            for entry in filtered:
                with st.expander(f"🕒 {entry['timestamp']}- {entry['question'][:80]}"):
                    st.markdown(f"**Question:** {entry['question']}")
                    st.markdown(f"**Answer:**{entry['answer']}")
                    if entry["sources"]:
                        st.markdown(f"**Sources:**{entry['sources']}")

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
            
            # convert webm to wav 
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

# track if voice was used
voide_used = audio is not None and query is not None and audio == query or (audio and not typed_query)
if query:
    with st.spinner("Searching..."):
        result = answer_question(query, username, role)

    st.subheader("Answer")
    st.write(result["answer"])

    if result["sources"]:
        st.subheader("Sources")
        for source in result["sources"]:
            st.write(f"-- {source}")

    #Speak answer if voice was use
    if audio and query:
        detected = "en"
        try:
            if len(query.strip())>=20:
                from langdetect import detect
                detected = detect(query)
        except:
            detected = "en"
        speak_answer(result["answer"], lang=detected if detected != "en" else "en")

    st.session_state["chat_history"].append({
        "question": query,
        "answer": result["answer"]
    })
    
