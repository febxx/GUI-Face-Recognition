import os
import re
import json
import pickle
import requests
import tkinter as tk
import face_recognition
from datetime import datetime
from tkinter import messagebox
from config import *

def check_model():
    get_model = requests.get(API_URL+'/model').json()

    if get_model.get('error'):
        messagebox.showerror(APP_NAME, get_model.get('error'))
    else:
        update_model(get_model)

def update_model(res):
    file = open('data.json', 'r')
    data = json.load(file)
    if data.get('model') != res.get('updated'):
        model = requests.get(BASE_URL+res['nama'])
        open(NAMA_MODEL, 'wb').write(model.content)
        data['model'] = res.get('updated')
        write = open('data.json', 'w')
        json.dump(data, write, indent=4)
        write.close()
        print("Renew model from database")
        messagebox.showinfo(APP_NAME, "Berhasil memperbarui model")
    else:
        messagebox.showinfo(APP_NAME, "Model sudah versi terbaru")
    file.close()

def check_user(name, now):
    file = open('data.json', 'r')
    data = json.load(file)
    file.close()
    user = data['pegawai'].get(name)
    if user:
        date = datetime.strptime(user['tanggal'], '%Y-%m-%d').date()
        exit_time = datetime.strptime(user['shift'], '%H:%M:%S').time()
        if date == now.date() and now.time() < exit_time:
            return user
        elif now.time() >= exit_time and user['pulang'] != "00:00:00":
            return user
        else:
            return False
    else:
        return False

def add_user(res):
    file = open('data.json', 'r')
    data = json.load(file)
    user = {res['nama']: res}
    data['pegawai'].update(user)
    write = open('data.json', 'w')
    json.dump(data, write, indent=4)
    write.close()
    file.close()

def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

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
