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

# ---- category api call methods to retrieve playlist ids, diversifying dataset ----
# def get_all_category_ids(token):
#     url = "https://api.spotify.com/v1/browse/categories"
#     headers = _auth_headers(token)

#     category_ids = []
#     limit = 50
#     offset = 0

#     while True:
#         r = requests.get(url, headers=headers, params={"limit": limit, "offset": offset})
#         r.raise_for_status()
#         data = r.json()

#         # IMPORTANT: categories -> items -> each has "id" like "pop", "rock", etc.
#         for cat in data["categories"]["items"]:
#             category_ids.append(cat["id"])

#         if data["categories"]["next"] is None:
#             break

#         offset += limit

#     return category_ids

# def get_playlist_ids_from_category(category_id, token, max_playlists=50, country="US"):
#     url = f"https://api.spotify.com/v1/browse/categories/{category_id}/playlists"
#     headers = _auth_headers(token)

#     playlist_ids = []
#     limit = 50
#     offset = 0

#     while True:
#         params = {"limit": limit, "offset": offset, "country": country}
#         r = requests.get(url, headers=headers, params=params)

#         # Skip categories that aren't accessible via client_credentials (often 404)
#         if r.status_code == 404:
#             return []

#         r.raise_for_status()
#         data = r.json()

#         for playlist in data["playlists"]["items"]:
#             playlist_ids.append(playlist["id"])
#             if len(playlist_ids) >= max_playlists:
#                 return playlist_ids

#         if data["playlists"]["next"] is None:
#             break

#         offset += limit

#     return playlist_ids



# def collect_playlist_ids_from_categories(token, max_playlists_per_category=5, country="US"):
#     all_playlist_ids = []
#     seen = set()

#     category_ids = get_all_category_ids(token)

#     for i, cid in enumerate(category_ids, start=1):
#         url = f"https://api.spotify.com/v1/browse/categories/{cid}/playlists"
#         params = {"limit": 50, "offset": 0, "country": country}
#         r = requests.get(url, headers=_auth_headers(token), params=params)

#         if r.status_code == 404:
#             print(f"[{i}/{len(category_ids)}] category {cid}: 404 (skipping)")
#             continue

#         r.raise_for_status()
#         data = r.json()

#         items = data.get("playlists", {}).get("items", [])
#         if not items:
#             print(f"[{i}/{len(category_ids)}] category {cid}: 0 playlists")
#             continue

#         added = 0
#         for p in items[:max_playlists_per_category]:
#             pid = p["id"]
#             if pid not in seen:
#                 seen.add(pid)
#                 all_playlist_ids.append(pid)
#                 added += 1

#         print(f"[{i}/{len(category_ids)}] category {cid}: +{added} playlists (total={len(all_playlist_ids)})")

#     return all_playlist_ids


# ---- playlist api call methods to retrieve a set of track_ids ----
def load_playlist_ids(path="playlist_ids.txt"):
    playlist_ids = []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()

            # skip blank lines or full-line comments
            if not line or line.startswith("#"):
                continue

            # allow inline comments
            playlist_id = line.split("#")[0].strip()

            if playlist_id:
                playlist_ids.append(playlist_id)

    return playlist_ids

def fetch_playlist_tracks(playlist_id, token):
    track_ids = set()

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    params = {"limit": 100}

    while url is not None:
        r = requests.get(url, headers=_auth_headers(token), params=params)
        r.raise_for_status()
        playlist = r.json()

        for item in playlist["items"]:
            if item["track"] is None:
                continue
            track = item["track"]
            if track["is_local"]:
                continue
            if track["id"] is None:
                continue

            track_ids.add(track["id"])

        url = playlist["next"]
        params = None  # keep this

    return track_ids


def collect_track_ids_from_playlists_ordered(playlist_ids, token, target=10000):
    seen = set()
    ordered_ids = []

    for i, pid in enumerate(playlist_ids, start=1):
        ids = fetch_playlist_tracks(pid, token)  #set
        added = 0

        for tid in ids:
            if tid not in seen:
                seen.add(tid)
                ordered_ids.append(tid)
                added += 1

        print(f"[{i}/{len(playlist_ids)}] {pid}: +{added} (total={len(seen)})")

        if target is not None and len(seen) >= target:
            break

    return ordered_ids, seen

def save_track_ids(track_ids, path):
    with open(path, "w") as f:
        for tid in track_ids:
            f.write(tid + "\n")

def load_track_ids(path):
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]

# ---- caches to store json data ----
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


# ---- methods to use cached json instead of many unneccesary API calls ----

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

def debug_categories_call(token):
    url = "https://api.spotify.com/v1/browse/categories"
    r = requests.get(url, headers=_auth_headers(token), params={"limit": 10, "offset": 0})

    print("STATUS:", r.status_code)
    print("FINAL URL:", r.url)          # <-- confirms endpoint + query params
    print("TOP KEYS:", list(r.json().keys()))  # <-- shows if 'categories' exists

    data = r.json()
    if "categories" not in data:
        print("NOT a categories response. Here's a snippet:")
        print(str(data)[:500])
        return

    items = data["categories"]["items"]
    print("FIRST 5 category (name, id):")
    for c in items[:5]:
        print(c["name"], "->", c["id"])

# main
def main():
    token = get_access_token(CLIENT_ID, CLIENT_SECRET)

    playlist_ids = load_playlist_ids("playlist_ids.txt")
    print("Playlists:", len(playlist_ids), playlist_ids[:5])

    track_ids, seen = collect_track_ids_from_playlists_ordered(
        playlist_ids,
        token,
        target=10_000
    )

    print("Tracks:", len(seen))
    save_track_ids(track_ids, "track_ids_10k.txt")

if __name__ == "__main__":
    main()