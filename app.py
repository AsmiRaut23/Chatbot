# python -m streamlit run app.py

import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
from chatbot_new import getBotReply

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

st.title("Smart AI Chatbot")

if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

if "messages" not in st.session_state: #st.session_state is streamlit's memory. it keeps the data even when the page refreshes.
    st.session_state.messages = [] # if the variable "message" is not in the session state, then it will create an empty list. it also stores all the chat conversastios

user_message = st.chat_input(
    "Type your message:"
)

if user_message:

    bot_response = ""

    # response = client.models.generate_content_stream(
    #     model="gemini-flash-lite-latest",
    #     contents=user_message
    # )

    # placeholder = st.empty()
    # for chunk in response:
    #     text = getattr(chunk, "text", "")
    #     if text:
    #         bot_response += text
    #         placeholder.write("bot:" + bot_response)

    reply = getBotReply(user_message)
    st.session_state.messages.append( #append new iten to the end of the list
        {
            "user": user_message,
            "bot": reply
        }
    )

    for chat in st.session_state.messages:
        with st.chat_message("user"):
            st.write(chat["user"])


        with st.chat_message("assistant"):
            st.write(chat["bot"])
  