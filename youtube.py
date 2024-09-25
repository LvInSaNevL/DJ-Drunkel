import utils
import spotify

import sys
from pydoc import cli
import datetime
import re
from urllib.parse import urlparse
import os
import requests
import json

import google.auth.exceptions
import google_auth_oauthlib
import google.oauth2
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import googleapiclient.discovery
import googleapiclient.errors

# Variables and such
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl",
          "https://www.googleapis.com/auth/youtube.readonly"]
playlist = "PLRDuNIkwpnsfJaOX5Bq3jrPtP2WfP_vBl"
lastAuth = datetime.datetime.min       

def get_authenticated_service(lastAuth):
    utils.logPrint("Authenticating service access and refresh token", 0)
    nowAuth = datetime.datetime.now()
    authDiff = nowAuth - lastAuth
    if (authDiff.total_seconds() * 1000 < 250):
        datetime.time.sleep(0.150)
    
    lastAuth = datetime.datetime.now()

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "youtubeauth.json"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)

    if os.path.exists("refresh.token"):
        with open("refresh.token", 'r') as t:
            rawToken = t.read()
            with open(client_secrets_file, 'r') as j:
                youtubeAuth = json.loads(j.read())
            params = {
                "grant_type": "refresh_token",
                "client_id": youtubeAuth['installed']['client_id'],
                "client_secret": youtubeAuth['installed']['client_secret'],
                "refresh_token": rawToken
            }
            authorization_url = "https://www.googleapis.com/oauth2/v4/token"
            r = requests.post(authorization_url, data=params)
            credToken = google.oauth2.credentials.Credentials(
                                                    rawToken,
                                                    refresh_token = rawToken,
                                                    token_uri = 'https://accounts.google.com/o/oauth2/token',
                                                    client_id = youtubeAuth['installed']['client_id'],
                                                    client_secret = youtubeAuth['installed']['client_secret']
                                                    )
    else: 
        credFlow = flow.run_console()
        with open('refresh.token', 'w+') as f:
            credToken = credFlow
            f.write(credFlow._refresh_token)
            utils.logPrint('Saved Refresh Token to file: refresh.token', 0)
    
    return googleapiclient.discovery.build(api_service_name, api_version, credentials=credToken)

### <summary>
# Adds a new video to the playlist
# <param name=videoID> The YouTube video ID, usually provided by URL
### </summary
async def add_to_playlist(videoURL, search=False):
    reactList = []
    regex = "((?<=(v|V)/)|(?<=be/)|(?<=(\?|\&)v=)|(?<=embed/))([\w-]+)"
    result = re.search(regex, videoURL)
    videoID = result.group()

    utils.logPrint("Adding {0} to playlist".format(videoID), 0)

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    youtube = get_authenticated_service(lastAuth)

    try:
        add_video_response = youtube.playlistItems().insert(
            part="snippet",
            body=dict(
                snippet=dict(
                    playlistId=playlist,
                    resourceId=dict(
                        kind="youtube#video",
                        videoId=videoID
                    )
                )
            )
        ).execute()
        utils.logPrint(add_video_response['snippet']['title'], 0)
        # if search:
        #     spAdd = await spotify.search(add_video_response['snippet']['title'], add_video_response['snippet']['videoOwnerChannelTitle'])
        #     if spAdd is not None:
        #         reactList.append(spAdd)
    except googleapiclient.errors.HttpError as e:
        print(e)
        reactList.append('👎')
        return reactList
    except:
        utils.logPrint(sys.exc_info()[0], 2)
        reactList.append('👎')
        return reactList
    reactList.append('<:YouTube:1200572694064808078>')
    
    return reactList

async def get_playlist_len():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    youtube = get_authenticated_service(lastAuth)

    try:
        response = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist,
                maxResults=50,  # Adjust as needed, max is 50
                pageToken=None
            ).execute()
        return response['pageInfo']['totalResults']
    except googleapiclient.errors.HttpError as e:
            print(e)
    except:
        utils.logPrint(sys.exc_info()[0], 2)

def search(title, artist):
    print(title)
    return "<:YouTube:1200572694064808078>"