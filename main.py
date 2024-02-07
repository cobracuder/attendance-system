import os.path
import tkinter as tk
import cv2
import util
from PIL import Image, ImageTk
import face_recognition
import numpy as np
from datetime import datetime

path='dbd' #create a raw file and give the absolute or relative path of file 
images=[]
classnames=[]
mylist=os.listdir(path)
print(mylist)
for cl in mylist:
    curimg=cv2.imread(f'{path}/{cl}')
    images.append(curimg)
    classnames.append(os.path.splitext(cl)[0])
print(classnames)

def findEncoding(images):
    encodelist=[]
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodelist.append(encode)
    return encodelist
encodeListknown= findEncoding(images)
print('Encoding Complete')
class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")

        self.login_button_main=util.get_button(self.main_window,'Login','green',self.login)
        self.login_button_main.place(x=750,y=350)
        self.new_user_button_main = util.get_button(self.main_window,'Register New User','gray',self.register_new_user)
        self.new_user_button_main.place(x=750, y=400)
        self.webcam_label=util.get_img_label(self.main_window)
        self.webcam_label.place(x=10,y=0,width=700,height=500)
        self.add_webcam(self.webcam_label)
        self.db_dir='./dbd'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)



    def add_webcam(self,label):
        if 'cap' not in self.__dict__:
            self.cap=cv2.VideoCapture(0)
        self._label=label
        self.proces_webcam()


    def proces_webcam(self):
        ret,frame=self.cap.read()
        self.most_recent_capture_arr=frame
        img_=cv2.cvtColor(self.most_recent_capture_arr,cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil=Image.fromarray(img_)

        imgtk=ImageTk.PhotoImage(image=self.most_recent_capture_pil)

        self._label.imgtk= imgtk
        self._label.configure(image=imgtk)

        self._label.after(20,self.proces_webcam)
    def login(self):
        flag=1
        for i in range(10):
            flag=1
            success, img = self.cap.read()
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            # imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            facescurframe = face_recognition.face_locations(imgS)
            encodecurframe = face_recognition.face_encodings(imgS, facescurframe)

            for encodeFace, faceloc in zip(encodecurframe, facescurframe):
                matches = face_recognition.compare_faces(encodeListknown, encodeFace)
                facedis = face_recognition.face_distance(encodeListknown, encodeFace)
                print(facedis)

                matchIndex = np.argmin(facedis)

                if (matches)[matchIndex]:
                    flag=0
                    self.name = classnames[matchIndex].upper()
                    print(self.name)
                    y1, x1, y2, x2 = faceloc
                    y1, y2, x1, x2 = y1 * 4, y2 * 4, x1 * 4, x2 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
                    cv2.putText(img, self.name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

                    self.markattendance(self.name)

        if flag==0:
                util.msg_box("sucess","attendance of "+self.name.upper()+" marked sucessfully")

        else:
                util.msg_box("Error","face not recognize please register if you have not")





    def register_new_user(self):
        self.register_new_user_window= tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+370+120")
        self.accept_button=util.get_button(self.register_new_user_window,'Accept','green',self.accept_register_new_user)
        self.accept_button.place(x=750,y=350)
        self.try_again = util.get_button(self.register_new_user_window,'try again','red',self.try_again_register_new_user)
        self.try_again.place(x=750, y=400)
        self.capture_label=util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10,y=0,width=700,height=500)
        self.add_img_to_label(self.capture_label)
        self.entry_text=util.get_entry_text(self.register_new_user_window)
        self.entry_text.place(x=750,y=200)
        self.entery_text_label=util.get_text_label(self.register_new_user_window,"Please,\nEnter Name:")
        self.entery_text_label.place(x=750,y=100)

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self,label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)
        self.register_new_user_capture=self.most_recent_capture_arr.copy()

    def start(self):
        self.main_window.mainloop()

    def markattendance(self,name):
        with open('attendance.csv', 'r+') as f:
            self.myDatalist = f.readlines()
            self.namelist = []
            for line in self.myDatalist:
                self.entry = line.split(',')
                self.namelist.append(self.entry[0])
            if name not in self.namelist:
                now = datetime.now()
                dtstring = now.strftime('%H:%M:%S')
                f.writelines(f'\n{name},{dtstring}')




    def accept_register_new_user(self):
        name=self.entry_text.get(1.0,"end-1c")
        cv2.imwrite(os.path.join(self.db_dir,'{}.jpg'.format(name)),self.register_new_user_capture)
        util.msg_box('sucess',"User Register Succesfully with name :"+ name)
        self.register_new_user_window.destroy()

if __name__ == "__main__":
    app=App()
    app.start()
