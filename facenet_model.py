import os
import numpy as np
from keras.models import load_model
from keras.utils import img_to_array
import cv2

# Load FaceNet model
FACENET_MODEL_PATH = os.path.join('models', 'facenet_keras.h5')

# Load the model globally
facenet_model = load_model(FACENET_MODEL_PATH)

def preprocess_face(face_img, target_size=(160, 160)) -> np.ndarray:
    """
    Resize, normalize, and reshape a face image for FaceNet input.
    """
    face = cv2.resize(face_img, target_size)
    face = face.astype('float32') / 255.0
    face = np.expand_dims(face, axis=0)  # Add batch dimension
    return face

def get_face_embedding(face_img: np.ndarray) -> np.ndarray:
    """
    Given a face image (RGB), return its FaceNet embedding vector.
    """
    preprocessed = preprocess_face(face_img)
    embedding = facenet_model.predict(preprocessed)[0]  # Get the 128-d vector
    return embedding