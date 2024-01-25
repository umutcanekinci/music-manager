#region Importing Packages

from scripts.database import Database
from tkinter import Tk, Event, Label, Button, Frame, Entry, Listbox, BOTH, END, filedialog, PhotoImage, Canvas
from ctypes import windll
from PIL import Image, ImageTk
from os import walk, rename, path
import pygame
from pytube import YouTube 
from scripts.settings import *
from scripts.canvas_button import CanvasButton
import requests
from io import BytesIO
import eyed3 # to get photo
from mutagen.id3 import ID3, APIC

#from stagger import read_tag, id3

#endregion

def DownloadMP3(url: str, output_path) -> None:
    
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first() # extract only audio 

    file_name = yt.title
    
    if path.isfile(output_path+"/"+file_name+".mp3"):

        i=1
        while True:

            if not path.isfile(output_path+"/"+file_name+" ("+str(i)+").mp3"):

                break
            
            i += 1

        file_name += f" ({i})"

    # download the file 
    video.download(output_path, file_name+".mp3") 
    
    # result of success 
    print(file_name + " has been successfully downloaded in "+output_path)

def GetMetadata(path):

    audiofile = eyed3.load(path)

    if audiofile.tag:
        
        # Extract artist and track name from the MP3 metadata
        artist = audiofile.tag.artist
        track_name = audiofile.tag.title

        return artist, track_name
    
    else:

        return None, None


#region stuffs
    
GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080

def set_appwindow(root) -> None:
    hwnd = windll.user32.GetParent(root.winfo_id())
    style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
    style = style & ~WS_EX_TOOLWINDOW
    style = style | WS_EX_APPWINDOW
    res = windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
    # re-assert the new window style
    root.withdraw()
    root.after(10, root.deiconify)

class Grip:

    ''' Makes a window dragable. '''
    def __init__ (self, parent, disable=None, releasecmd=None) -> None:

        self.parent = parent
        self.root = parent.winfo_toplevel()

        self.disable = disable

        if type(disable) == 'str':

            self.disable = disable.lower()

        self.releaseCMD = releasecmd

        self.parent.bind('<Button-1>', self.relative_position)
        self.parent.bind('<ButtonRelease-1>', self.drag_unbind)

    def relative_position (self, event) -> None:

        cx, cy = self.parent.winfo_pointerxy()
        geo = self.root.geometry().split("+")
        self.oriX, self.oriY = int(geo[1]), int(geo[2])
        self.relX = cx - self.oriX
        self.relY = cy - self.oriY

        self.parent.bind('<Motion>', self.drag_wid)

    def drag_wid (self, event) -> None:

        cx, cy = self.parent.winfo_pointerxy()
        d = self.disable
        x = cx - self.relX
        y = cy - self.relY

        if d == 'x':

            x = self.oriX

        elif d == 'y':

            y = self.oriY

        self.root.geometry('+%i+%i' % (x, y))

    def drag_unbind (self, event) -> None:

        self.parent.unbind('<Motion>')
        
        if self.releaseCMD != None :

            self.releaseCMD()

#endregion

