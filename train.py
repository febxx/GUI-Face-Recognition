import cv2
import imutils
import tkinter as tk
from PIL import Image, ImageTk

APP_COLOR = '#5e72e4'
BUTTON_FONT = ("Arial", 12)
LABEL_FONT = ("Arial", 16, "bold")
TITLE_FONT = ("Arial", 28, "bold")

root = tk.Tk()
root.geometry("1080x720")
root.iconbitmap('files/icon.ico')
root.title("Tampilan App")
root.resizable(width=False, height=False)
root.configure(bg=APP_COLOR)

video = cv2.VideoCapture(0)

tk.Label(root, text="Tambah dan Train Data", bg=APP_COLOR, font=TITLE_FONT).place(x=350, y=30)

left_frame = tk.LabelFrame(root, width=352, height=580, bg="white", relief="flat")
left_frame.place(x=25, y=105)
tk.Label(left_frame, text="List Pegawai", bg="white", font=LABEL_FONT).place(x=120, y=5)

right_frame = tk.LabelFrame(root, bg="white", width=680, height=510, relief="flat")
right_frame.place(x=383, y=105)
canvas = tk.Label(root, bg="white")
canvas.place(x=383, y=105)

def video_stream():
    ret, frame = video.read()
    if ret == True:
        resize_frame = imutils.resize(frame, width=676)
        frame = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2RGB)
        # frame = cv2.flip(frame, 1)
        tk_frame = Image.fromarray(frame)
        tk_frame = ImageTk.PhotoImage(image=tk_frame)
        canvas.configure(image=tk_frame)
        canvas.image = tk_frame
        canvas.after(10, video_stream)

def get_data():
    response = [{'id': 7, 'nip': '112128', 'nama': 'Obama', 'jabatan': 'Direktur Produksi', 'shift': '16:00:00'}, {'id': 8, 'nip': '9992088', 'nama': 'Rio Dumatubun', 'jabatan': 'Anggota', 'shift': '16:00:00'}, {'id': 9, 'nip': '9992088', 'nama': 'Messi', 'jabatan': 'Anggota', 'shift': '23:00:00'}]
    y = 20
    for data in response:
        y+=40
        tk.Button(left_frame, text=f"{data['nip']} {data['nama']}", font=BUTTON_FONT, relief="flat", bg=APP_COLOR, width=34, fg='white', anchor="w").place(x=20, y=y)

tk.Button(root, text="GET DATA", command=get_data, font=BUTTON_FONT, relief="solid", width=36, height=2).place(x=383, y=635)
tk.Button(root, text="START CAPTURE", command=video_stream, font=BUTTON_FONT, relief="solid", width=36, height=2).place(x=730, y=635)
tk.LabelFrame(root, width=1080, height=2, bg="black", relief="flat").place(x=0, y=0)
tk.LabelFrame(root, width=1080, height=2, bg="black", relief="flat").place(x=0, y=719)
tk.LabelFrame(root, width=2, height=720, bg="black", relief="flat").place(x=0, y=0)
tk.LabelFrame(root, width=2, height=720, bg="black", relief="flat").place(x=1080, y=0)

root.mainloop()