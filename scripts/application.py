#region Importing Packages

from scripts.database import Database
from tkinter import Tk, ttk, Event, Label, Button, Frame, Entry, Listbox, BOTH, END, filedialog, PhotoImage, Canvas, StringVar
from ctypes import windll
from PIL import Image, ImageTk
from os import walk, rename, path
import pygame
from pytube import YouTube 
from scripts.settings import *

from time import strftime, gmtime

import requests
from io import BytesIO
import eyed3 # to get photo
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3


from scripts.player import Player
from scripts.music import GetMusicData, FilterMusicList
from scripts.canvas_button import CanvasButton
from scripts.music_list import MusicList

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

        self.player = Player()

        super().__init__()
        pygame.init()
        pygame.mixer.init()
        self.InitWindow()
        self.InitWidgets()
        self.InitDatabase()

        self.LoadContent()
        self.bind("<KeyRelease>", self.HandleKeys)

    #region Window Initialization
        
    def InitWindow(self):

        self.SetWindowTitle(TITLE)
        self.SetSize(SIZE)
        self.CenterWindow()
        self.MakeUnresizable()
        self.MakeBorderless()
        self.ShowInTaskBar()

    def Start(self) -> None:

        self.mainloop()

    def SetWindowTitle(self, text: str) -> None:

        self.wm_title(text)

    def SetSize(self, size: tuple) -> None:

        self.size = self.width, self.height = size
        self.geometry(str(self.width) + "x" + str(self.height))

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

    def MakeUnresizable(self) -> None:

        self.resizable(0, 0)

    def MakeBorderless(self) -> None:

        self.overrideredirect(True)

    def ShowInTaskBar(self) -> None:

        self.after(10, set_appwindow, self)

    #endregion
    
    def InitWidgets(self):

        self.mainFrame = Frame(bg="grey", width= self.width, height=self.height)
        self.mainFrame.pack_propagate(0)
        self.mainFrame.pack(fill=BOTH, expand=1)

        #region Top Frame

        topFrame = Frame(self.mainFrame, bg="#505050")
        topFrame.place(x=0, y=0, anchor="nw", width=self.width, height=40)
        Grip(topFrame)

        Label(topFrame, bg="#505050", fg='white', font=("Comic Sans MS", 15), text=TITLE).pack()
        Button(topFrame, text="X", bg="#FF6666", fg="white", command=self.Exit).place(x=self.width-75, y=0, anchor="nw", width=75, height=40)

        #endregion

        #region Music Frame

        self.musicFrame = Frame(self.mainFrame, bg="#505050")
        self.musicName = Label(self.musicFrame, text="Music Name", font=("Comic Sans MS", 11))
        self.musicImage = Label(self.musicFrame)

        self.musicFrame.place(x=20, y=50, anchor="nw", width=self.width-40, height=180)
        self.musicImage.place(x=0, y=30, anchor="nw")
        self.musicName.place(x=0, y=0, anchor="nw")

        #region Multimedia Buttons Frame

        self.buttonCanvas = Canvas(self.musicFrame, bg="#505050", width=200, height=40, bd=0, highlightthickness=0, relief="ridge")
        self.player.mixButton = CanvasButton(self.buttonCanvas, 0, 0, 32, 32, "./images/mix.png", self.Mix)
        self.previousButton = CanvasButton(self.buttonCanvas, 40, 0, 32, 32, "./images/previous.png", self.Previous)
        self.resumePauseButton = CanvasButton(self.buttonCanvas, 80, 0, 32, 32, "./images/resume.png", self.ResumePause)
        self.nextButton = CanvasButton(self.buttonCanvas, 120, 0, 32, 32, "./images/next.png",  self.Next)
        self.repeatButton = CanvasButton(self.buttonCanvas, 160, 0, 32, 32, "./images/repeat.png", self.Repeat)

        self.buttonCanvas.place(x=120, y=90)
        
        #endregion

        #region Slider Frame

        self.sliderFrame = Frame(self.musicFrame, bg='#505050')
        self.timer = Label(self.sliderFrame, text="00:00", font=("Comic Sans MS", 11))
        self.slider = ttk.Scale(self.sliderFrame, from_=0, to=100, orient="horizontal", value=0, command=self.Slide, length=250)
        self.sliderLabel = Label(self.mainFrame, text="00:00")
        self.musicLength = Label(self.sliderFrame, text="00:00", font=("Comic Sans MS", 11))

        self.sliderFrame.place(x=0, y=145, anchor="nw", width=360, height=30)
        self.timer.place(x=0, y=0, anchor="nw")
        self.slider.place(x=55, y=0, anchor="nw")
        self.sliderLabel.place(anchor="nw")
        self.musicLength.place(x=315, y=0, anchor="nw")
        
        #endregion

        #endregion

        #region Folder Frame
        
        self.keyword = StringVar()
        self.keyword.trace("w", self.Search)

        self.folderFrame = Frame(self.mainFrame, bg="#505050")
        self.folderNavBarFrame = Frame(self.folderFrame, bg="#505050")        
        self.searchEntry = Entry(self.folderFrame, bg="#505050", fg="orange", textvariable=self.keyword)
        self.musicList = MusicList(self.folderFrame, 'white', 'green', ("Comic Sans MS", 12), 0, 70, self.width-40, 325, "nw", self.DoubleClickMusic)
        self.folderFrame.place(x=20, y=240, anchor="nw", width=self.width-40, height=375)
        self.folderNavBarFrame.place(x=0, y=0, anchor="nw", width=self.width-40, height=50)
        self.searchEntry.place(x=0, y=50, width=self.width-40, height=20)

        #endregion

        #region Download Frame

        self.downloadFrame = Frame(self.mainFrame, bg="#505050")

        Label(self.downloadFrame, text="Download from YouTube", font=("Comic Sans MS", 11)).place(x=0, y=0, anchor="nw")
        self.urlEntry = Entry(self.downloadFrame)
        self.downloadButton = Button(self.downloadFrame, bg='orange', fg='white', font=("Comic Sans MS", 10), text='DOWNLOAD', command=self.Download)
        
        self.downloadFrame.place(x=20, y=635, anchor="nw", width=self.width-40, height=80)
        self.urlEntry.place(x=0, y=35, anchor="nw", width=self.width - 160, height=30)
        self.downloadButton.place(x=255, y=35, anchor="nw", width=100, height=30)

        #endregion

        Label(self.mainFrame, text="Developed by Umutcan Ekinci", font=("Comic Sans MS", 9), bg="#505050", fg="white").place(x=120, y=self.height-25, anchor="nw")

    #region Database Initialization

    def InitDatabase(self):

        self.database = Database('database')
        if not self.database.Connect(): self.Exit()
        self.CreateTables()
        self.ApplySettings(self.GetSettings())

    def CreateTables(self) -> None:

        """
        
        This function creates necessary tables if they aren't exist

        """
   
        self.database.Execute('CREATE TABLE IF NOT EXISTS folders (id INTEGER PRIMARY KEY, path TEXT NOT NULL)')
        self.database.Execute('CREATE TABLE IF NOT EXISTS musics (id INTEGER PRIMARY KEY, folder_id INTEGER NOT NULL, name TEXT NOT NULL)')
        self.database.Execute('CREATE TABLE IF NOT EXISTS settings (volume INT NOT NULL, last_folder INT, last_music INT, mix INT, repeat INT)')
        self.database.Commit()

    def GetSettings(self) -> list:

        """
        
        This function returns a settings record from database.

        """

        return self.database.Execute('SELECT * FROM settings').fetchone()

    def GetFolders(self) -> list:

        """
        
        This function returns all folder records from database.

        """

        return self.database.Execute('SELECT * FROM folders').fetchall()

    def GetMusics(self) -> list:

        """
        
        This function returns all music records from database.

        """

        return self.database.Execute('SELECT * FROM musics').fetchall()

    def SetDefaultSettings(self) -> None:

        """
        
        This function deletes records if there is any record in settings table and inserts a new settings record with default values.
        
        """

        self.database.Execute('DELETE FROM settings')
        self.database.Execute(f"INSERT INTO settings (volume, mix, repeat) VALUES ('{DEFAULT_VOLUME}', 0, 0)")
        self.database.Commit()

    def ApplySettings(self, settings) -> None:

        """
        
        If there is no any settings record this function will insert a settings record with default values and get them.
        
        """

        if not settings:

            self.SetDefaultSettings()
            self.ApplySettings(self.GetSettings())

        else:
            
            self.volume, self.lastFolder, self.lastMusic, self.player.mix, self.repeat = settings

    #endregion
   
    def LoadContent(self) -> None:

        self.LoadFolders(self.GetFolders())
        self.RenderFolderBar()

        if self.player.folders:

            self.LoadMusics(self.GetMusics())
            self.OpenFolder(self.selectedFolder)
            if not self.lastMusic == None: self.OpenMusic(self.lastMusic, False)

        else:

            self.warningLabel = Label(self.mainFrame, text='Please add a folder or drag a music to play it !')
            self.warningLabel.place(anchor='nw', x=80, y=370)

        self.downloadButton["state"] = "normal" if self.selectedFolder else "disabled"
        self.UpdateButtonImages()

    def RenderFolderBar(self) -> None:

        self.GetFolders()
        
        self.folderButtons = {}
        
        for i, folder in enumerate(self.player.folders.values()):
        
            self.folderButtons[folder.id] = Button(self.folderNavBarFrame, bg='orange', fg='white', font=("Comic Sans MS", 12), text=folder.name, command=lambda t=folder.id: self.OpenFolder(t))
            self.folderButtons[folder.id].place(x=i*100, y=0, anchor="nw", width=100, height=50)

        self.plusImage = PhotoImage(file='images/plus.png')
        self.addFolderButton = Button(self.folderNavBarFrame, image=self.plusImage, bg='green', command=self.AddFolder)
        self.addFolderButton.place(x=len(self.player.folders)*100, y=0, anchor="nw", width=60, height=50)

    def Slide(self, value):

        return
        
    def UpdateTime(self, filePath, length):

        currentTime = int(pygame.mixer.music.get_pos() / 1000)
        sliderTime = int(self.slider.get())
        convertedCurrentTime = strftime('%M:%S', gmtime(currentTime))
        
        self.sliderLabel.config(text=f'Slider Position: {sliderTime}\nMusic Position: {currentTime}')

        if sliderTime + 1 == currentTime: # Slider isn't moved
            
            pass

        else: # Slider is moved
            
            pass
            #print("slider is moved")
            #currentTime = sliderTime
            #convertedCurrentTime = strftime('%M:%S', gmtime(currentTime))

            #self.Play(filePath, startValue=currentTime)
        
        self.timer.config(text=convertedCurrentTime)
        self.slider.set(currentTime)

        if sliderTime == length:

            return self.Next()

        self.timer.after(1000, lambda filePath=filePath, length=length:self.UpdateTime(filePath, length))

    def GetMusicPhoto(self, path):
        
        audiofile = ID3(path)
        if 'APIC' in audiofile:
        # Extract album art data from ID3 tag using mutagen
            image_data = BytesIO(audiofile['APIC:Cover'].data)
        
        else:

            image_data = "./images/default.jpg"

        self.DisplayMusicImage(image_data)

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

    def DisplayMusicImage(self, image_data):

        # Open the image using Pillow
        image = Image.open(image_data)

        # Resize the image if necessary
        image = image.resize((100, 100))

        # Convert the image to Tkinter format
        tk_image = ImageTk.PhotoImage(image)

        # Update the label with the new image
        self.musicImage.config(image=tk_image)
        self.musicImage.image = tk_image

    def HandleKeys(self, event):

        if event.keysym == 'F5':

            self.RefreshFolder()

    def Download(self):

        DownloadMP3(self.urlEntry.get(), self.player.folders[self.selectedFolder])
        self.RefreshFolder()

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
        self.ScanMusics(self.player.folders[self.selectedFolder], self.selectedFolder)

        self.LoadContent()

    def AddFolder(self) -> None:

        path = filedialog.askdirectory()

        if path:

            alreadyExist = False
            
            for folderPath in self.player.folders.values():

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

    def DeleteMusic(self, musicID):

        try:

            self.database.Execute(f'DELETE FROM musics WHERE id={musicID}')
            self.database.Commit()

        except:

            print('An unexpected error occured while trying to delete a music!')
            self.Exit()

    def UpdateButtonImages(self) -> None:

        self.player.mixButton.SetImage("./images/plus.png" if self.player.mix else "./images/mix.png")
        self.resumePauseButton.SetImage("./images/pause.png" if self.player.isPlaying else "./images/resume.png")
        self.repeatButton.SetImage("./images/plus.png" if self.player.repeat else "./images/repeat.png")

    def UpdateMusicFrame(self):

        music = self.player.lastMusic
        
        self.musicName.config(text = music.title)
        self.GetMusicPhoto(music.path)
        self.musicLength.config(text=music.convertedLength)
        self.slider.config(value=0, to=music.length)
        #self.UpdateTime(music.path, music.length)

    def OpenMusic(self, index) -> None:
        
        try:

            music = self.filteredMusics[index]
            self.player.OpenPlayList(self.filteredMusics, music)
            self.selectedFolder = music.folder.id

            self.UpdateMusicFrame()
            self.HighlightPlayingMusic()
            self.UpdateButtonImages()

        except:# Delete music if it is corrupted

            self.DeleteMusic(self.filteredMusics[index].id)
            self.LoadMusics(self.GetMusics())
            self.OpenFolder(self.selectedFolder)
            self.OpenMusic(index)
    
    def DoubleClickMusic(self, event: Event) -> None:

        widget = event.widget
        index = widget.curselection()[0]
        self.OpenMusic(index)

    def OpenFolder(self, id) -> None:

        # Highlight selected folder
        if self.selectedFolder: self.folderButtons[self.selectedFolder].config(bg='orange')
        self.folderButtons[id].config(bg='green')

        # Update selected folder
        self.selectedFolder = id
        self.musicList.Update(FilterMusicList(self.player.folders[id].musics, self.keyword.get()))
        self.HighlightPlayingMusic()

    def LoadFolders(self, folders) -> None:

        self.player.AddFolder(*folders)

        if self.player.folders:

            self.selectedFolder = self.lastFolder if self.lastFolder else list(self.player.folders.keys())[0]

        else:

            self.selectedFolder = None

    def LoadMusics(self, musics) -> None:

        self.player.AddMusic(*[(music[0], music[1], *GetMusicData(music[2], self.player.folders[music[1]])) for music in musics])
        self.filteredMusics = FilterMusicList(self.player.folders[self.selectedFolder].musics, self.keyword.get())

    def HighlightPlayingMusic(self) -> None:

        if self.player.lastMusic and self.player.lastMusic.title in self.musicList.get(0, END) and self.player.lastMusic.folder.id == self.selectedFolder:
            
            self.player.index = self.musicList.get(0, END).index(self.player.lastMusic.title)
            self.musicList.Highlight(self.player.index)
   
    def Search(self, *args):
        
        self.filteredMusics = FilterMusicList(self.player.folders[self.selectedFolder].musics, self.keyword.get())
        self.musicList.Update(self.filteredMusics)

        self.HighlightPlayingMusic()

    def ResumePause(self) -> None:
        
        self.player.ResumePause()
        self.UpdateButtonImages()

    def Repeat(self) -> None:

        self.player.Repeat()
        self.UpdateButtonImages()

    def Mix(self) -> None:

            self.player.Mix()
            self.UpdateButtonImages()

    def Next(self) -> None:

        self.player.Next()
        self.UpdateMusicFrame()
        self.HighlightPlayingMusic()

    def Previous(self) -> None:

        self.player.Previous()
        self.UpdateMusicFrame()
        self.HighlightPlayingMusic()

    #endregion
    
    def Exit(self) -> None:

        try:

            if self.player.index:

                self.database.Execute(f"UPDATE settings SET volume={self.volume}, last_folder={self.lastFolder}, last_music={self.index}, mix={1 if self.player.mix else 0}, repeat={1 if self.repeat else 0}")

            else:

                self.database.Execute(f"UPDATE settings SET volume={self.volume}, mix={1 if self.player.mix else 0}, repeat={1 if self.repeat else 0}")

            self.database.Commit()
            self.database.Disconnect()
        
        except:
            
            pass

        self.destroy()
