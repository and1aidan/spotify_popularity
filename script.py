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
    print(response.json())
    return response.json()["access_token"]


def main():
    token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    print(token)
if __name__ == "__main__":
    main()