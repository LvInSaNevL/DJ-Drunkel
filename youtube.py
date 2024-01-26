import sys
from pydoc import cli
import datetime
import re
from urllib.parse import urlparse
import os
import utils
import requests

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
playlist = "PLRDuNIkwpnsdsAaytTIOtkaQGcsdy_fJH"
lastAuth = datetime.datetime.min       

def refresh_token(client_id, client_secret, refresh_token):
    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post(token_url, data=data)
    token_info = response.json()
    return token_info.get("access_token")

# Authenticates to the Google API
def get_authenticated_service(lastAuth):
    utils.logPrint("Authenticating YouTube service access and refresh token", 0)
    nowAuth = datetime.datetime.now()
    authDiff = nowAuth - lastAuth
    if (authDiff.total_seconds() * 1000 < 250):
        datetime.time.sleep(0.150)
    
    lastAuth = datetime.datetime.now()

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "youtubeauth.json"
    redirect_uri = "http://localhost:5656"
    cred_token = None

    # Try to use the refresh token first
    if os.path.exists("refresh.token"):
        try:
            cred_token = Credentials.from_authorized_user_file('refresh.token')
            cred_token.refresh(Request())
        except google.auth.exceptions.RefreshError as e:
            print(e)
    # Manually authenticate with the user if no token is available  
    else:
        credFlow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
        cred = credFlow.run_local_server(
            host='localhost',
            port=5656,
            authorization_prompt_message='Please visit this URL: {url}',
            success_message='The auth flow is complete; you may close this window.',
            open_browser=False
        )
        with open('refresh.token', 'w') as token:
            token.write(cred.to_json())
    return googleapiclient.discovery.build(api_service_name, api_version, credentials=cred_token)

### <summary>
# Adds a new video to the playlist
# <param name=videoID> The YouTube video ID, usually provided by URL
### </summary
async def add_to_playlist(videoURL):
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
    except googleapiclient.errors.HttpError as e:
            print(e)
    except:
        utils.logPrint(sys.exc_info()[0], 2)

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