import numpy as np
from typing import List
from werkzeug.datastructures import FileStorage
from utils.db_handler import get_all_faculty
from face_utils import get_embedding_from_image
from scipy.spatial.distance import cosine

# Set similarity threshold for FaceNet embeddings (tunable based on testing)
THRESHOLD = 0.6

def l2_normalize(x):
    """
    Normalize a vector using L2 norm.
    """
    return x / np.linalg.norm(x)

def cosine_similarity(embedding1, embedding2):
    """
    Compute cosine similarity between two embeddings.
    """
    return 1 - cosine(embedding1, embedding2)

def recognize_faces(image_file: FileStorage) -> List[str]:
    """
    Recognize faculty from the uploaded image using FaceNet embeddings.
    Returns a list of recognized faculty IDs.
    """
    if not image_file or not image_file.filename:
        print("⚠️ No file uploaded.")
        return []

    try:
        uploaded_embedding = get_embedding_from_image(image_file)

        if uploaded_embedding is None or not isinstance(uploaded_embedding, np.ndarray):
            print("⚠️ No face or invalid embedding from uploaded image.")
            return []

        uploaded_embedding = l2_normalize(uploaded_embedding)
        print("🔬 Uploaded embedding shape:", uploaded_embedding.shape)

        all_faculty = get_all_faculty()
        recognized_ids = []

        for faculty in all_faculty:
            if not faculty.get('face_embedding'):
                continue

            stored_embedding = np.frombuffer(faculty['face_embedding'], dtype=np.float32)

            if stored_embedding.shape != uploaded_embedding.shape:
                print(f"⚠️ Shape mismatch for {faculty['faculty_id']} – skipping.")
                continue

            stored_embedding = l2_normalize(stored_embedding)
            similarity = cosine_similarity(uploaded_embedding, stored_embedding)

            print(f"🔍 Comparing with {faculty['name']} (ID: {faculty['faculty_id']}) – Similarity: {similarity:.4f}")

            if similarity >= THRESHOLD:
                print(f"✅ Match found: {faculty['faculty_id']}")
                recognized_ids.append(faculty['faculty_id'])

        print(f"🎯 Final recognized faculty IDs: {recognized_ids}")
        print("📸 Raw uploaded embedding (first 5):", uploaded_embedding[:5])
        return recognized_ids

    except Exception as e:
        print(f"❌ Error in face recognition: {str(e)}")
        return []