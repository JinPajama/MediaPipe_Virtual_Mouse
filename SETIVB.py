# -*- coding: utf-8 -*-

import subprocess
import tkinter as tk
import threading
import os
import keyboard
from Camera import CameraApp

def infin_process(stop_event):
    while not stop_event.is_set():
        #subprocess.run('AIVM.exe')
        #subprocess.run('AIVB.exe')
        subprocess.run(['python', 'AIVM.py'])
        subprocess.run(['python', 'AIVB.py'])

def start_SETIVB():
    t = threading.Thread(target=infin_process, args=(stop_event,))
    t.start()
    return t

def stop_program(t, stop_event):
    open("stop.txt", "w").close()
    subprocess.call(['attrib','+H','stop.txt'])
    stop_event.set()
    t.join()
    os.remove("stop.txt")
    os.remove("index.txt")
    root.quit()

if os.path.exists("index.txt"):
    os.remove("index.txt")

if os.path.exists("stop.txt"):
    os.remove("stop.txt")

if CameraApp.selected_webcam_index is None:
    app = CameraApp()
    CameraApp.selected_webcam_index = app.start_webcam()

    with open("index.txt", "w") as f1:
        f1.write(str(CameraApp.selected_webcam_index))
    subprocess.call(['attrib','+H','index.txt'])

def do_nothing():
        pass
    
stop_event = threading.Event()
t = start_SETIVB()

root = tk.Tk()
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
w = 160
h = 90 
x = ws - 88 - (w/2)
y = hs - 100 - (h/2)

button = tk.Button(root, text="종료",width = 10, height = 10, command=lambda: stop_program(t, stop_event))
button.pack()

root.geometry('%dx%d+%d+%d' % (w, h, x, y))
img = tk.Image("photo", file="SETIVB.png")
root.tk.call('wm', 'iconphoto', root._w, img)
root.iconphoto(True, img)
root.title('SETIVB')

root.protocol("WM_DELETE_WINDOW", do_nothing)

root.mainloop()