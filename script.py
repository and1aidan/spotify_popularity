import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


def get_access_token(client_id, client_secret):
    spotify_auth_url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}

    response = requests.post(
        spotify_auth_url,
        headers=headers,
        data=data,
        auth=(client_id, client_secret)
    )
    response.raise_for_status()
    return response.json()["access_token"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ---- CACHES ----
_TRACK_CACHE = {}
_ARTIST_CACHE = {}

def fetch_track_json(track_id, token):
    if track_id in _TRACK_CACHE:
        return _TRACK_CACHE[track_id]
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    r = requests.get(url, headers=_auth_headers(token))
    r.raise_for_status()
    _TRACK_CACHE[track_id] = r.json()
    return _TRACK_CACHE[track_id]

def fetch_artist_json(artist_id, token):
    if artist_id in _ARTIST_CACHE:
        return _ARTIST_CACHE[artist_id]
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    r = requests.get(url, headers=_auth_headers(token))
    r.raise_for_status()
    _ARTIST_CACHE[artist_id] = r.json()
    return _ARTIST_CACHE[artist_id]


# ---- YOUR METHODS, rewritten to use cached JSON ----

def get_track_popularity(track_id, token):
    track = fetch_track_json(track_id, token)
    return track["popularity"]

def get_track_artists(track_id, token):
    track = fetch_track_json(track_id, token)
    return [{"name": a["name"], "id": a["id"]} for a in track["artists"]]

def get_duration_ms(track_id, token):
    track = fetch_track_json(track_id, token)
    return track["duration_ms"]

def get_explicit_status(track_id, token):
    track = fetch_track_json(track_id, token)
    return track["explicit"]

def get_track_name(track_id, token):
    track = fetch_track_json(track_id, token)
    return track["name"]

def get_track_release_date(track_id, token):
    track = fetch_track_json(track_id, token)
    return track["album"]["release_date"]

def get_num_markets(track_id, token):
    track = fetch_track_json(track_id, token)
    return len(track["available_markets"])


def get_artist_name(artist_id, token):
    artist = fetch_artist_json(artist_id, token)
    return artist["name"]

def get_artist_genres(artist_id, token):
    artist = fetch_artist_json(artist_id, token)
    return artist["genres"]

def get_artist_popularity(artist_id, token):
    artist = fetch_artist_json(artist_id, token)
    return artist["popularity"]

def get_artist_follow_count(artist_id, token):
    artist = fetch_artist_json(artist_id, token)
    return artist["followers"]["total"]


# main
def main():
    token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    print(get_num_markets("3bGfuGWywg85koHG8nturm",token))

if __name__ == "__main__":
    main()