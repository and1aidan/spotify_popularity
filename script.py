import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
# api token
def get_access_token(client_id, client_secret):
    spotify_auth_url = "https://accounts.spotify.com/api/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(
        spotify_auth_url,
        headers=headers,
        data=data,
        auth=(client_id, client_secret)
    )

    response.raise_for_status()
    # print(response.json())
    return response.json()["access_token"]

# y label, what we are going to try to predict
def get_track_popularity(track_id, token):
    pass



''' artist's metadata '''

# retrieve artist by artist_id, type string
def get_artist_name(artist_id, token):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    artist = requests.get(
        url, 
        headers=headers
    )

    return artist.json()["name"]

# retrieve genres for an artist by artist_id, type array of strings
def get_artist_genres(artist_id, token):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    artist = requests.get(
        url, 
        headers=headers
    )

    return artist.json()["genre"]
# retrieve popularity of an artist of scale 0-100, type int
def get_artist_popularity(artist_id, token):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    artist = requests.get(
        url, 
        headers=headers
    )
# retrieve follower count of an artist, type int
def get_artist_follow_count(artist_id, token):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    artist = requests.get(
        url, 
        headers=headers
    )

    return artist.json()["followers"]["total"]    

''' track metadata '''

# retrieve artists, type arr
def get_track_artists():
    pass

# retrieve track duration
def get_duration_ms(track_id, token):
    pass

# retrieve if a song has explicit lyrics or not, type boolean
def get_explicit_status(track_id, token):
    pass

# retrieve if a track has 
def get_track_name(track_id, token):
    pass
# retrieve release date of track, api consists of release_date and release_data_precision so check this one in-depth
def get_track_release_date(track_id, token):
    pass

# retrieve number of markets song is currently available in, type arr
def get_num_markets(track_id, token):
    pass


# main
def main():
    token = get_access_token(CLIENT_ID, CLIENT_SECRET)

if __name__ == "__main__":
    main()