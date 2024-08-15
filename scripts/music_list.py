from tkinter import Listbox, Misc, END
from scripts.player import Music

class MusicList(Listbox):

    def __init__(self, master: Misc, bg, fg, font, x, y, w, h, anchor, func) -> None:

        super().__init__(master, bg=bg, fg=fg, font=font)
        self.place(x=x, y=y, width=w, height=h, anchor=anchor)
        self.bind('<Double-Button>', func)

    def Highlight(self, index) -> None:

        self.select_clear(0, END)
        self.activate(index)
        self.select_set(index)

    def Update(self, musicList: list) -> None:

        self.delete(0, END)

        for music in musicList:
            
            self.insert(END, music.title)
