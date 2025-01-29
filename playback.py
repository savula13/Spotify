
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def start_recently_played_song():
    # Replace these values with your own Spotify API credentials
    CLIENT_ID = "f5e1cd1aef244438b9f9e921623d830f"
    CLIENT_SECRET = "789fdb605d0b48faa9291198c83e570f"
    REDIRECT_URI = 'http://localhost:3000'

    # Create a Spotipy client with the necessary credentials
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri=REDIRECT_URI,
                                                   scope='user-read-recently-played user-modify-playback-state'))

    try:
        # Get the most recently played songs for the authenticated user
        recent_tracks = sp.current_user_recently_played(limit=1)

        if recent_tracks and 'items' in recent_tracks and len(recent_tracks['items']) > 0:
            track_uri = recent_tracks['items'][0]['track']['uri']
            
            # Start playback for the most recent song
            sp.start_playback(uris=[track_uri])
            print("Started playback for the most recent song.")
        else:
            print("No recently played tracks found.")

    except spotipy.SpotifyException as e:
        print(f"Error: {e}")
        print("Make sure you have provided valid API credentials and have granted the necessary scopes.")

if __name__ == "__main__":
    start_recently_played_song()

"""

from dataclasses import fields
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Replace these with your own values
SPOTIFY_CLIENT_ID = "f5e1cd1aef244438b9f9e921623d830f"
SPOTIFY_CLIENT_SECRET = "789fdb605d0b48faa9291198c83e570f"
SPOTIFY_REDIRECT_URI = 'http://localhost:3000'  # e.g., "http://localhost:8000/callback"
SCOPE = "playlist-read-private user-read-playback-state user-modify-playback-state"

# Initialize the spotipy client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri=SPOTIFY_REDIRECT_URI,
                                               scope=SCOPE))

def get_most_recent_playlists(user_id, limit=2):
    playlists = sp.user_playlists(user_id, limit=50)  # Retrieve up to 50 playlists (maximum allowed per request)
    all_playlists = {}
    for i in range(len(playlists['items'])):
        all_playlists[playlists['items'][i]["name"]] = playlists['items'][i]['id']
    print(all_playlists)
    return[playlists['items'][0]['id'], playlists['items'][1]['id']]
    #playlists = sorted(playlists['items'], key=lambda x: x['created_at'], reverse=True)
    #return [playlist['id'] for playlist in playlists[:limit]]

def get_playlist_by_name(user_id, name):
    playlists = sp.user_playlists(user_id, limit=50)  # Retrieve up to 50 playlists (maximum allowed per request)
    all_playlists = {}
    for i in range(len(playlists['items'])):
        all_playlists[playlists['items'][i]["name"]] = playlists['items'][i]['id']
    #print(all_playlists
    id = all_playlists[name]
    results = sp.playlist_tracks(id)
    #results = tracks['items']
    playlist_tracks = {}
    for idx, track in enumerate(results['items'], 1):
        track_name = track['track']['name']
        track_id = track['track']['id']
        track_artists = ", ".join([artist['name'] for artist in track['track']['artists']])
        print(f"{idx}. Track Name: {track_name}\n   Track ID: {track_id}\n   Artist(s): {track_artists}\n")
        audio_features = sp.audio_features(track_id)[0]
    
    

        playlist_tracks[track_name] = {
            'track_id': track_id,
            'artists': track_artists,
            'audio_features': audio_features
        }

    return playlist_tracks

def add_songs_to_queue(playlist_ids):
    # Get 20 songs from each playlist
    songs_to_add = []
    for playlist_id in playlist_ids:
        playlist_tracks = sp.playlist_tracks(playlist_id, limit=5, offset=0)
        for item in playlist_tracks['items']:
            if 'track' in item and item['track']:
                songs_to_add.append(item['track']['uri'])
               #print(item['track']['uri'])
    #print(songs_to_add)
    # Add the songs to the playback queue
    if songs_to_add:
        for s in songs_to_add:
            print(s)
            #sp.add_to_queue(s)

if __name__ == "__main__":
    # Replace this with the user ID you want to use
    user_id = "sai.avula"

    # Get the most recent 2 playlists of the user
    #playlist_ids = get_most_recent_playlists(user_id, limit=2)
    #add_songs_to_queue(playlist_ids)
    print(get_playlist_by_name(user_id, 'Club Sai'))