class Application(Tk):

    def __init__(self) -> None:

        #region Library Initialization

        super().__init__()
        pygame.init()
        pygame.mixer.init()

        #endregion

        #region Window Initialization

        self.SetWindowTitle(TITLE)
        self.SetSize(SIZE)
        self.CenterWindow()
        self.MakeUnresizable()
        self.MakeBorderless()
        self.ShowInTaskBar()

        #endregion

        #region Main Frame

        self.mainFrame = Frame(bg="grey", width= self.width, height=self.height)
        self.mainFrame.pack_propagate(0)
        self.mainFrame.pack(fill=BOTH, expand=1)

        #endregion

        #region Top Frame

        topFrame = Frame(self.mainFrame, bg="#505050")
        topFrame.place(x=0, y=0, anchor="nw", width=self.width, height=40)
        Grip(topFrame)

        Label(topFrame, bg="#505050", fg='white', font=("Comic Sans MS", 15), text=TITLE).pack()
        Button(topFrame, text="X", bg="#FF6666", fg="white", command=self.Exit).place(x=self.width-75, y=0, anchor="nw", width=75, height=40)

        #endregion

        #region Music Frame

        self.img = ImageTk.PhotoImage(Image.open("./images/sample.jpg").resize((64, 64)))
        
        self.musicName = Label(self.mainFrame, text="Music Name", font=("Comic Sans MS", 11))
        self.musicImage = Label(self.mainFrame, image=self.img)

        self.musicImage.place(x=20, y=60, anchor="nw")
        self.musicName.place(x=90, y=60, anchor="nw")

        #endregion

        #region FolderFrame
        
        self.folderFrame = Frame(self.mainFrame, bg="#505050")
        self.folderFrame.place(x=20, y=220,  anchor="nw", width=self.width-40, height=50)
        
        #endregion

        #region Music List

        self.musicList = Listbox(self.mainFrame, bg='white', fg='green', font=("Comic Sans MS", 12))
        self.musicList.place(x=20, y=270, anchor="nw", width=self.width - 40, height=self.height - 400)
        self.musicList.bind('<Double-Button>', self.DoubleClickMusic)
        
        #endregion

        #region Buttons

        self.buttonCanvas = Canvas(self.mainFrame, bg="grey", width=400, height=40, bd=0, highlightthickness=0, relief="ridge")
        self.buttonCanvas.place(x=20, y=140)

        self.mixButton = CanvasButton(self.buttonCanvas, 0, 0, 32, 32, "./images/mix.png", self.Mix)
        self.previousButton = CanvasButton(self.buttonCanvas, 40, 0, 32, 32, "./images/previous.png", self.Previous)
        self.resumePauseButton = CanvasButton(self.buttonCanvas, 80, 0, 32, 32, "./images/resume.png", self.ResumePause)
        self.nextButton = CanvasButton(self.buttonCanvas, 120, 0, 32, 32, "./images/next.png",  self.Next)
        self.repeatButton = CanvasButton(self.buttonCanvas, 160, 0, 32, 32, "./images/repeat.png", self.Repeat)

        #endregion

        #region Process

        self.processFrame = Frame(self.mainFrame, bg='grey')
        self.processFrame.place(x=20, y=180, anchor="nw", width=340, height=30)

        self.timer = Label(self.processFrame, text="00:00", font=("Comic Sans MS", 11))
        self.musicLength = Label(self.processFrame, text="03:00", font=("Comic Sans MS", 11))
        
        #self.process = 

        self.timer.place(x=0, y=0, anchor="nw")
        self.musicLength.place(x=295, y=0, anchor="nw")
        
        #endregion

        #region Download

        Label(self.mainFrame, text="Download from YouTube", font=("Comic Sans MS", 13)).place(x=20, y=self.height - 120, anchor="nw")

        self.urlEntry = Entry(self.mainFrame)
        self.urlEntry.place(x=20, y=self.height - 70, anchor="nw", width=self.width - 160, height=30)

        self.downloadButton = Button(self.mainFrame, bg='orange', fg='white', font=("Comic Sans MS", 12), text='DOWNLOAD', command=self.Download)
        self.downloadButton.place(x=self.width - 120, y=self.height - 70, anchor="nw", width=100, height=30)

        #endregion

        #region Database Initialazation, Getting and Applying Datas

        self.database = Database('database')
        if not self.database.Connect(): self.Exit()
        self.CreateTables()
        self.ApplySettings(self.GetSettings())
        self.LoadContent()

        #endregion

        self.bind("<KeyRelease>", self.HandleKeys)


    def GetMusicPhoto(self, path):

        print(path)
        
        audiofile = ID3(path)
        print(audiofile)
        if 'APIC:Cover' in audiofile:
        # Extract album art data from ID3 tag using mutagen
            image_data = audiofile['APIC:Cover'].data
        
        else:
            return

        """

        # WAY 2

        audiofile = eyed3.load(path)


        if audiofile.tag and audiofile.tag.frame_set.get('APIC'):
            print("a")
            # Extract album art data from ID3 tag
            album_art_data = audiofile.tag.frame_set['APIC'][0].image

            image_data = album_art_data

        else:
            return
        """

        """  
        # WAY 1
        
        artist, track_name = GetMetadata(path)

        if artist and track_name:

            print(f"Artist: {artist}")
            print(f"Track Name: {track_name}")

        else:

            print("Metadata not found.")

        api_key = 'c5ef518a3f64c01a13e4591d8d1d1214'
        url = f'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={api_key}&artist={artist}&track={track_name}&format=json'

        try:

            response = requests.get(url)
            data = response.json()

            # Extract album image URL from the API response
            image_url = data['track']['album']['image'][2]['#text']

            # Download the image
            image_data = requests.get(image_url).content

        except Exception as e:

            print(f"Error: {e}")
        """

        self.DisplayMusicImage(image_data)

    def DisplayMusicImage(self, image_data):

        # Open the image using Pillow
        image = Image.open(BytesIO(image_data))

        # Resize the image if necessary
        image = image.resize((64, 64))

        # Convert the image to Tkinter format
        tk_image = ImageTk.PhotoImage(image)

        # Update the label with the new image
        self.musicImage.config(image=tk_image)
        self.musicImage.image = tk_image

    def HandleKeys(self, event):

        if event.keysym == 'F5':

            self.RefreshFolder()

    def Download(self):

        DownloadMP3(self.urlEntry.get(), self.folders[self.selectedFolder])
        self.RefreshFolder()

    def CreateTables(self) -> None:

        """
        
        This function create necessary tables if they aren't exist

        """
   
        self.database.Execute('CREATE TABLE IF NOT EXISTS folders (id INTEGER PRIMARY KEY, path TEXT NOT NULL)')
        self.database.Execute('CREATE TABLE IF NOT EXISTS musics (id INTEGER PRIMARY KEY, folder_id INTEGER NOT NULL, name TEXT NOT NULL)')
        self.database.Execute('CREATE TABLE IF NOT EXISTS settings (volume INT NOT NULL, last_folder INT, last_music INT, mix INT, repeat INT)')
        self.database.Commit()

    def GetSettings(self) -> any:

        """
        
        This function gets a record from settings table in database.

        If there is no settings table this will create a settings table with default values and get them.
        
        """

        return self.database.Execute('SELECT * FROM settings').fetchone()

    def SetDefaultSettings(self) -> None:

        self.database.Execute('DELETE FROM settings')
        self.database.Execute(f"INSERT INTO settings (volume, mix, repeat) VALUES ('{DEFAULT_VOLUME}', 0, 0)")
        self.database.Commit()

    def ApplySettings(self, settings) -> None:

        if not settings:

            self.SetDefaultSettings()
            self.ApplySettings(self.GetSettings())

        else:
            
            self.volume, self.lastFolder, self.lastMusic, self.mix, self.repeat = settings

            self.mixButton.SetImage("./images/plus.png" if self.mix else "./images/mix.png")
            self.repeatButton.SetImage("./images/plus.png" if self.repeat else "./images/repeat.png")

    def LoadContent(self) -> None:

        self.GetFolders()
        self.GetMusics()
        self.RenderFolderBar()

        if self.folders:

            if not self.lastMusic == None:

                self.OpenFolder(self.lastFolder)
                self.OpenMusic(self.lastMusic)
                self.Pause()

            else:

                if not hasattr(self, 'selectedFolder'):

                    self.OpenFolder(list(self.folders.keys())[0])

                else:

                    self.OpenFolder(self.selectedFolder)

            self.downloadButton["state"] = "normal"

        else:

            self.warningLabel = Label(self.mainFrame, text='Please add a folder or drag a music to play it !')
            self.warningLabel.place(anchor='nw', x=80, y=370)
            self.downloadButton["state"] = "disabled"

    def GetFolders(self) -> None:

        self.folders = self.database.Execute('SELECT * FROM folders').fetchall()
        self.folders = {folder[0]: (folder[1].replace('\\', '/')) for folder in self.folders}
        
    def GetMusics(self) -> None:

        self.musics = {key: {} for key in self.folders.keys()}
        result = self.database.Execute('SELECT * FROM musics').fetchall()

        for music in result:

            self.musics[music[1]][music[0]] = music[2].replace('\\', '/')
            
    def RenderFolderBar(self) -> None:

        self.GetFolders()
        
        self.folderButtons = {}
        
        for i, folder in enumerate(self.folders.items()):
        
            self.folderButtons[folder[0]] = Button(self.folderFrame, bg='orange', fg='white', font=("Comic Sans MS", 12), text=folder[1].split('/')[-1], command=lambda t=folder[0]: self.OpenFolder(t))
            self.folderButtons[folder[0]].place(x=i*100, y=0, anchor="nw", width=100, height=50)

        self.plusImage = PhotoImage(file='images/plus.png')
        self.addFolderButton = Button(self.folderFrame, image=self.plusImage, bg='green', command=self.AddFolder)
        self.addFolderButton.place(x=len(self.folders)*100, y=0, anchor="nw", width=60, height=50)

    def OpenFolder(self, id) -> None:

        if hasattr(self, 'selectedFolder'): self.folderButtons[self.selectedFolder].config(bg='orange')
        self.folderButtons[id].config(bg='green')

        self.selectedFolder = id
        self.musicList.delete(0, END)
        for musicName in self.musics[self.selectedFolder].values():
            
            self.musicList.insert(END, musicName.removesuffix(".mp3"))

    def ScanMusics(self, path, folderID):

        for root, dirs, files in walk(path):
            for fileName in files:

                if fileName.endswith(".mp3"):

                    fileName = fileName.replace("'", "''") # bug with ' char
                    self.database.Execute(f"INSERT INTO musics (folder_id, name) VALUES ({folderID}, '{fileName}')")

        self.database.Commit()

    def RefreshFolder(self):

        # Firstly delete records from database
        self.database.Execute(f"DELETE FROM musics WHERE folder_id={self.selectedFolder}")
        self.database.Commit()

        # Then scan musics and insert them to table
        self.ScanMusics(self.folders[self.selectedFolder], self.selectedFolder)

        self.LoadContent()

    def AddFolder(self) -> None:

        path = filedialog.askdirectory()

        if path:

            alreadyExist = False
            
            for folderPath in self.folders.values():

                if folderPath == path:

                    alreadyExist = True
                    break

            if not alreadyExist:

                self.database.Execute(f"INSERT INTO folders (path) VALUES ('{path}')")
                self.database.Commit()
    
                folderID = self.database.Execute(f"SELECT id FROM folders WHERE path='{path}'").fetchone()[0]

                self.ScanMusics(path, folderID)
                
                self.LoadContent()
                self.OpenFolder(folderID)

                if hasattr(self, 'warningLabel'):
                    
                    self.warningLabel.pack_forget() # condition error

            else:

                print("fuck your self! this already exists")

        else:

            print("fuck your self!")

    def OpenMusic(self, index) -> None:
        
        self.index = index
        self.lastFolder = self.selectedFolder

        fileName = list(self.musics[self.selectedFolder].values())[index]
        folderPath = self.folders[self.selectedFolder]
        filePath = folderPath + "/" + fileName

        pygame.mixer.music.load(filePath)
        pygame.mixer.music.play(-1 if self.repeat else 0)
        
        self.Resume()
        self.musicName.config(text = fileName.removesuffix('.mp3'))
        self.GetMusicPhoto(filePath)
        self.musicList.select_clear(0, END)
        self.musicList.select_set(index)

    def DoubleClickMusic(self, event: Event) -> None:

        widget = event.widget
        index = widget.curselection()[0]
        self.OpenMusic(index)

    #region Button Functions

    def Mix(self) -> None:

        self.mix = not self.mix
        self.mixButton.SetImage("./images/plus.png" if self.mix else "./images/mix.png")

    def Previous(self) -> None:

        if hasattr(self, 'index') and self.index > 0:
            
            self.OpenMusic(self.index - 1)

    def Resume(self) -> None:

        pygame.mixer.music.unpause()
        self.resumePauseButton.SetImage("./images/pause.png")
        self.isMusicPlaying = True

    def Pause(self) -> None:

        pygame.mixer.music.pause()
        self.resumePauseButton.SetImage("./images/resume.png")
        self.isMusicPlaying = False

    def ResumePause(self) -> None:
        
        if hasattr(self, 'index'):

            if self.isMusicPlaying:

                self.Pause()

            else:

                self.Resume()

    def Next(self) -> None:

        if hasattr(self, 'index') and self.index < len(self.musics[self.selectedFolder]) - 1:

            self.OpenMusic(self.index + 1)

    def Repeat(self) -> None:

        self.repeat = not self.repeat
        self.repeatButton.SetImage("./images/plus.png" if self.repeat else "./images/repeat.png")

    #endregion
    
    #region Tkinter Functions
        
    def Start(self) -> None:

        self.mainloop()

    def CenterWindow(self) -> None:

        self.update_idletasks()
        width = self.winfo_width()
        frm_width = self.winfo_rootx() - self.winfo_x()
        win_width = width + 2 * frm_width
        height = self.winfo_height()
        titlebar_height = self.winfo_rooty() - self.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = self.winfo_screenwidth() // 2 - win_width // 2
        y = self.winfo_screenheight() // 2 - win_height // 2
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        self.deiconify()

    def ShowInTaskBar(self) -> None:

        self.after(10, set_appwindow, self)

    def SetWindowTitle(self, text: str) -> None:

        self.wm_title(text)

    def SetSize(self, size) -> None:

        self.size = self.width, self.height = size
        self.geometry(str(self.width) + "x" + str(self.height))

    def MakeUnresizable(self) -> None:

        self.resizable(0, 0)

    def MakeBorderless(self) -> None:

        self.overrideredirect(True)

    #endregion

    def Exit(self) -> None:

        try:

            if hasattr(self, 'index') and self.index:

                self.database.Execute(f"UPDATE settings SET volume={self.volume}, last_folder={self.lastFolder}, last_music={self.index}, mix={1 if self.mix else 0}, repeat={1 if self.repeat else 0}")

            else:

                self.database.Execute(f"UPDATE settings SET volume={self.volume}, mix={1 if self.mix else 0}, repeat={1 if self.repeat else 0}")

            self.database.Commit()
            self.database.Disconnect()
        
        except:
            
            pass

        self.destroy()
