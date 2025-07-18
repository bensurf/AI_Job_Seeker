import streamlit as st
import scoring_utils
import prompts

st.title("AI Scoring of Cardiology applicants")
st.write('''Instructions: Fill out the form below to score the applicants. You can either score a specific number of applications or all applications by entering -1 in the number of applications field. The prompts are pre-filled with default values, but you can modify them as needed.
This demo includes the 9 UCLA applicants.''')

def process_input(number_of_applications,prompt_rating,prompt_phrases,prompt_attributes):
    scoring_prompt_rating = prompts.scoring_prompt_rating
    scoring_prompt_rating[1] = prompt_rating
    scoring_prompt_rating = " ".join(scoring_prompt_rating)
    scoring_prompt_phrases = prompts.scoring_prompt_phrases
    scoring_prompt_phrases[1] = prompt_phrases
    scoring_prompt_phrases = " ".join(scoring_prompt_phrases)
    scoring_prompt_attributes = prompts.scoring_prompt_attributes
    scoring_prompt_attributes[1] = prompt_attributes
    scoring_prompt_attributes = " ".join(scoring_prompt_attributes)

    number_to_score = int(number_of_applications)
    if number_to_score == -1:
        number_to_score = None
    if number_to_score >= 9:
        number_to_score = 9
    if number_to_score <= 0:
        number_to_score = 0

    
    progress_bar = st.progress(0, width = 3)
    status_text = st.empty()

    df = scoring_utils.score_many_applicants(number_to_score=number_to_score,
                                             prompt_rating=scoring_prompt_rating,
                                             prompt_phrases=scoring_prompt_phrases, 
                                             prompt_attributes=scoring_prompt_attributes,
                                             progress_bar=progress_bar,
                                             status_text=status_text)
    
    progress_bar.progress(100)
    status_text.text("Scoring completed. You can now download the results.")

    st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="data.csv",
        mime="text/csv",
        icon=":material/download:",
    )

number_of_applications = st.text_input("Enter the number of applications you would like to process (for all, put -1):", value = "3")
prompt_rating = st.text_area("Prompt for the PDLOR rating:", value = prompts.scoring_prompt_rating[1], height = 350)
prompt_phrases = st.text_area("Prompt for the LOR notes:", value = prompts.scoring_prompt_phrases[1], height = 350)
prompt_attributes = st.text_area("Prompt for the star diagram scores (for attributes: Likeable, Work ethic, Intelligent, Clincial abilities, Leader, Team player, Teacher, Self-starter in research)", value = prompts.scoring_prompt_attributes[1], height = 200)

if st.button("Submit"):
    result = process_input(number_of_applications,prompt_rating,prompt_phrases,prompt_attributes)
