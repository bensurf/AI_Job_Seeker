import streamlit as st
#import pandas as pd
#import numpy as np
import openai
from openai import OpenAI

import prompts

from utils import extract_text_from_docx


st.title('AI Job Seeker')

st.text('Create an AI representative for your job search process by uploading your CV and a narrative that goes into more detail about yourself.\n\n' \
'Once you are done, you can chat with it.')

st.markdown("---")

CV_uploaded_file = st.file_uploader("Upload your CV (.docx only)", type=["docx"])

if CV_uploaded_file is not None:
    st.write("File uploaded successfully!")

    # Example: if it's a .docx
    if CV_uploaded_file.name.endswith(".docx"):
        CV_contents = extract_text_from_docx(CV_uploaded_file)
        #st.write(CV_contents)

    # Show file details
    #st.write("Filename:", CV_uploaded_file.name)
    #st.write("File type:", CV_uploaded_file.type)
    #st.write("File size:", CV_uploaded_file.size, "bytes")

CV_narrative_file = st.file_uploader("Upload a narrative providing additional details, stories, and background about your past experience, skills, and career goals. (.docx only)", type=["docx"])

if CV_narrative_file is not None:
    st.write("File uploaded successfully!")

    # Example: if it's a .docx
    if CV_narrative_file.name.endswith(".docx"):
        CV_narrative_contents = extract_text_from_docx(CV_narrative_file)
        #st.write(CV_narrative_contents)


if "chat_started" not in st.session_state:
    st.session_state["chat_started"] = False

system_prompt = st.text_area("System prompt: These are the instructions for the chatbot's personality and behavior.",
                             value = prompts.default_system_prompt,
                             height=500,
                             disabled=st.session_state["chat_started"])

st.markdown("---")

def start():
    st.session_state['chat_started'] = True

if CV_uploaded_file is not None and CV_narrative_file is not None:
    st.button('Start the conversation', on_click=start, disabled=st.session_state["chat_started"])


if st.session_state["chat_started"]:

    st.text("Your AI representative has been created!\n" \
            "Chat with it as if you are a recruiter here:")

    openai.api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    BACKGROUND_CONTEXT = f"""{system_prompt}

    To understand who you are impersonating, here is their CV as well as a narrative going into more detail. Base all of your responses off of this information, as if you are this person:

    ######
    CV
    ######
    {CV_contents}

    ######
    Narrative
    ######
    {CV_narrative_contents}
    """


    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": BACKGROUND_CONTEXT}
        ]

    # Display previous messages
    for msg in st.session_state.messages[1:]:  # Skip system message
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input box
    if prompt := st.chat_input("Thank you for reaching out about my job application. What would you like to know about me?"):
        
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call OpenAI
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # response = openai.ChatCompletion.create(
                #     model="gpt-4",  # or "gpt-3.5-turbo"
                #     messages=st.session_state.messages
                # )
                # reply = response.choices[0].message.content
                # st.markdown(reply)

                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=st.session_state.messages
                )

                reply = response.choices[0].message.content
                st.markdown(reply)

        # Save assistant reply
        st.session_state.messages.append({"role": "assistant", "content": reply})