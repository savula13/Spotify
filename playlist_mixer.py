import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, render_template, request, redirect, url_for
import random
import pandas as pd

app = Flask(__name__)

CLIENT_ID = pd.read_csv('secrets.txt', header=None)[0][0]
CLIENT_SECRET = pd.read_csv('secrets.txt', header=None)[0][1]


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='f5e1cd1aef244438b9f9e921623d830f',
                                               client_secret='789fdb605d0b48faa9291198c83e570f',
                                               redirect_uri='http://localhost:3000',
                                               scope='playlist-read-private user-read-recently-played'))

def get_playlists():
    playlists = sp.current_user_playlists()
    return playlists['items']

def get_recent_audio_features():
    # Get the 50 most recently played tracks and collect their audio features
    results = sp.current_user_recently_played(limit=50)
    audio_features = []
    for item in results['items']:
        track_id = item['track']['id']
        features = sp.audio_features(track_id)
        if features:
            audio_features.append(features[0])
    return audio_features

def calculate_feature_averages(audio_features):
    # Calculate the average of each audio feature from the recently played tracks
    num_tracks = len(audio_features)
    feature_sums = {}
    for track_features in audio_features:
        for feature, value in track_features.items():
            feature_sums.setdefault(feature, 0)
            feature_sums[feature] += value

    averages = {feature: value / num_tracks for feature, value in feature_sums.items()}
    return averages

def weighted_random_choice(tracks, feature_averages):
    # Create a weighted random selection based on the audio features of the tracks
    weights = []
    for track in tracks:
        weight = 0
        for feature, average_value in feature_averages.items():
            weight += abs(average_value - track['audio_features'][feature])
        weights.append(weight)

    total_weights = sum(weights)
    probabilities = [weight / total_weights for weight in weights]

    selected_track = random.choices(tracks, weights=probabilities, k=1)[0]
    return selected_track

def adjust_percentages(playlist_percentages):
    total_percentage = sum(playlist_percentages)
    if total_percentage > 100:
        diff = total_percentage - 100
        max_index = playlist_percentages.index(max(playlist_percentages))
        playlist_percentages[max_index] -= diff

@app.route('/')
def index():
    playlists = get_playlists()
    playlist_ids = [playlist['id'] for playlist in playlists]
    playlist_percentages = {playlist_id: 0 for playlist_id in playlist_ids}
    return render_template('index.html', playlists=playlists, playlist_percentages=playlist_percentages)

@app.route('/select_tracks', methods=['POST'])
def select_tracks():
    playlist_percentages = {playlist_id: int(request.form.get(playlist_id, 0)) for playlist_id in request.form}
    adjust_percentages(list(playlist_percentages.values()))

    selected_tracks = {}
    for playlist_id, percentage in playlist_percentages.items():
        if percentage > 0:
            playlist_tracks = sp.playlist_tracks(playlist_id)
            total_tracks = len(playlist_tracks['items'])
            num_tracks_to_select = round(total_tracks * (percentage / 100))
            
            audio_features = get_recent_audio_features()
            feature_averages = calculate_feature_averages(audio_features)
            
            weighted_tracks = []
            for track in playlist_tracks['items']:
                track_audio_features = sp.audio_features(track['track']['id'])[0]
                weighted_tracks.append({'track': track, 'audio_features': track_audio_features})

            selected_tracks[playlist_id] = [weighted_random_choice(weighted_tracks, feature_averages) for _ in range(num_tracks_to_select)]

    add_songs_to_queue(selected_tracks)

    return redirect(url_for('index'))

def add_songs_to_queue(selected_tracks):

    print("Tracks to be added to the play next queue:")
    for playlist_id, tracks in selected_tracks.items():
        for track in tracks:
            track_name = track['track']['name']
            track_artists = ", ".join([artist['name'] for artist in track['track']['artists']])
            print(f"Track Name: {track_name}\n   Artist(s): {track_artists}")
    print("\n")

if __name__ == '__main__':
    app.run(debug=True)
