import streamlit as st
import pandas as pd
import chardet
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
load_dotenv()

username = os.getenv("USER_NAME")
my_id = os.getenv("MY_ID")
my_secret = os.getenv("MY_SECRET")
token = 'BQAWOt4RIw7RDgR4N13VjVOwWlr2f_mX8EYAtVjyhGBjbhym4LPwdnXyzvOFdNpnRHkwYpC5n7Ix5D0z0utqBhP1q6khI0r-egDSLOfJvXXxnG7ql6oHFXZT0P0AIkVnEsoDnuEftUNQ0bCGZ81DJ6QRzUgmAddwiUuh-MUxQ5JXXMEJcnvgu0B6TmwRoCX6o9zFAfYxztXrBL4wOdll7W2nr9TzPT4eUsNu8kyhP283HX8xk1hq19Xyr4KAwQw'
spotify = spotipy.Spotify(auth = token)


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
   #st.write(data['tracks']['items'][0]['id'])
   #st.write(data)
   return data['tracks']['items'][0]['id'] #トラックURIを返す
   

def add_playlist(playlist_id: str, track_id: str):
   spotify.user_playlist_add_tracks(username, playlist_id, [track_id])

def main():
   st.title("プレイリスト作成アプリ")
   st.write('このアプリは[setlist.fm](https://www.setlist.fm/)のURLからSpotifyのプレイリストを作成するアプリです')
   submit_setlist()
  

if __name__ == "__main__":
   main()
