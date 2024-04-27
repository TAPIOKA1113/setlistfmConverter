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

username = 'gnti7y5zkih9elje0lzd4b84g' 
my_id ='7ca33bfaf9ce41fbbc43a2abeec4e53d' 
my_secret = '79b0572f34084761b508cbca34bd3512' 
token = ""
spotify = spotipy.Spotify(auth = token)


def submit_setlist():
   url = st.text_input("URLを入力", placeholder="https://www.setlist.fm/")
   submit = st.button("作成")
   if submit:
       # ここで入力されたURLを処理する
       last_hyphen_index = url.rfind("-")
       dot_html_index = url.rfind(".html")

       id_part = url[last_hyphen_index+1:dot_html_index]
       
       playlist_id = create_playlist()
       #仮想マシンの8000番をmacの8000番と紐づけているため、仮想マシン上のCLIでこのコードを実行する場合は、urlにローカルホスト（仮想マシン）の8000番を指定しないといけない
       url = f"http://0.0.0.0:8000/setlists/{id_part}"
       headers = {
        "Accept": "application/json",
       }
       response = requests.get(url, headers=headers)
       response.raise_for_status()
       data = response.json()
      
       for key in data['songs']:
        #st.write(key['name']) # nameのみ参照
        track_id = search_song(key["name"], key['original_artist'])
        add_playlist(playlist_id, track_id)
       

       components.iframe("https://open.spotify.com/embed/playlist/" + playlist_id , height=500)

       return data
       
def create_playlist():
   data = spotify.user_playlist_create(username, "myplaylist", public=True)
   #st.write(data['id'])
   return data['id']  #プレイリストIDを返す
   

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
