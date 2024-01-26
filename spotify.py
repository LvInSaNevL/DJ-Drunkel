# File imports
import utils
# Dep imports
import re
import requests
import datetime
import json
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util

auth_url = 'https://accounts.spotify.com/authorize'
token_url = 'https://accounts.spotify.com/api/token'
base_url = 'https://api.spotify.com/v1/'
redirect_uri = 'http://localhost:3000'
scope = 'playlist-modify-public'
playlist = "7iAnRkjRC4RqbkzjeSRi85"
lastAuth = datetime.datetime.min
creds = utils.readAuth("spotify")

def get_authenticated_service():
    with open("spotify.token") as jsonfile:
        token = json.load(jsonfile)

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': token['token'],
        'client_id': creds['client'],
        'client_secret': creds['secret'],
    }
    response = requests.post(token_url, data=data)

    if response.status_code == 200:
        # The response contains a new access token and possibly a new refresh token
        new_access_token = response.json()['access_token']
        new_refresh_token = response.json().get('refresh_token', creds['token'])
        with open('spotify.token', 'w') as token:
            token.write(json.dumps({"token": new_refresh_token}))
        return new_access_token 
    else:
        # Handle errors
        print(f"Error: {response.status_code}, {response.text}")

async def add_to_playlist(videoURL):
    regex = "(?:https:\/\/open.spotify.com\/track\/|spotify:track:)([a-zA-Z0-9]+)"
    result = re.search(regex, videoURL)
    videoID = result.group(1)

    utils.logPrint("Adding {0} to playlist".format(videoID), 0)
    
    url = f"https://api.spotify.com/v1/playlists/{playlist}/tracks"
    headers = {
        'Authorization': 'Bearer {}'.format(get_authenticated_service()),
        'Content-Type': 'application/json',
    }
    data = {
        "uris": [f"spotify:track:{videoID}"],
        "position": 0
    }

    response = requests.post(url, headers=headers, json=data)
    print(response.status_code)
    if response.status_code == 201:
        print(response.json())
        return True
    else:
        print(response.json())
        return False
    
async def get_playlist_len():
    url = 'https://api.spotify.com/v1/playlists/3cEYpjA9oz9GiPac4AsH4n/tracks?fields=total'
    headers = {
        'Authorization': 'Bearer {}'.format(get_authenticated_service()),
    }
    
    response = requests.get(url, headers=headers)
    return response.json()['total']