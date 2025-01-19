from tkinter import *

class Link(Tk):
    def __init__(self):
        super().__init__()
        self.title("Link")
        self.geometry("400x300")
        self.resizable(False, False)
        self.config(bg="black")
        
if __name__ == "__main__":
    link = Link()
    link.mainloop()