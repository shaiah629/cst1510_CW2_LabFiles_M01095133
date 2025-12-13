import streamlit as st
from openai import OpenAI

# Initialize OpenAI client with API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the AI Chatbot.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")   # back to the first page
    st.stop()

#Page configuration
st.set_page_config(
    page_title="ShaiahGPT",
    page_icon="💬",
    layout="wide",
)

#Title
st.title("💬 ShaiahGPT - AI Chatbot")
st.caption("Powered by GPT-4.1-mini")

#Initialize session state for messages
if 'messages' not in st.session_state:
    st.session_state.messages = []

#Sidebar with controls
with st.sidebar:
    st.subheader("Chat Controls")

    message_count = len([m for m in st.session_state.messages if m["role"]!= "system"])
    st.metric("Messages", message_count)

    # Clear chat button
    if st.button("🗑️ CLear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    #Model
    model = "gpt-4.1-mini"

    #Temperature slider
    temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=1.0, step=0.1, help="Controls the randomness of the AI's responses.")

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
prompt = st.chat_input("Type your message here...")

if prompt:
    #Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    #Add user message to session state
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    #Call OpenAI API with streaming
    with st.spinner("Thinking..."):
        completion = client.chat.completions.create(
            model=model,
            messages=st.session_state.messages,
            temperature=temperature,
            stream=True
        )

    with st.chat_message("assistant"):
        container = st.empty()
        full_reply = ""

        for chunk in completion:
            delta = chunk.choices[0].delta
            if delta.content:
                full_reply += delta.content
                container.markdown(full_reply + " ") #Add cursor effect

        container.markdown(full_reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_reply
    })


