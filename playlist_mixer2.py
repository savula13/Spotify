from dataclasses import fields
from select import select
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import random
import pandas as pd
import requests



CLIENT_ID = pd.read_csv('secrets.txt', header=None)[0][0]
CLIENT_SECRET = pd.read_csv('secrets.txt', header=None)[0][1]

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                            client_secret= CLIENT_SECRET,
                                            redirect_uri='http://localhost:3000',
                                            scope='playlist-read-private user-read-recently-played user-read-playback-state user-modify-playback-state'))

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
    print(audio_features)
    num_tracks = len(audio_features)
    feature_sums = {}
    for track_features in audio_features:
        count = 0
        for feature, value in track_features.items():
            count += 1
            #print("Feature: {}".format(feature))
            #print("Value: {}".format(value))
            feature_sums.setdefault(feature, 0)
            feature_sums[feature] += value
            if(count == 11):
                break

    averages = {feature: value / num_tracks for feature, value in feature_sums.items()}
    return averages

def weighted_random_choice(tracks, feature_averages,num):
    # Create a weighted random selection based on the audio features of the tracks
    weights = []
    for track in tracks:
        weight = 0
        for feature, average_value in feature_averages.items():
            weight += abs(average_value - track['audio_features'][feature])
        weights.append(weight)

    total_weights = sum(weights)
    probabilities = [weight / total_weights for weight in weights]

    selected_tracks = random.choices(tracks, weights=probabilities, k=num)
    return selected_tracks

def adjust_percentages(playlist_percentages):
    total_percentage = sum(playlist_percentages)
    if total_percentage > 100:
        diff = total_percentage - 100
        max_index = playlist_percentages.index(max(playlist_percentages))
        playlist_percentages[max_index] -= diff


def playlist_info(id):
    limit = 100
    offset = 0
    items = []
    while(True):
        req = sp.playlist_tracks(id, fields = "items(added_at, track(name, id, album(name, id, genres, release_date), artists(id, name, genres), popularity))", limit = limit, offset = offset)
        if(len(req["items"]) == 0):
            break
        items.extend(req["items"])
        offset += limit

    spread = pd.DataFrame.from_dict(items)
    track = spread["track"].apply(pd.Series)
    track.columns = ["track " + column for column in track.columns]
    album = track["track album"].apply(pd.Series)
    album.columns = [("album " + column).replace("track", "") for column in album.columns]
    #artists = [value for d in track["track artists"].apply(pd.Series) for value in d.values()]
    artist = pd.DataFrame(track["track artists"][0]).apply(pd.Series)
    artist.columns = [("arist " + column).replace("track", "") for column in artist.columns]


    ret = pd.concat([spread, track, album, artist], axis = 1).drop(labels = ["track", "track album", "track artists"], axis = 1)

    return ret

def get_multiple_playlists(pl):
    ret = []
    for p in pl:
        ret.append(playlist_info(p))
    return ret

def filter_time_added(songs, start, end):
    songs['added_at'] = songs['added_at'].astype('datetime64[ns]')
    return(songs[(songs['added_at'] >= start) & (songs['added_at'] <= end)])

def filter_release_date(songs, start, end):
    songs['album release_date'] = songs['album release_date'].astype('datetime64[ns]')
    return(songs[(songs['album release_date'] >= start) & (songs['album release_date'] <= end)])

#def get_date_range(timeframe):
#    seasons = {"Spring": ["3/1", "5/31"], "Summer": ["6/1", "8/31"], "Fall": ["9/1", "11/30"], "Winter"}


def get_active_device(device = "Smartphone"):
    activate = None
    for d in sp.devices()['devices']:
        if((d['is_active'] == True ) & (d['is_restricted'] == False )):
            return d['id']
        if(d['type'] == device):
            activate = d['id']
    
    return(activate)

def shuffle_playlists(pl, n, splits):
    ret = pd.DataFrame()
    for i in range(len(pl)):
        ret = pd.concat([ret, pl[i].sample(n = round(n*splits[i])).reset_index(drop = True)])
    #print(ret)
    return ret.sample(frac = 1).reset_index(drop = True)




def main():



    playlists = sp.current_user_playlists()
    playlist_ids = {}
    for idx, playlist in enumerate(playlists['items'], 1):
        playlist_ids[playlist['name']] = playlist['id']

    SPLIT_PERCENT = 0.33
    NUM_SONGS = 30
    D1 = pd.to_datetime('01-01-2022', format = "%m-%d-%Y")
    D2 = pd.to_datetime('1-11-2024', format = "%m-%d-%Y")

    tracks = playlist_info(playlist_ids["shawshank"])

    #print(filter_time_added(tracks, D1, D2))

    
    s_playlists = get_multiple_playlists([playlist_ids["shawshank"], playlist_ids["THE sugar honey iced tea"], playlist_ids["moss"]])

    for i in range(len(s_playlists)):
        s_playlists[i] = filter_time_added(s_playlists[i], D1, D2)
        s_playlists[i] = filter_release_date(s_playlists[i], D1, D2)

    shuffled = shuffle_playlists(s_playlists, NUM_SONGS, [SPLIT_PERCENT, SPLIT_PERCENT, SPLIT_PERCENT])

    

    device_id = get_active_device()

    for s in shuffled["track id"]:
        sp.add_to_queue(s, device_id = device_id)
    
    #sp.start_playback(device_id)
    

main()