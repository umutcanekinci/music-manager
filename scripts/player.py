# Import Packages
from pygame import mixer, error
from time import strftime, gmtime

from random import shuffle


from scripts.folder import Folder
from scripts.music import Music

#from mutagen.id3 import ID3, APIC
#from stagger import read_tag, id3
#import requests
#from io import BytesIO

class Player():

    def __init__(self) -> None:

        self.playList = []
        self.mixList = []
        self.folders = {}

        self.isPlaying = False
        self.lastMusic = None
        self.index = None
        self.mixIndex = 0
        self.mix = False
        self.repeat = False

    def ResumePause(self) -> None:
        
        if self.index != None:

            if self.isPlaying:

                self.Pause()

            else:

                self.Resume()

    def Resume(self) -> None:

        mixer.music.unpause()
        self.isPlaying = True

    def Pause(self) -> None:

        mixer.music.pause()
        self.isPlaying = False

    def Repeat(self) -> None:

        self.repeat = not self.repeat

    def Mix(self) -> None:

        self.mix = not self.mix

    def AddFolder(self, *args) -> None:

        """
        
        Parameter => *args => (id, path), (id, path), (id, path)...
        
        """

        for folderID, folderPath in args:
            
            self.folders[folderID] = Folder(folderID, folderPath)

    def AddMusic(self, *args) -> None:

        for musicID, folderID, fileName, ext, name, artist, title in args:

            Music(musicID, self.folders[folderID], fileName, ext, name, artist, title)
 
    def OpenPlayList(self, playList: list, music, start=True) -> None:

        self.playList = playList
        self.mixList.clear()
        self.index = self.mixIndex = 0
        self.Play(music, start)

    def Play(self, music: Music, start=True, startValue: float=0) -> None:
        
        try:

            self.mixIndex = self.mixList.index(music) if self.mix else 0
            self.index = self.playList.index(music)
            
            mixer.music.load(music.path)
            mixer.music.play(-1 if self.repeat else 0, startValue)

            if not start:

                self.Pause()

            else:

                self.Resume()

            self.lastMusic = music

        except error:

            self.Next()

            """
            musicID = list(self.filteredMusics[self.selectedFolder].keys())[index]
            self.DeleteMusic(musicID)
            self.LoadMusics(self.GetMusics())
            self.OpenFolder(self.selectedFolder)
            self.OpenMusic(index)
            """

    def UpdateTime(self, filePath, length) -> None:
         
        self.currentTime = int(mixer.music.get_pos() / 1000)
        self.convertedCurrentTime = strftime('%M:%S', gmtime(self.currentTime))
        return
        #sliderTime = int(self.slider.get())

        #self.sliderLabel.config(text=f'Slider Position: {sliderTime}\nMusic Position: {currentTime}')

        #if sliderTime + 1 == currentTime: # Slider isn't moved
            
        #    pass

        #else: # Slider is moved
            
        #    pass
            #print("slider is moved")
            #currentTime = sliderTime
            #convertedCurrentTime = strftime('%M:%S', gmtime(currentTime))

            #self.Play(filePath, startValue=currentTime)
        
        self.timer.config(text=convertedCurrentTime)
        self.slider.set(currentTime)


        if self.currentTime == self.lastMusic.length:

            return self.Next()

        self.timer.after(1000, lambda filePath=filePath, length=length:self.UpdateTime(filePath, length))

    def ClearMixList(self) -> None:

        self.mixList.clear()
        self.mixList.append(self.lastMusic)

    def Previous(self) -> None:

        self.Play(self.playList[self.index - 1])

    def Next(self) -> None:

        if self.mix:

            if not self.mixList:

                self.mixList = self.playList.copy()
                self.mixList.remove(self.lastMusic)
                shuffle(self.mixList)
                self.mixList = [self.lastMusic] + self.mixList
                self.mixIndex = 0

            if self.mixIndex < len(self.mixList) - 1:

                self.Play(self.mixList[self.mixIndex + 1])

        else:
            
            if self.index < len(self.playList) - 1:

                self.Play(self.mixList[self.mixIndex + 1])