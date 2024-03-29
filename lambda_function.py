import os
import base64
import requests
from urllib.parse import urlencode

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
TOKEN_ENDPOINT = "https://accounts.spotify.com/api/token"


def get_access_token():
    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = urlencode(
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
    )

    response = requests.post(TOKEN_ENDPOINT, headers=headers, data=body)

    return response.json()


DISCOVER_WEEKLY_PLAYLIST_ID = os.getenv("SPOTIFY_DISCOVER_WEEKLY_PLAYLIST_ID")
DISCOVER_WEEKLY_TRACKS_ENDPOINT = f"https://api.spotify.com/v1/playlists/{DISCOVER_WEEKLY_PLAYLIST_ID}/tracks?fields=items%28track%28uri%29%29"


def get_discover_weekly_tracks(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(DISCOVER_WEEKLY_TRACKS_ENDPOINT, headers=headers)

    return response.json()


def map_to_uris(tracks):
    uris = [track["track"]["uri"] for track in tracks["items"]]

    return {"uris": uris}


LOG_PLAYLIST_ID = os.getenv("SPOTIFY_LOG_PLAYLIST_ID")
LOG_PLAYLIST_TRACKS_ENDPOINT = (
    f"https://api.spotify.com/v1/playlists/{LOG_PLAYLIST_ID}/tracks"
)


def add_discover_weekly_tracks_to_log_playlist():
    access_token = get_access_token()["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    body = map_to_uris(get_discover_weekly_tracks(access_token))

    response = requests.post(LOG_PLAYLIST_TRACKS_ENDPOINT, headers=headers, json=body)

    return response


def handler(event, context):
    response = add_discover_weekly_tracks_to_log_playlist()

    print(response.json())

    if response.ok:
        return {"message": "success"}
    else:
        return {"message": "fail"}
