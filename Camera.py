import cv2
import tkinter as tk
from tkinter import ttk
import sys

class CameraApp:
    selected_webcam_index = None
    def __init__(self):
        self.selected_webcam = None
    
    def get_available_cameras(self):
        # Get list of all available cameras
        index = 0
        arr = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.read()[0]:
                arr.append("Camera " + str(index))
            cap.release()
            index += 1
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

        # When user clicks 'OK', set selected camera and close the window
        def select_camera():
            self.selected_webcam = camera_selected.get()
            root.destroy()
        
        def on_closing():
            root.quit()

        ok_button = tk.Button(root, text="OK", command=select_camera)
        ok_button.pack()
        root.wm_protocol("WM_DELETE_WINDOW", on_closing)

        root.mainloop()

        if self.selected_webcam is None:
            sys.exit(0)
        else:
            selected_webcam_index = int(self.selected_webcam.split()[-1])
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
