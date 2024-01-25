from tkinter import Canvas
from PIL import ImageTk, Image

class CanvasButton:

    def __init__(self, canvas: Canvas, x, y, w, h, imagePath, command):

        self.canvas, self.command = canvas, command
        self.x, self.y = canvas.canvasx(x), canvas.canvasy(y) # Convert window to canvas coords.
        self.size = (w, h)

        self.SetImage(imagePath)

    def Enable(self):

        self.canvas.tag_bind(self.object, "<Button-1>", lambda event: self.command())

    def Disable(self):

        def _():pass

        self.canvas.tag_bind(self.object, "<Button-1>", lambda event: _())

    def SetImage(self, path):

        self.imagePath = path
        self.image = ImageTk.PhotoImage(Image.open(self.imagePath).resize(self.size))

        self.object = self.canvas.create_image(self.x, self.y, anchor='nw', image=self.image)
        self.canvas.tag_bind(self.object, "<Button-1>", lambda event: self.command())
