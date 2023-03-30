from tkinter import *
from PIL import ImageTk, Image

def impoAIVM():
    import AIVM
    
def impoAIVB():
    import AIVB

root = Tk()
img = Image.open('./photo/backgroundImage.jpg')
bg = ImageTk.PhotoImage(img)

Img1 = Image.open('./photo/AIVB.png')
Img2 = Image.open('./photo/AIVM.png')

AIVMImg = ImageTk.PhotoImage(Img2)
AIVBImg = ImageTk.PhotoImage(Img1)

width = 1024
height = 576

wi = root.winfo_screenwidth()
he = root.winfo_screenheight()
root.geometry('%dx%d+%d+%d' % (width, height, wi/2-width/2, he/2-height/2))
root.title = "SETIVB"
root.resizable(False, False)

label = Label(root, image = bg)
label.place(x = -2, y = -2)

btn1 = Button(root, image = AIVMImg, command = impoAIVM, border = 0,borderwidth=0)
btn2 = Button(root, image = AIVBImg, command = impoAIVB, border = 0,borderwidth=0)
btn1.place(relx = 0.5, rely = 0.5, y = -25, anchor = CENTER)
btn2.place(relx = 0.5, rely = 0.5, y = 25,  anchor = CENTER)

root.mainloop()