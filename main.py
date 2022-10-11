import cv2
# import busio
# import board
import imutils
# import adafruit_amg88xx
from PIL import Image, ImageTk

from utils import *
from config import *
class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry(f"{w}x{h}")
        #self.attributes('-fullscreen', True)
        self.title(APP_NAME)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.frames = {}
        for F in (HomePage, PresensiPage, TrainPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=APP_COLOR)

        tk.LabelFrame(self, width=w*.25, height=h, bg="white", relief="flat").place(x=0, y=0)
        tk.LabelFrame(self, width=w*.75, height=h*.2, bg='white', relief="flat").place(x=w*.25+2, y=0)
        tk.Label(self, text="Aplikasi Sistem Presensi", bg='white', font=TITLE_FONT).place(x=300, y=h*.2/3)

        tk.Button(self, text="HOME", command=lambda: controller.show_frame("HomePage"), font=BUTTON_FONT, relief="flat", bg=APP_COLOR, width=15).place(x=50, y=150)
        tk.Button(self, text="PRESENSI", command=lambda: controller.show_frame("PresensiPage"), font=BUTTON_FONT, relief="flat", bg=APP_COLOR, width=15).place(x=50, y=200)
        tk.Button(self, text="TRAIN DATA", command=lambda: controller.show_frame("TrainPage"), font=BUTTON_FONT, relief="flat", bg=APP_COLOR, width=15).place(x=50, y=250)
        tk.Button(self, text="UPDATE MODEL", command=check_model, font=BUTTON_FONT, relief="flat", bg=APP_COLOR, width=15).place(x=50, y=300)
        tk.Button(self, text="QUIT", command=quit, font=BUTTON_FONT, relief="flat", width=15).place(x=50, y=650)

        tk.LabelFrame(self, width=w*.75, height=2, bg="black", relief="flat").place(x=w*.25+2, y=h*.2)
        tk.LabelFrame(self, width=2, height=h, bg="black", relief="flat").place(x=w*.25, y=0)

class PresensiPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=APP_COLOR)
        self.controller = controller

        tk.Label(self, text="Presensi Program", bg=APP_COLOR, font=TITLE_FONT).place(x=w*.4, y=30)
        self.left_frame = tk.LabelFrame(self, bg="white", width=672, height=503, relief="flat")
        self.left_frame.place(x=10, y=105)
        self.canvas = tk.Label(self, bg="white")
        self.canvas.place(x=10, y=105)

        self.right_frame = tk.LabelFrame(self, width=327, height=558, bg="white", relief="flat")
        self.right_frame.place(x=687, y=105)
        tk.Label(self.right_frame, text="Data User", bg="white", font=LABEL_FONT).place(x=120, y=5)

        tk.Button(self, text="Mulai", relief="flat", cursor="hand2", command=self.play, width=10, font=LABEL_FONT).place(x=280, y=626)
        tk.Button(self, text="< Kembali", relief="flat", cursor="hand2", command=self.back, font=BUTTON_FONT).place(x=25, y=25)

    def play(self):
        if hasattr(self, 'vid') and self.vid.opened():
            pass
        else:
            self.vid = VideoCapture()
            self.update_video()

    def back(self):
        try:
            self.vid.close()
        except:
            pass
        tk.Label(self.right_frame, fg="white", bg="white", font=TEXT_FONT, height=400, width=300).place(x=10, y=70)
        self.canvas.configure(image='')
        self.controller.show_frame("HomePage")

    def update_video(self):
        try:
            ret, frame = self.vid.get_frame()
            if ret:
                resize_frame = imutils.resize(frame, width=670)
                resize_frame = cv2.flip(resize_frame, 1)
                resize_frame = cv2.flip(resize_frame, 0)
                self.predict(resize_frame)
                self.image = ImageTk.PhotoImage(image=Image.fromarray(resize_frame))
                self.canvas.configure(image=self.image)
                self.canvas.image = self.image
            self.after(10, self.update_video)
        except:
            pass

    def predict(self, frame):
        face_detec = face_recognition.face_locations(frame)
        if len(face_detec) == 1:
            img = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            suhu = 35.7
            now = datetime.now()
            try:
                predictions = predict(img, model_path=NAMA_MODEL)
            except Exception as e:
                print(e)

            if predictions and predictions != 'Unknown':
                data = check_user(predictions, now)
                if data:
                    self.show_data(data)
                else:
                    data = {'suhu': suhu, 'jam': now, 'nama': predictions}
                    response = requests.post(f'{API_URL}/presensi/', data=data).json()
                    add_user(response)
                    self.show_data(response)
            else:
                self.show_data()
        else:
            self.show_data()

    def show_data(self, data=None):
        if data:
            tk.Label(self.right_frame, text=data['nip'], bg="white", font=TEXT_FONT).place(x=10, y=70)
            tk.Label(self.right_frame, text=data['nama'], bg="white", font=TEXT_FONT).place(x=10, y=100)
            tk.Label(self.right_frame, text=data['jabatan'], bg="white", font=TEXT_FONT).place(x=10, y=130)
            tk.Label(self.right_frame, text='Tanggal = ' +data['tanggal'], bg="white", font=TEXT_FONT).place(x=10, y=200)
            tk.Label(self.right_frame, text='Jam Masuk = ' +data['masuk'], bg="white", font=TEXT_FONT).place(x=10, y=230)
            tk.Label(self.right_frame, text='Jam Pulang = ' +data['pulang'], bg="white", font=TEXT_FONT).place(x=10, y=260)
            tk.Label(self.right_frame, text='Suhu = ' +data['suhu'], bg="white", font=TEXT_FONT).place(x=10, y=290)
            tk.Label(self.right_frame, text='Keterangan = ' +data['keterangan'], bg="white", font=TEXT_FONT).place(x=10, y=320)
        else:
            tk.Label(self.right_frame, fg="white", bg="white", font=TEXT_FONT, height=400, width=300).place(x=10, y=70)

class TrainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=APP_COLOR)
        self.controller = controller
        self.capture = False

        tk.Label(self, text="Tambah dan Train Data", bg=APP_COLOR, font=TITLE_FONT).place(x=350, y=30)
        self.left_frame = tk.LabelFrame(self, width=327, height=503, bg="white", relief="flat")
        self.left_frame.place(x=10, y=105)
        tk.Label(self.left_frame, text="List User", bg="white", font=LABEL_FONT).place(x=115, y=5)

        self.right_frame = tk.LabelFrame(self, bg="white", width=672, height=503, relief="flat")
        self.right_frame.place(x=342, y=105)
        self.canvas = tk.Label(self, bg="white")
        self.canvas.place(x=342, y=105)

        tk.Button(self, text="GET DATA", command=self.get_data, font=BUTTON_FONT, relief="solid", width=33, height=2).place(x=10, y=635)
        tk.Button(self, text="TRAIN MODEL", command=self.train, font=BUTTON_FONT, relief="solid", width=33, height=2).place(x=350, y=635)
        tk.Button(self, text="START CAPTURE", command=self.start_capture, font=BUTTON_FONT, relief="solid", width=33, height=2).place(x=691, y=635)
        tk.Button(self, text="< Kembali", relief="flat", cursor="hand2", command=self.back, font=BUTTON_FONT).place(x=25, y=25)

        #tk.Button(self, text="QUIT", command=quit, font=BUTTON_FONT, relief="flat", width=15).place(x=50, y=650)

    def get_data(self):
        try:
            response = requests.get(f'{API_URL}/pegawai/').json()
        except:
            return messagebox.showerror(APP_NAME, 'API tidak merespons')
        if response:
            tk.Label(self.left_frame, width=352, height=450, bg="white", relief="flat").place(x=0, y=55)
            y = 20
            for data in response:
                y += 40
                tk.Button(self.left_frame, text=data['nama'], command=lambda id_=data['id'], nama=data['nama']: self.choose_data(id_, nama), font=BUTTON_FONT, relief="flat", bg=APP_COLOR, width=31, fg='white', anchor="w").place(x=10, y=y)
        else:
            tk.Label(self.left_frame, width=352, height=450, bg="white", relief="flat").place(x=0, y=55)
            tk.Label(self.left_frame, text="Tidak ada data", bg="white", font=BUTTON_FONT).place(x=120, y=55)

    def start_capture(self):
        if not hasattr(self, 'id'):
            return messagebox.showwarning(APP_NAME, 'Pilih data pegawai terlebih dahulu!')
        self.capture = True
        self.start_cap = datetime.now()

    def choose_data(self, id_, nama):
        self.id = id_
        self.nama = nama
        self.count = 1
        self.files = {}
        self.play()

    def play(self):
        if hasattr(self, 'vid') and self.vid.opened():
            pass
        else:
            self.vid = VideoCapture()
            self.update_video()

    def back(self):
        try:
            self.vid.close()
        except:
            pass
        tk.Label(self.left_frame, width=352, height=450, bg="white", relief="flat").place(x=0, y=55)
        self.canvas.configure(image='')
        self.controller.show_frame("HomePage")

    def post(self):
        for i in self.files:
            self.files[i] = open(self.files[i], 'rb')
        try:
            response = requests.post(f"{API_URL}/pegawai/{self.id}/", files=self.files).json()
        except:
            return messagebox.showerror(APP_NAME, 'API tidak merespons')
        messagebox.showinfo(APP_NAME, f"Berhasil memperbarui data {response['nama']}.")

    def train(self):
        yes = messagebox.askyesno(APP_NAME, f"Train Model baru?")
        if yes:
            try:
                response = requests.get(f'{API_URL}/model/train/').json()
                print(response)
            except:
                return messagebox.showerror(APP_NAME, 'API tidak merespons')
            update_model(response)

    def captured(self, frame, resize_frame):
        if self.capture:
            if self.count >= 6:
                self.count = 1
                self.capture = False
                send = messagebox.askokcancel(APP_NAME, message='Kirim ke sistem web untuk memperbarui data?')
                if send:
                    self.post()
            now_cap = datetime.now()
            diff = (now_cap - self.start_cap).seconds
            if countdown.get(diff) == '[O"]':
                face_detec = face_recognition.face_locations(frame)
                if len(face_detec) == 1:
                    filename = f"files/train/{self.id}_{self.nama}_{self.count}.jpg"
                    cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                    self.files[f"img{self.count}"] = filename
                    self.start_cap = datetime.now()
                    self.count += 1
                else:
                    return cv2.putText(resize_frame, 'NO FACE DETECTED', (70, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(resize_frame, countdown.get(diff), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2, cv2.LINE_AA)

    def update_video(self):
        try:
            ret, frame = self.vid.get_frame()
            if ret:
                resize_frame = imutils.resize(frame, width=670)
                resize_frame = cv2.flip(resize_frame, 1)
                self.captured(frame, resize_frame)
                self.image = ImageTk.PhotoImage(image=Image.fromarray(resize_frame))
                self.canvas.configure(image=self.image)
                self.canvas.image = self.image
            self.after(10, self.update_video)
        except:
            pass

class VideoCapture:
    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    def opened(self):
        if self.vid.isOpened():
            return True

    def close(self):
        if self.vid.isOpened():
            self.vid.release()

if __name__ == "__main__":
    app = App()
    app.mainloop()