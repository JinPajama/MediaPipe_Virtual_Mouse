import subprocess
import tkinter as tk
import threading
import os

def infin_process(stop_event):
    while not stop_event.is_set():
        subprocess.run(['python', 'AIVM.py'])
        subprocess.run(['python', 'AIVB.py'])

def start_SETIVB():
    t = threading.Thread(target=infin_process, args=(stop_event,))
    t.start()
    return t

def stop_program(t, stop_event):
    open("stop.txt", "w").close()
    stop_event.set()
    t.join()
    os.remove("stop.txt")
    root.quit()

stop_event = threading.Event()
t = start_SETIVB()

root = tk.Tk()
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
w = 160
h = 90 
x = ws - 88 - (w/2)
y = hs - 100 - (h/2)

button = tk.Button(root, text="종료", command=lambda: stop_program(t, stop_event))
button.pack()

root.geometry('%dx%d+%d+%d' % (w, h, x, y))
img = tk.Image("photo", file="./photo/SETIVB.png")
root.tk.call('wm', 'iconphoto', root._w, img)
root.iconphoto(True, img)
root.title('SETIVB')

root.mainloop()