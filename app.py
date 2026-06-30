# python -m streamlit run app.py

import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
from chatbot_new import getBotReply

def load_css():
    with open("style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide"
)
load_css()
# st.title("Chatbot")
# st.caption("● Online")

# if st.button("Clear Chat"):
#     st.session_state.messages = []
#     st.rerun()

header_col1, header_col2 = st.columns([8,2])

with header_col1:

    st.markdown("<h1>Chatbot</h1>", unsafe_allow_html=True)

with header_col2:

    clear = st.button(
        "Clear Chat",
        use_container_width=True
    )

if clear:
    st.session_state.messages = []
    st.rerun()





if "messages" not in st.session_state: #st.session_state is streamlit's memory. it keeps the data even when the page refreshes.
    st.session_state.messages = [] # if the variable "message" is not in the session state, then it will create an empty list. it also stores all the chat conversastios

# for chat in st.session_state.messages:
#     with st.chat_message("user"):
#         st.write(chat["user"])


#     with st.chat_message("assistant"):
#         st.write(chat["bot"])


for chat in st.session_state.messages:
    st.markdown(
        f"""
        <div class="user-msg">
            {chat['user']}
        </div>
        """,
        unsafe_allow_html=True 
    )

    st.markdown(
        f"""
        <div class="bot-msg">
            {chat['bot']}
        </div>
        """,
        unsafe_allow_html=True
    )
  

user_message = st.chat_input(
    "Type your message:"
)

# if user_message:

#     bot_response = ""

#     with st.spinner("Thinking..."): # it takes few seconds to load the response, so using this st.spinner() it shows a loading message with a spinning animation while code is running
#         reply = getBotReply(user_message)
#         st.session_state.messages.append( #append new iten to the end of the list
#             {
#                 "user": user_message,
#                 "bot": reply
#             }
#         )


if user_message:

    thinking = st.empty()

    thinking.markdown(
        """
        <div class="bot-msg">
            Thinking...
        </div>
        """,
        unsafe_allow_html=True
    )

    reply = getBotReply(user_message)

    thinking.empty()

    st.session_state.messages.append(
        {
            "user": user_message,
            "bot": reply
        }
    )

    st.rerun()
