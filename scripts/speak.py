from gtts import gTTS
from io import BytesIO
import pygame

def speak(text, language='tr'):

    mp3_fo = BytesIO()
    tts = gTTS(text, lang=language)
    tts.write_to_fp(mp3_fo)
    mp3_fo.seek(0)

    with open('temp.mp3', 'wb') as f:
        f.write(mp3_fo.read())
        
    pygame.mixer.music.load('sound.mp3')
    pygame.mixer.music.play()

pygame.init()
pygame.mixer.init()
speak("Selam orospi çocugi")