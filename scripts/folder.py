class Folder():

    def __init__(self, id, path) -> None:
        
        self.id = id
        self.musics = []
        self.path = path.replace('\\', '/')
        self.name = path.split('/')[-1]

    def AddMusic(self, music) -> None:

        self.musics.append(music)

    #def GetMusicCount(self) -> int:

    #    return len(self.musics)
