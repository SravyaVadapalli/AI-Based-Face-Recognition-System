import cv2
import numpy as np
from keras_facenet import FaceNet
from keras.utils import img_to_array
from PIL import Image

# Load FaceNet model
face_net = FaceNet()

# Haar cascade for face detection
FACE_DETECTOR_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(FACE_DETECTOR_PATH)


def get_face_from_frame(frame) -> np.ndarray:
    """
    Detect the largest face in the frame and return the cropped face region.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    if len(faces) == 0:
        print("⚠️ No faces detected.")
        return None

    print(f"✅ Detected {len(faces)} face(s). Using the largest.")
    # Use the largest face detected
    x, y, w, h = sorted(faces, key=lambda b: b[2] * b[3], reverse=True)[0]
    return frame[y:y+h, x:x+w]


def preprocess_face(face_img):
    """
    Resize and normalize the face image for FaceNet.
    """
    face_img = cv2.resize(face_img, (160, 160))
    face_img = face_img.astype('float32')
    mean, std = face_img.mean(), face_img.std()
    face_img = (face_img - mean) / std
    return np.expand_dims(face_img, axis=0)


def l2_normalize(x):
    """
    Normalize a vector using L2 norm.
    """
    return x / np.linalg.norm(x)


def get_embedding_from_image(image) -> np.ndarray:
    """
    Extract face from an image and return FaceNet embedding.
    Accepts FileStorage, BytesIO, NumPy array, or PIL Image.
    """
    try:
        # Step 1: Convert to NumPy (BGR) regardless of input type
        if hasattr(image, 'read'):  # FileStorage or BytesIO
            image = Image.open(image).convert("RGB")
            image = np.array(image)[:, :, ::-1]  # Convert RGB to BGR
        elif isinstance(image, Image.Image):  # PIL image
            image = np.array(image.convert("RGB"))[:, :, ::-1]
        elif isinstance(image, np.ndarray):  # Already a NumPy array
            pass
        else:
            print("❌ Unsupported image type")
            return None

        # Step 2: Detect face
        face_img = get_face_from_frame(image)
        if face_img is None:
            print("⚠️ No face detected in the image.")
            return None

        # Step 3: Preprocess face and get embedding
        processed_face = preprocess_face(face_img)
        embedding = face_net.embeddings(processed_face)[0]
        return embedding

    except Exception as e:
        print(f"❌ Failed to process image: {e}")
        return None


def get_average_embedding_from_images(image_list) -> np.ndarray:
    """
    Accepts a list of images (PIL or np.ndarray), extracts L2-normalized face embeddings from each,
    and returns their average embedding.
    Skips images where no face is detected.
    """
    embeddings = []

    for idx, img in enumerate(image_list):
        if not isinstance(img, np.ndarray):
            img = np.array(img.convert('RGB'))

        embedding = get_embedding_from_image(img)
        if embedding is not None:
            embeddings.append(embedding)
        else:
            print(f"⚠️ Skipping image {idx+1}: no valid face detected.")

    if not embeddings:
        print("❌ No valid embeddings found.")
        return None

    return np.mean(embeddings, axis=0)


def get_embedding_from_camera() -> np.ndarray:
    """
    Capture face from webcam and return L2-normalized FaceNet embedding vector.
    Press 'c' to capture, 'q' to quit.
    """
    cap = cv2.VideoCapture(0)
    print("📸 Capturing face. Press 'c' to capture or 'q' to quit.")

    embedding = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display_frame = frame.copy()
        face_img = get_face_from_frame(frame)
        if face_img is not None:
            x, y, w, h = cv2.boundingRect(cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY))
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow("Face Capture", display_frame)

        key = cv2.waitKey(1)
        if key == ord('c') and face_img is not None:
            processed_face = preprocess_face(face_img)
            embedding = face_net.embeddings(processed_face)[0]
            embedding = l2_normalize(embedding)
            print("✅ Face captured and embedding generated.")
            break
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return embedding