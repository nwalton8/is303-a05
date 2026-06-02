'''
Noah Walton
IS303-A05

Playlist
Add song, remove song, total duration, find longest song

Inputs:
- Song objects with title, artist, and duration

Processes:
- Song class: stores title, artist, duration; displays info
- Playlist class: manages a collection of songs, provides methods to 
  add/remove songs, calculate total duration, and find the longest song

Outputs:
- Each songs info, total duration of the playlist, longest song info

'''

class Song:
    def __init__(self, title, artist, duration):
        self.title = title
        self.artist = artist
        self.duration = duration # doing it in seconds
        
    def __str__(self):
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{self.title} by {self.artist} - {minutes}:{seconds:02d}"
    
class Playlist:
    def __init__(self):
        self.songs = []
        
    def add_song(self, song):
        self.songs.append(song)
        
    def remove_song(self, title):
        self.songs = [song for song in self.songs if song.title != title]
        
    def total_duration(self):
        return sum(song.duration for song in self.songs)
    
    def longest_song(self):
        if not self.songs:
            return None
        return max(self.songs, key=lambda song: song.duration)
    
    def __str__(self):
        return "\n".join(str(song) for song in self.songs)

# Main program

playlist = Playlist()

while True:
    print("\nPlaylist Menu:")
    print("1. Add Song")
    print("2. Remove Song")
    print("3. Total Duration")
    print("4. Longest Song")
    print("5. Display Playlist")
    print("6. Exit")
    
    choice = input("Choose an option: ")
    
    if choice == '1':
        title = input("Enter song title: ").strip().lower()
        artist = input("Enter artist name: ").strip().lower()
        duration = int(input("Enter duration in seconds: ").strip())
        song = Song(title, artist, duration)
        playlist.add_song(song)
        print(f"Added: {song.display_info()}")
        
    elif choice == '2':
        title = input("Enter the title of the song to remove: ").strip().lower()
        playlist.remove_song(title)
        print(f"Removed song with title: {title}")
        
    elif choice == '3':
        total_seconds = playlist.total_duration()
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        print(f"Total Duration: {minutes} minutes and {seconds} seconds")
        
    elif choice == '4':
        longest = playlist.longest_song()
        if longest:
            print(f"Longest Song: {longest.display_info()}")
        else:
            print("No songs in the playlist.")
            
    elif choice == '5':
        print("Displaying the playlist:")
        print(playlist)
    
    elif choice == '6':
        print("Exiting the playlist manager.")
        break
        
    else:
        print("Invalid option. Please try again.")