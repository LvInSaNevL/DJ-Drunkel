# File imports
import utils
import youtube
# Dep imports
import re
import requests
import datetime 
import urllib
import json
from thefuzz import fuzz

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

async def add_to_playlist(videoURL, search=False):
    reactList = []
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
        songInfo = get_song_info(videoID)
        # if search:
        #     reactList.append(youtube.search(songInfo[0], songInfo[1]))
        reactList.append("<:Spotify:1200572693104316436>")
    else:
        print(response.json())
        reactList.append('👎')

    return reactList
    
async def get_playlist_len():
    url = 'https://api.spotify.com/v1/playlists/3cEYpjA9oz9GiPac4AsH4n/tracks?fields=total'
    headers = {
        'Authorization': 'Bearer {}'.format(get_authenticated_service()),
    }
    
    response = requests.get(url, headers=headers)
    return response.json()['total']

async def get_song_info(videoID):
    url = f"https://api.spotify.com/v1/tracks/{videoID}"
    headers = {
        'Authorization': 'Bearer {}'.format(get_authenticated_service())
    }
    response = requests.get(url, headers=headers)
    data = response.json()['album']
    songInfo = (data['name'], data['artists'][0]['name'])
    return songInfo

async def search(title, artist):
    url = 'https://api.spotify.com/v1/search'
    query = urllib.parse.quote(f"track:{title} artist:{artist}")
    params = {
        'q': query,
        'type': 'track',
        'limit': 50,
        'offset': 0
    }
    headers = {
        'Authorization': 'Bearer {}'.format(get_authenticated_service()),
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()['tracks']['items']
    maxMatch = {
        "match": 0,
        "data": []
    }

    for t in range(len(data)):
        songName = data[t]['name']
        artistName = data[t]['artists'][0]['name']
      
        songRatio = fuzz.ratio(title, songName)
        artistRatio = fuzz.ratio(artist, artistName)
        # Allows us to bias towards the artist's name, its safer
        totalRatio = (((songRatio * 0.65) + (artistRatio * 0.35)))

        if (totalRatio > maxMatch['match']):
            maxMatch['match'] = totalRatio
            maxMatch['data'] = data[t]

    if (maxMatch['match'] > 90):
        add = await add_to_playlist(maxMatch['data']['external_urls']['spotify'], False)
        if add[0] == "<:Spotify:1200572693104316436>":
            return add[0]
        else:
            return None