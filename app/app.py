import streamlit as st
import pandas as pd
#import chardet
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import json
import re
from urllib.parse import quote_plus
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv
import base64
load_dotenv()

username = os.getenv("USER_NAME")
my_id = os.getenv("MY_ID")
my_secret = os.getenv("MY_SECRET")
access_token = 'BQAWOt4RIw7RDgR4N13VjVOwWlr2f_mX8EYAtVjyhGBjbhym4LPwdnXyzvOFdNpnRHkwYpC5n7Ix5D0z0utqBhP1q6khI0r-egDSLOfJvXXxnG7ql6oHFXZT0P0AIkVnEsoDnuEftUNQ0bCGZ81DJ6QRzUgmAddwiUuh-MUxQ5JXXMEJcnvgu0B6TmwRoCX6o9zFAfYxztXrBL4wOdll7W2nr9TzPT4eUsNu8kyhP283HX8xk1hq19Xyr4KAwQw'
refresh_token = 'AQDbn04HT4tNMovNt2r3j_xiNOz2qJPXrsIszfJEH7MfEQCR2ZBGsk9vrBeYosvqfy92UM2ciFLONzwd3K8J63wklBh9NBGfIypgOg-wgRpjGiYuPYD6gc933gNR_TpnhNU'
spotify = spotipy.Spotify(auth = access_token)

auth_encoded = base64.b64encode(f"{my_id}:{my_secret}".encode('utf-8')).decode('utf-8')
auth_headers = {
    'Authorization': f'Basic {auth_encoded}'
}
auth_data = {
    'grant_type': 'refresh_token',
    'refresh_token': refresh_token
}

def submit_setlist():
   url = st.text_input("URLを入力", placeholder="https://www.setlist.fm/")
   submit = st.button("作成")
   if submit:
       # ここで入力されたURLを処理する
       last_hyphen_index = url.rfind("-")
       dot_html_index = url.rfind(".html")
       
       id_part = url[last_hyphen_index+1:dot_html_index]
       
       #仮想マシンの8000番をmacの8000番と紐づけているため、仮想マシン上のCLIでこのコードを実行する場合は、urlにローカルホスト（仮想マシン）の8000番を指定しないといけない
       url = f"http://0.0.0.0:8000/setlists/{id_part}"
       headers = {
        "Accept": "application/json",
       }
       response = requests.get(url, headers=headers)
       if response.status_code != 200:
          auth_response = requests.post('https://accounts.spotify.com/api/token', headers=auth_headers, data=auth_data)
          access_token = auth_response.json()['access_token']
       response.raise_for_status()
       data = response.json()
       date_part = data['event_date'].split('T')[0]

       playlist = spotify.user_playlist_create(username, data['artist_name'] + '  ' + data['tour_name'] + '  (' + date_part + ')', public=True)
      
       for key in data['songs']:
        #st.write(key['name']) # nameのみ参照
        track_id = search_song(key["name"], key['original_artist'])
        add_playlist(playlist['id'], track_id)

       components.iframe("https://open.spotify.com/embed/playlist/" + playlist['id'] , height=500)

       return data
   

def search_song(name: str, artist: str):
   q = f"{quote_plus(name)} {quote_plus(artist)}"
   data = spotify.search(q, limit=1, offset=0, type='track', market="US")
   return data['tracks']['items'][0]['id'] #トラックURIを返す
   

def add_playlist(playlist_id: str, track_id: str):
   spotify.user_playlist_add_tracks(username, playlist_id, [track_id])

def main():
   st.title("プレイリスト作成アプリ")
   st.write('このアプリは[setlist.fm](https://www.setlist.fm/)のURLからSpotifyのプレイリストを作成するアプリです')
   submit_setlist()
  

if __name__ == "__main__":
   main()
