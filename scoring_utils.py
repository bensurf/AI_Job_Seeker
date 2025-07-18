import csv
import os
import pandas as pd
import numpy as np
import json
from tqdm.auto import tqdm
from datetime import datetime

import pdfplumber
from PyPDF2 import PdfReader, PdfWriter

from openai import AzureOpenAI

#from pdf2image import convert_from_path
import pytesseract
import fitz  # PyMuPDF
from PIL import Image

import prompts

GLOBAL = {}
GLOBAL["model"] = 'GPT-4o'
GLOBAL["client"] = AzureOpenAI(
    api_key = "c06e4252191f4ee296fa32f47c5efae4",  
    api_version = "2024-02-01",
    azure_endpoint = "https://scripps-openai-01.openai.azure.com/"
    )
base_dir = os.path.dirname(os.path.abspath(__file__))


def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text


def extract_text_from_pdf_with_OCR(pdf_path):
    extracted_text = ""

    #Get number of pages
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)

    
    # Iterate through pages and extract each page as an image
    pdf_document = fitz.open(pdf_path)
    images = []
    for page_number in range(num_pages):
        page = pdf_document[page_number]
        pix = page.get_pixmap()
        if pix.alpha:  # Check if the image has an alpha channel
            pix = fitz.Pixmap(pix, 0)  # Remove the alpha channel
         # Convert pix.samples (raw image data) to a Pillow Image
        im = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(im)
        #output_file = f"{output_folder}/page_{page_number + 1}.png"
        #pix.save(output_file)
        #print(f"Saved: {output_file}")

    # Perform OCR using pytesseract
    pytesseract.pytesseract.tesseract_cmd = r"C:\Users\282339\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
    for im in images:
        ocr_text = pytesseract.pytesseract.image_to_string(im)
        extracted_text += ocr_text + "\n"

    return extracted_text



def extract_bookmarks_and_split(pdf_path, output_dir):
    # Read the PDF file
    reader = PdfReader(pdf_path)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Extract bookmarks (outline)
    try:
        bookmarks = reader.outline
    except Exception as e:
        print("Error: Unable to extract bookmarks from the PDF.")
        print(f"Details: {e}")
        return

    # Process each bookmark and extract title and page number
    bookmark_info_list = []
    for bookmark in bookmarks:
        if isinstance(bookmark, dict):  # Ensure it's a valid bookmark
            title = bookmark.get('/Title')  # Bookmark title
            page_number = reader.get_destination_page_number(bookmark)

            if title and page_number is not None:
                bookmark_info_list.append(
                    {
                        "title" : title,
                        "page number" : page_number
                    }
                )
            else:
                print("Skipping bookmark due to missing title or page number.")


    # Split the PDF
    num_bookmarks = len(bookmark_info_list)
    for i,info in enumerate(bookmark_info_list):
        title = info["title"]
        start_page_number = info["page number"]
        if i+1 == num_bookmarks:
            end_page_number = len(reader.pages)
        else:
            end_page_number = bookmark_info_list[i+1]["page number"]
        
        # Create a writer object for this section
        writer = PdfWriter()
        
        # Add pages starting from the bookmark's page
        # Assuming the bookmark represents the start of a section
        for page in range(start_page_number, end_page_number):
            writer.add_page(reader.pages[page])

        # Create a sanitized filename for the bookmark title
        sanitized_title = "".join(c if c.isalnum() else "_" for c in title)

        # Write the section to a new PDF file
        output_file = os.path.join(output_dir, f"{sanitized_title}.pdf")
        try:
            with open(output_file, "wb") as output_pdf:
                writer.write(output_pdf)
        except Exception as e:
            print(f"Error writing file: {output_file}")
            print(f"Exception: {e}")

        # Write as a text file
        #pdf_text = extract_text_from_pdf(output_file)
        pdf_text = extract_text_from_pdf_with_OCR(output_file)
        output_txt_file = os.path.join(output_dir, f"{sanitized_title}.txt")
        with open(output_txt_file, "w", encoding="utf-8") as txt_file:
            txt_file.write(pdf_text)

        #print(f"Saved section '{title}' to: {output_file}")

def get_pdf_names_in_folder(applications_path):
    dir_list = os.listdir(applications_path)
    pdf_names = []
    for name in dir_list:
        if name[-4:] == ".pdf":
            pdf_names.append(name)
    return pdf_names

def get_applicant_data_from_pdf_names(pdf_names):
    application_data_list = []

    for id, applicant_pdf_name in enumerate(pdf_names):
        
        applicant_pdf_name = applicant_pdf_name.split(".pdf")[0]
        
        split_string = applicant_pdf_name.split("_")
        applicant_last_name = split_string[0][:-1]
        applicant_first_initial = split_string[0][-1:]
        applicant_AAMC_ID = split_string[1]

        applicant_dict = {
            "id": str(id),
            "Application PDF name": applicant_pdf_name,
            "Last name": applicant_last_name,
            "First name": applicant_first_initial,
            "AAMC ID": applicant_AAMC_ID
        }
        applicant_dict["Folder name"] = applicant_dict["id"]+"_"+applicant_dict["Last name"]+"_"+applicant_dict["First name"]

        application_data_list.append(applicant_dict)
    
    return application_data_list

def split_pdfs_into_indivial_LORs(application_data_list, original_folder_path, output_path):
    for applicant in application_data_list:
        applicant_pdf_name = applicant["Application PDF name"]

        folder_name = applicant["Folder name"]

        pdf_path = original_folder_path+applicant_pdf_name+".pdf"  # Path to the input PDF file
        print(pdf_path)
        output_dir = output_path+folder_name+"\\"  # Directory to save the split sections
        #output_dir = applications_path+applicant_pdf_name+"\\"  # Directory to save the split sections
        extract_bookmarks_and_split(pdf_path, output_dir)

        with open(output_dir+"applicant_info.txt", "w") as file:
            json.dump(applicant, file)
    

