import streamlit as st
#import pandas as pd
#import numpy as np
import openai
from openai import OpenAI
import chatbot

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

st.markdown("---")



if CV_uploaded_file is not None and CV_narrative_file is not None:

    chatbot.start_chatbot(CV_contents, CV_narrative_contents)