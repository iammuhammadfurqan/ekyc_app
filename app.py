import streamlit as st
from Home import home_page
from DataExtraction import data_extraction_page
from FaceComparison import face_comparison_page

PAGES = {
    "Home": home_page,
    "Data Extraction": data_extraction_page,
    "Face Comparison": face_comparison_page
}

st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

page = PAGES[selection]
page()
