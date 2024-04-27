import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import requests
import json

def get_setlist(setlist_fm_id: str):
    #仮想マシンの8000番をmacの8000番と紐づけているため、仮想マシン上のCLIでこのコードを実行する場合は、urlにローカルホスト（仮想マシン）の8000番を指定しないといけない
    url = f"http://0.0.0.0:8000/setlists/{setlist_fm_id}"
    headers = {
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    return data

data = get_setlist("53ab83a1")

print(json.dumps(data, indent=2))


# lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'

# client_id = 'eed84f1ca1b2496fb69628e871630668'
# client_secret = '381e0a9c2b95490d82353d755c1d600f'
# client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(client_id, client_secret)
# spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# results = spotify.artist_top_tracks(lz_uri)

# for track in results['tracks'][:10]:
#     print('track    : ' + track['name'])
#     print('audio    : ' + track['preview_url'])
#     print('cover art: ' + track['album']['images'][0]['url'])
#     print()