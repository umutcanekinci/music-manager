from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from time import strftime, gmtime

def GetMetadata(path) -> tuple | None:

    try:
        
        data = EasyID3(path)

    except:

        return None, 'Unknown'

    return data['title'][0] if 'title' in data.keys() else None, data['artist'][0] if 'artist' in data.keys() else 'Unknown'

def GetMusicData(fileName, folder) -> tuple:

    fileExt = fileName.split('.')[-1]
    fileName = fileName[:-len(fileExt)-1]


    path = folder.path + '/' + fileName + '.' + fileExt
    name, artist = GetMetadata(path)

    if name:
    
        if artist != 'Unknown':

            title = artist + ' - ' + name

        else:

            title = fileName
    else:

        name = title = fileName

    return fileName, fileExt, name, artist, title

def FilterMusicList(musicList, keyword) -> list:

        if keyword:
            
            return [music for music in musicList if keyword.lower() in music.title.lower()]
            
        return musicList.copy()

class Music():

    def __init__(self, id, folder, fileName, ext, name, artist, title) -> None:
        
        self.id, self.folder, self.fileName, self.ext, self.name, self.artist, self.title = id, folder, fileName.replace('\\', '/'), ext, name, artist, title
        self.path = self.folder.path + '/' + self.fileName + '.' + self.ext
        self.folder.AddMusic(self)
        self.SetImage()
    
        try:
            
            self.length = MP3(self.path).info.length

        except:

            self.length = 0
        
        self.convertedLength = strftime('%M:%S', gmtime(self.length))

    def SetImage(self) -> None:
        
        self.image = "./images/default.jpg"

        """

        audiofile = ID3(path)
        if 'APIC' in audiofile:
        
            image_data = BytesIO(audiofile['APIC:Cover'].data) # Extract album art data from ID3 tag using mutagen
        
        else:

            image_data = "./images/default.jpg"


        audiofile = eyed3.load(path)

        if audiofile.tag and audiofile.tag.frame_set.get('APIC'):

            # Extract album art data from ID3 tag
            album_art_data = audiofile.tag.frame_set['APIC'][0].image

            image_data = album_art_data
        
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