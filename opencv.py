import cv2
import math
from sklearn import neighbors
import os
import os.path
import pickle
from PIL import Image, ImageDraw
import face_recognition
import numpy as np

def predict(X_frame, knn_clf=None, model_path=None, distance_threshold=0.5):
    if knn_clf is None and model_path is None:
        raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")

    # Load a trained KNN model (if one was passed in)
    if knn_clf is None:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)

    X_face_locations = face_recognition.face_locations(X_frame)

    # If no faces are found in the image, return an empty result.
    if len(X_face_locations) == 0:
        return []

    # Find encodings for faces in the test image
    faces_encodings = face_recognition.face_encodings(X_frame, known_face_locations=X_face_locations)

    # Use the KNN model to find the best matches for the test face
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]

    # Predict classes and remove classifications that aren't within the threshold
    return knn_clf.predict(faces_encodings)[0] if are_matches else "Unknown"

if __name__ == "__main__":
    #camera = picamera.PiCamera()
    #camera.resolution = (320, 240)
    #output = np.empty((240, 320, 3), dtype=np.uint8)
    cap = cv2.VideoCapture(0)
    while True:
        #camera.capture(output, format="rgb")
        ret, frame = cap.read()
        img = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        predictions = predict(img, model_path="files/facemodel.clf")
        print(predictions)
        cv2.imshow('camera', frame)
        if ord('q') == cv2.waitKey(10):
          cap.release()
          cv2.destroyAllWindows()
          exit(0)
