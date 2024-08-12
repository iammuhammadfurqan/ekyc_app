import streamlit as st
from PIL import Image
import numpy as np
import easyocr
import pandas as pd
import base64
import re
from datetime import datetime, timedelta
from database import connect, record_exists, insert_record

def process_image(image):
    reader = easyocr.Reader(['en'], gpu=False)
    img_np = np.array(image)
    result = reader.readtext(img_np)

    extracted_data = {
        "Name": None,
        "Father Name": None,
        "Gender": None,
        "Country of Stay": "Pakistan",
        "Identity Number": None,
        "Date of Birth": None,
        "Date of Issue": None,
        "Date of Expiry": None
    }

    for i, detection in enumerate(result):
        text = detection[1].strip()
        if "name" in text.lower() and not "father" in text.lower():
            extracted_data["Name"] = result[i+1][1].strip() if i+1 < len(result) else None
        elif "father" in text.lower():
            extracted_data["Father Name"] = result[i+1][1].strip() if i+1 < len(result) else None
        elif text.lower() in ["m", "f"]:
            extracted_data["Gender"] = text.upper()
        elif re.match(r'\d{5}-\d{7}-\d', text):
            extracted_data["Identity Number"] = text
        elif re.match(r'\d{2}\.\d{2}\.\d{4}', text):
            if extracted_data["Date of Birth"] is None:
                extracted_data["Date of Birth"] = text
            elif extracted_data["Date of Issue"] is None:
                extracted_data["Date of Issue"] = text

    if extracted_data["Date of Issue"] and not extracted_data["Date of Expiry"]:
        try:
            date_of_issue = datetime.strptime(extracted_data["Date of Issue"], "%d.%m.%Y")
            date_of_expiry = date_of_issue.replace(year=date_of_issue.year + 10)
            extracted_data["Date of Expiry"] = date_of_expiry.strftime("%d.%m.%Y")
        except ValueError:
            pass

    return extracted_data

def display_table(extracted_data):
    fields = ["Name", "Father Name", "Gender", "Country of Stay", "Identity Number", "Date of Birth", "Date of Issue", "Date of Expiry"]
    values = [extracted_data[field] if extracted_data[field] else "" for field in fields]
    df = pd.DataFrame(list(zip(fields, values)), columns=['Field', 'Value'])
    st.dataframe(df)

def get_csv_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="extracted_data.csv">Download CSV File</a>'
    return href

def data_extraction_page():
    st.title('ID Card Text Extraction and Storage')

    uploaded_file = st.file_uploader("Upload an image of your ID card", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        extracted_data = process_image(image)
        display_table(extracted_data)

        connection = connect()
        if connection:
            identity_number = extracted_data["Identity Number"]
            if not record_exists(connection, identity_number):
                insert_record(connection, extracted_data)
                st.success("Data inserted into database.")
            else:
                st.warning("Data already exists in the database.")
            st.markdown(get_csv_download_link(pd.DataFrame(list(extracted_data.items()), columns=['Field', 'Value'])), unsafe_allow_html=True)
            connection.close()
        else:
            st.error("Database connection failed. Check your credentials and database settings.")
