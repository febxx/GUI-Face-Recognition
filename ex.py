import cv2
import imutils
import requests
import tkinter as tk
import face_recognition
from datetime import datetime
from PIL import Image, ImageTk

BASE_URL = 'http://localhost:8000'
NAMA_MODEL = 'files/facemodel.clf'

root = tk.Tk()
root.geometry("1080x720")
root.iconbitmap('files/icon.ico')
root.title("Tampilan App")
root.resizable(width=False, height=False)

# background_img = tk.PhotoImage(file="oke2.png")
# background = tk.Label(root, image=background_img).place(x=0, y=0, relwidth=1, relheight=1)

right_frame = tk.LabelFrame(root, width=352, height=510, bg="#33A67B")
right_frame.place(x=698, y=106)
label_right_frame = tk.Label(right_frame, text="Data User", bg="#33A67B", font=("times new roman", 14, "bold"))
label_right_frame.place(x=120, y=5)

video = cv2.VideoCapture(0)
btn_color = "#066056"

def video_stream():
    ret, frame = video.read()
    if ret == True:
        resize_frame = imutils.resize(frame, width=676)
        resize_frame = cv2.flip(resize_frame, 1)
        faces = face_recognition.face_locations(resize_frame)
        if len(faces) == 1:
            img = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            suhu = 35.7
            now = datetime.now().time().strftime('%H:%M')
            from utils import predict
            predictions = predict(img, model_path=NAMA_MODEL)
            print(predictions)
            if predictions and predictions[0][0] != 'unknown':
                data = {'suhu': suhu, 'jam': now, 'pegawai': predictions[0][0]}
                pegawai = requests.post(f'{BASE_URL}/api/model/', json=data, data=data).json()
            cv2.imwrite("frame.jpg", img)
            files = {'gambar':  open('frame.jpg', 'rb')}
            data = {'suhu': suhu, 'jam': now, 'pegawai': predictions[0][0]}
            predict = requests.post(f'{BASE_URL}/api/model/', json=data, files=files, data=data).json()
            print(predict)
            # nama = predict.get('nama')
            # (top, right, bottom, left) = faces[0]
            # cv2.rectangle(resize_frame, (left, top), (right, bottom), (0, 0, 255), 2)
            # font = cv2.FONT_HERSHEY_DUPLEX
            # cv2.putText(resize_frame, nama, (50, 50), font, 1.0, (255, 255, 255), 1)
        
        frame = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2RGB)
        # frame = cv2.flip(frame, 1)
        tk_frame = Image.fromarray(frame)
        tk_frame = ImageTk.PhotoImage(image=tk_frame)
        video_frame.configure(image=tk_frame)
        video_frame.image = tk_frame
        video_frame.after(10, video_stream)

def Quit():
    global video
    video_frame.place_forget()
    video.release()

def get_model():
    res_model = requests.get(BASE_URL+'/api/model').json()
    res_file = requests.get(BASE_URL+res_model['nama'])
    open(NAMA_MODEL, 'wb').write(res_file.content)
    return

# tombol
button = tk.Button(root, text="Mulai", bg=btn_color, relief="flat", cursor="hand2", command=video_stream, width=12, height=2, font=("times new roman", 14, "bold"))
button.place(x=210, y=639)

button2 = tk.Button(root, text="Kembali", bg=btn_color, relief="flat", cursor="hand2", command=quit, width=12, height=2, font=("times new roman", 14, "bold"))
button2.place(x=792, y=639)

video_frame = tk.Label(root, bg="black")
video_frame.place(x=30, y=105)

# get_model()
video_stream()

root.mainloop()