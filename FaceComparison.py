import streamlit as st
from PIL import Image
from compare_faces import compare_faces
import tempfile

def face_comparison_page():
    st.title("ID Card and Face Verification")

    id_card_image = st.file_uploader("Upload your ID card image", type=["jpg", "jpeg", "png"])
    face_image = st.file_uploader("Upload your face image", type=["jpg", "jpeg", "png"])

    if id_card_image and face_image:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as id_temp:
            id_temp.write(id_card_image.read())
            id_temp_path = id_temp.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as face_temp:
            face_temp.write(face_image.read())
            face_temp_path = face_temp.name

        result = compare_faces(id_temp_path, face_temp_path)
        st.write(result)
