import streamlit as st
import pandas as pd
import numpy as np

from utils import extract_text_from_docx


st.title('AI Job Seeker')

st.text('Use this form to create an AI representative for your job search process.\n' \
'Once you are done, you can chat with it.')

CV_uploaded_file = st.file_uploader("Upload your CV (.docx only)", type=["docx"])

if CV_uploaded_file is not None:
    st.write("File uploaded successfully!")

    # Example: if it's a .docx
    if CV_uploaded_file.name.endswith(".docx"):
        CV_contents = extract_text_from_docx(CV_uploaded_file)
        #st.write(CV_contents)

    # Show file details
    st.write("Filename:", CV_uploaded_file.name)
    st.write("File type:", CV_uploaded_file.type)
    st.write("File size:", CV_uploaded_file.size, "bytes")