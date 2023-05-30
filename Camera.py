# -*- coding: utf-8 -*-

import cv2
import tkinter as tk
from tkinter import ttk
import sys
from PIL import Image, ImageTk
from pygrabber.dshow_graph import FilterGraph

is_selected = False

class CameraApp:
    selected_webcam_index = None
    webcam_name = None

    def __init__(self):
        self.selected_webcam = None
        self.is_running = True
        
    def get_available_cameras(self):
        # Get list of all available cameras
        devices = FilterGraph().get_input_devices()
        global arr
        arr = []
        for index, device_name in enumerate(devices):
            arr.append(device_name)
        
        return arr

    def start_webcam(self):
        # Create a tkinter window to display camera selection

        root = tk.Tk()
        root.title("Select Camera")
        root.geometry("300x200")

        # Get the list of available cameras and display them in a dropdown menu
        camera_list = self.get_available_cameras()
        camera_selected = tk.StringVar(root)
        camera_selected.set(camera_list[0])
        camera_dropdown = ttk.Combobox(root, textvariable=camera_selected, values=camera_list)
        camera_dropdown.pack(pady=10)
        
        global is_selected
        is_selected = False

        # When user clicks 'OK', set selected camera and close the window
        def on_closing():
            root.quit()

        def show_webcam():
            
            cap = cv2.VideoCapture(arr.index(camera_selected.get()))

            window = tk.Toplevel()
            window.title("이 웹캠이 맞습니까?")

            def select_camera():
                global is_selected
                is_selected = True
                self.selected_webcam = camera_selected.get()
                cap.release()
                window.destroy()
                root.destroy()
                
            def restart():
                global is_selected
                is_selected = True
                cap.release()
                window.destroy()
                
            global is_selected
            is_selected = False

            label = tk.Label(window)
            label.pack()
            OKbutton = tk.Button(window, text="선택하기", command=select_camera)
            OKbutton.pack()
            NObutton = tk.Button(window, text="다시 선택", command=restart)
            NObutton.pack()

            def update_frame():
                    _, frame = cap.read()
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame)
                    photo = ImageTk.PhotoImage(image)
                    label.configure(image=photo)
                    label.image = photo
                    window.update()
            
            while is_selected is False:
                update_frame()
                
            window.mainloop()
            cap.release()

        ok_button = tk.Button(root, text="확인", command=show_webcam)
        ok_button.pack()

        img = tk.Image("photo", file="SETIVB.png")
        root.tk.call('wm', 'iconphoto', root._w, img)
        root.iconphoto(True, img)
        root.title('SETIVB')

        root.wm_protocol("WM_DELETE_WINDOW", on_closing)

        root.mainloop()

        if self.selected_webcam is None:
            sys.exit(0)
        else:
            selected_webcam_index = arr.index(self.selected_webcam)
            return selected_webcam_index

def main():
    global selected_webcam_index

    app = CameraApp()
    selected_webcam_index = app.start_webcam()
    cap = cv2.VideoCapture(selected_webcam_index)

    while True:
        ret, frame = cap.read()
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
