from dataclasses import fields
from email import header
import webbrowser
from wsgiref.util import request_uri
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import webbrowser
from urllib.parse import urlencode
import base64


def create_request():
    base_url = 'https://api.spotify.com/v1/'

def get_token(id, secret):
    url = 'https://accounts.spotify.com/api/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': id,
        'client_secret': secret,
    }
    response = requests.post(url, data = data)
    if(response and response.status_code == 200):
        return response.json().get('access_token')
    else:
        return None

def get_token_auth(code, id, secret):
    
    encoded_credentials = base64.b64encode(id.encode() + b':' + secret.encode()).decode("utf-8")

    token_headers = {
    "Authorization": "Basic " + encoded_credentials,
    "Content-Type": "application/x-www-form-urlencoded"
    }

    url = 'https://accounts.spotify.com/api/token'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:3000'
    }
    response = requests.post(url, data = data, headers = token_headers)
    if(response and response.status_code == 200):
        return response.json().get('access_token')
    else:
        return None

def auth(id):
    url = 'https://accounts.spotify.com/api/authorize'
    data = {
      "response_type": 'code',
      "client_id": id,
      "scope": "user-modify-playback-state user-read-playback-state",
      "redirect_uri": 'http://localhost:3000'
    }
    webbrowser.open("https://accounts.spotify.com/authorize?" + urlencode(data))
    response = requests.get(url, params = data)
    if(response and response.status_code == 200):
        return response.json().get('code')
    else:
        return response.json()

def get_playlists(user_id, base_url, header):
    response = requests.get(base_url + "users/{}/playlists".format(user_id), headers= header)
    if(response and response.status_code == 200):
        playlists = response.json()
        return pd.DataFrame.from_dict(playlists['items'])
    else:
        return None

def get_playlist_tracks(id, base_url, header):
    response = requests.get(base_url + "playlists/{}/tracks?fields={}".format(id, "items(track(id))"), headers= header)
    if(response and response.status_code == 200):
        tracks = response.json()
        return pd.DataFrame.from_dict(tracks['items'])
    else:
        return None

def get_audio_features(id, baseurl, header):
    response = requests.get(base_url + "audio-features?ids={}".format(id), headers= header)
    if(response and response.status_code == 200):
        features = response.json()
        return features['audio_features']
    else:
        return None


def play_track(baseurl, header, track):
    response = requests.put(base_url + "me/player/play", headers = header, data = {"uri": track})
    if(response and response.status_code == 200):
        print("track playing")
        features = response.json()
        return features
    else:
        return None

def get_device(baseurl, header):
    response = requests.get(base_url + "me/player/devices", headers = header)
    if(response and response.status_code == 200):
        devices = response.json()
        return devices
    else:
        return response.json()


def get_user(baseurl, header):
    response = requests.get(base_url + "/me", headers = header)
    if(response and response.status_code == 200):
        user = response.json()
        return user
    else:
        return response.json()

    

id = "f5e1cd1aef244438b9f9e921623d830f"
secret = "789fdb605d0b48faa9291198c83e570f"
code = "AQCIfhcYqA8tiq6GMPAYWXcbPkNAelAkd8cTtC1T9YwuKatfOIp796Gl_lD58H8tExM8h7dL3ys7d-7YTzuEggTyt61KqXebRuPOm3FHrmE4Kr0LwgMLGLPHX7YpMFwua8eyt9qXnH9GsmuWsWLw2yyHTJcbOkL97BiiupcGihJzl7NN3JLQQoAr7OJL_3lUvIS8UyhZUbwgmWEV-BwWdT5PlfCz5STyjPQNZAJyHA"
#print(auth(id))
auth_token = get_token_auth(code, id, secret)

print(auth_token)

#auth_token = get_token(id, secret)

headers = {"Authorization": "Bearer {}".format(auth_token)}
base_url = 'https://api.spotify.com/v1/'

#playlists = get_playlists("sai.avula", base_url, headers)


#tracks = get_playlist_tracks(list(playlists.id)[1], base_url, headers)
#tracks = tracks['track'].apply(pd.Series)
#print(tracks)


#print(get_user(base_url, headers))
print(get_device(base_url, headers))
play_track(base_url, headers, "174MCVl2pSoR958OPB6u24")


"""
t_af = []
for i in range(len(tracks)):
    t_af.append(get_audio_features(tracks["id"][i], base_url, headers))


t_af = pd.DataFrame(t_af)[0].apply(pd.Series)

t_af = pd.concat([tracks, t_af], axis = 1)



t_af_means = t_af.mean(numeric_only= True).to_frame()

print(t_af_means.columns)



#sns.barplot(data = t_af_means)

#plt.show()
"""


