from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Constants
URL = "https://www.billboard.com/charts/hot-100"

CLIENT_ID = os.environ.get("client_id")
CLIENT_SECRET = os.environ.get("client_secret")
REDIRECT_URI = "http://example.com/callback/"

SCOPE = "playlist-modify-private"

# User input
date = input("Which year would you like to travel to? Enter date in the format YYYY-MM-DD: ")
year = date.split("-")[0]

# Fetch Billboard Hot 100 page
response = requests.get(f"{URL}/{date}")
if response.status_code != 200:
    print("Failed to retrieve Billboard page")
    exit()

billboard_website = response.text
soup = BeautifulSoup(billboard_website, "html.parser")

# Extract song titles
song_titles = [song.get_text().strip() for song in soup.find_all('h3', id='title-of-a-story', class_='a-no-trucate')]

# Debug: Print extracted song titles
print("Extracted song titles:", song_titles)

# Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))

# Search for each song on Spotify and get URI
uri_list = []
for song in song_titles:
    query = f"track:{song} year:{year}"
    print(f"Searching for: {query}")  # Debug: Print the search query
    results = sp.search(q=query, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        uri = track['uri']
        uri_list.append(uri)
        print(f"Found URI for {song}: {uri}")  # Debug: Print the found URI
    else:
        print(f"Song '{song}' from {year} not found.")

# Debug: Print collected URIs
print("Collected URIs:", uri_list)

# Create a new playlist
user_id = sp.me()['id']
playlist_name = f"Billboard Hot 100 on {date}"
playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
playlist_id = playlist['id']

# Add tracks to the playlist
if uri_list:
    sp.playlist_add_items(playlist_id=playlist_id, items=uri_list)
    print(f"Playlist '{playlist_name}' created successfully with {len(uri_list)} tracks.")
else:
    print(f"No tracks found to add to the playlist '{playlist_name}'.")

# Verify the playlist contents
playlist_contents = sp.playlist_tracks(playlist_id=playlist_id)
print(f"Tracks in playlist '{playlist_name}': {[track['track']['name'] for track in playlist_contents['items']]}")