def get_application_info_list():
    directory_path = os.path.join(base_dir, "LORs")
    folders = [f for f in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, f))]
    print(folders)
    application_info_list = []
    for f in folders:
        file_name = os.path.join(directory_path,f)
        file_name = os.path.join(file_name,"applicant_info.txt")
        #file_name = directory_path + f + "\\applicant_info.txt"
        with open(file_name, "r") as file:
            json_string = file.read()
            data = json.loads(json_string)
        application_info_list.append(data)
    return application_info_list

def score_file(folder_path, text_file_name, score_prompt):
    #with open(folder_path + text_file_name, 'r', encoding="utf-8") as file:
    with open(os.path.join(folder_path,text_file_name), 'r', encoding="utf-8") as file:
        text = file.read()

    openai_query = GLOBAL["client"].chat.completions.create(
        model = GLOBAL["model"],
        messages = [{"role" : "user",
                    "content" : score_prompt+text}]
    )
    return openai_query.choices[0].message.content

def score_applicant(applicant, prompt_rating = None, prompt_phrases = None, prompt_attributes = None):
    #folder_name = "LORs\\"+applicant["Folder name"]+"\\"
    folder_name = os.path.join(base_dir, "LORs")
    folder_name = os.path.join(folder_name,applicant["Folder name"])

    # Get list of text file names
    dir_list = os.listdir(folder_name)
    file_names = []
    for name in dir_list:
        if name[-4:] == ".txt" and name != "applicant_info.txt":
            file_names.append(name)

    ratings_dict = {}
    for file_name in file_names:
        # Determine if PD or not
        if file_name[0:2] == "PD":
            reviewer_name = "(PD) "
        else:
            reviewer_name = ""

        #Extract the reviewer last name
        last_name = file_name.split("___")[1]
        last_name = last_name.split(".")[0]
        last_name = last_name.replace("_"," ")
        #last_name = last_name.split("__")[0]
        #last_name = last_name.split("_")[-1]
        #last_name = last_name.split(".")[0]

        reviewer_name = reviewer_name + last_name

        #Score the applicant
        ratings_dict[reviewer_name] = {
                "Rating": score_file(folder_name, file_name, prompt_rating),
                "Phrases": score_file(folder_name, file_name, prompt_phrases),
                "Attributes": score_file(folder_name, file_name, prompt_attributes)
            }

    return ratings_dict


def score_many_applicants(number_to_score = None, prompt_rating = None, prompt_phrases = None, prompt_attributes = None, progress_bar = None, status_text = None):
    application_info_list = get_application_info_list()
    if number_to_score is None:
        number_to_score = len(application_info_list)
    application_info_list = application_info_list[0:number_to_score]
    
    
    #for applicant in tqdm(application_info_list):
    #    ratings = score_applicant(applicant, prompt_rating, prompt_phrases, prompt_attributes)
    #    applicant['Ratings'] = ratings

    ## Create a dataframe
    output_df = pd.DataFrame(columns=['AAMC ID', 'Applicant Name', 'PDLOR Rating', 'PDLOR Rating sentence', 'LOR Notes', 'Likable', 'Work ethic', 'Intelligent', 'Clinical abilities', 'Leader', 'Team player', 'Teacher', 'Self-starter in research'])

    i = 0
    for applicant in tqdm(application_info_list):
        progress_bar.progress(int(i / number_to_score * 100))
        status_text.text(f"Processing application {i+1} of {number_to_score}....")
        i+=1

        aamc_id = applicant['AAMC ID']
        applicant_name = applicant["Last name"]+", "+applicant["First name"]
        
        print(applicant["Last name"])
        print("")
        ratings = score_applicant(applicant, prompt_rating, prompt_phrases, prompt_attributes)
        #ratings = applicant["Ratings"]
        

        lor_notes = ""

        attributes = {
            'Likeable' : 0,
            'Work ethic' : 0,
            'Intelligent' : 0,
            'Clincial abilities' : 0,
            'Leader' : 0,
            'Team player' : 0,
            'Teacher' : 0,
            'Self-starter in research' : 0,
        }
        
        for name in ratings.keys():
            print(name)
            print("")
            print(ratings[name])
            print("")
            print("")
            print("")

            if name[0:4] == '(PD)':
                pdlor_rating = str.split(str.split(ratings[name]['Rating'], "\"Rating\"")[1], "\"")[1]
                pdlor_full_sentence = str.split(str.split(ratings[name]['Rating'], "\"Full sentence\"")[1], "\"")[1]
                
            lor_notes += name+": "+ratings[name]['Phrases']+"\n\n"

            for att in attributes.keys():
                #print(att)
                rating_of_attribute = str.split(str.split(ratings[name]['Attributes'],att)[1],"\n")[0]
                #print(rating_of_attribute)
                if "YES" in rating_of_attribute:
                    attributes[att] += 1
                elif "NO" in rating_of_attribute:
                    1
                else:
                    #print("can't find the rating, bruh")
                    1
                
        print("")
        print("-----------------------------")
        print("")

        output_df.loc[len(output_df)] = [aamc_id, applicant_name, pdlor_rating, pdlor_full_sentence, lor_notes] + list(attributes.values())
    
    #output_df.to_csv("Applicant_Ratings.csv")
    return output_df