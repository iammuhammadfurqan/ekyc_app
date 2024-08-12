from deepface import DeepFace

def compare_faces(id_card_image_path, face_image_path):
    result = DeepFace.verify(id_card_image_path, face_image_path)
    return "Faces Match" if result["verified"] else "Faces doesn't Match"
