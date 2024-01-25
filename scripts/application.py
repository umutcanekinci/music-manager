import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO

class MusicPlayerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Music Player")

        self.current_music_label = tk.Label(self.root, text="Currently Playing:")
        self.current_music_label.pack()

        self.album_photo_label = tk.Label(self.root)
        self.album_photo_label.pack()

        self.get_album_photo_button = tk.Button(self.root, text="Get Album Photo", command=self.get_album_photo)
        self.get_album_photo_button.pack()

    def get_album_photo(self):
        # Replace 'YOUR_API_KEY' and 'YOUR_ARTIST' with actual values
        api_key = 'YOUR_API_KEY'
        artist = 'YOUR_ARTIST'
        track = 'TRACK_NAME'  # Replace with the actual track name

        url = f'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={api_key}&artist={artist}&track={track}&format=json'

        try:
            response = requests.get(url)
            data = response.json()

            # Extract album image URL from the API response
            image_url = data['track']['album']['image'][2]['#text']

            # Download the image
            image_data = requests.get(image_url).content

            # Display the image on the Tkinter window
            self.display_image(image_data)

        except Exception as e:
            print(f"Error: {e}")

    def display_image(self, image_data):
        # Open the image using Pillow
        image = Image.open(BytesIO(image_data))

        # Resize the image if necessary
        image = image.resize((150, 150), Image.ANTIALIAS)

        # Convert the image to Tkinter format
        tk_image = ImageTk.PhotoImage(image)

        # Update the label with the new image
        self.album_photo_label.config(image=tk_image)
        self.album_photo_label.image = tk_image

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MusicPlayerApp()
    app.run()
