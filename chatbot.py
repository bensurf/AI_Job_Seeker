import streamlit as st
from openai import OpenAI
import openai
import tempfile
from streamlit_webrtc import webrtc_streamer, WebRtcMode#, ClientSettings
import av
import wave
import numpy as np

# Audio Processor Class
class AudioProcessor:
    def __init__(self):
        self.frames = []

    def recv(self, frame: av.AudioFrame):
        audio_data = frame.to_ndarray().flatten()
        self.frames.append(audio_data)
        return frame

def start_chatbot(CV_contents,CV_narrative_contents):
    st.text("Your AI representative has been created!\n" \
    "Chat with it as if you are a recruiter here:")
    
    input_mode = st.radio("Choose chat mode:", ["Text", "Voice"], horizontal=True)

    

    openai.api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    BACKGROUND_CONTEXT = f"""
    You are an AI representative for someone seeking a job.
    You are to respond to questions as if you are this person speaking to a recruiter in an interview for the first time.
    As such, do the following:
        1) Introduce yourself with your name
        2) Be very polite
        3) Speak from the point of view of the person applying for a job, based on their CV and narrative
        4) Make responses short, just a few sentences (5 max), unless you are specifically asked to expand further in which case you can make it longer
        
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

    # Collect input from user
    if input_mode == 'Text':
        prompt = st.chat_input("Thank you for reaching out about my job application. What would you like to know about me?")
        if prompt is not None:
            collect_next_user_input(client, prompt)
    elif input_mode == 'Voice':
        # Start the WebRTC audio capture

        ctx = webrtc_streamer(
            key="mic",
            mode=WebRtcMode.SENDONLY,
            audio_receiver_size=256,
            video_processor_factory=None,  # No video
            media_stream_constraints={
                "video": False,
                "audio": True
            }
        )

        # Button appears once WebRTC is running
        if ctx.state.playing:
            st.info("Connection ready. Click the button when you're done speaking.")

            if st.button("🎧 Transcribe Audio"):
                ctx.state.playing = False
                
                audio_frames = ctx.audio_receiver.get_frames(timeout=3)  # 3 second wait

                if not audio_frames:
                    st.warning("No audio received. Try again.")
                else:
                    # Combine audio and save as .wav
                    audio_data = b"".join([f.to_ndarray().tobytes() for f in audio_frames])
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                        with wave.open(f.name, "wb") as wf:
                            wf.setnchannels(1)
                            wf.setsampwidth(2)  # 16-bit audio
                            wf.setframerate(48000)
                            wf.writeframes(audio_data)
                        audio_path = f.name

                    # Transcribe with Whisper
                    with open(audio_path, "rb") as audio_file:
                        transcript = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file
                        )
                       # st.success("Transcription complete:")
                       # st.write(transcript.text)

                        prompt = transcript.text
                        collect_next_user_input(client, prompt)



def collect_next_user_input(client, prompt):
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