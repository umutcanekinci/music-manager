from tkinter import Canvas
from PIL import ImageTk, Image

class CanvasButton:

    def __init__(self, canvas: Canvas, x, y, w, h, imagePath, onClick) -> None:

        self.canvas, self.onClick = canvas, onClick
        self.x, self.y = canvas.canvasx(x), canvas.canvasy(y) # Convert window to canvas coords.
        self.size = (w, h)

        self.SetImage(imagePath)

    def SetImage(self, path) -> None:

        self.imagePath = path
        self.image = ImageTk.PhotoImage(Image.open(self.imagePath).resize(self.size))

        self.object = self.canvas.create_image(self.x, self.y, anchor='nw', image=self.image)
        self.canvas.tag_bind(self.object, "<Button-1>", lambda e: self.onClick())

    def SetPosition(self, x, y):

        self.canvas.moveto(self.object, self.canvas.canvasx(0), self.canvas.canvasy(0))