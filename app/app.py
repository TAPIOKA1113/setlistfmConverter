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

username = '6w0j4q09g6iki4c318olak6a4' 
my_id ='eed84f1ca1b2496fb69628e871630668' 
my_secret = '381e0a9c2b95490d82353d755c1d600f' 
token = "BQC-lDGOpx8dqIwy26HJfTiOn9hoAk-ECFk8YuoM1GElCQ04FieguGcxxKSd6SBcqcT7-kPV_mqQco2nYMTTLX8iI0oL_Oqo1Ri_s1owCyw3oEdOsDSe7j1Pxf7mm8_3FbHJhTgiJTE6oF49H2IKRdEr9zL0YsGZxDUtM-MPAoi_IhiwYwcwGR6jvMX601euty4NAo8mqn8TwVQNQdV3iKCwoVZb5wHA5twxB2jAVQCHdFaeOuIOav9ybeMKspSkVJA"
spotify = spotipy.Spotify(auth = token)


def submit_setlist():
   url = st.text_input("URLを入力してください")
   submit = st.button("送信")
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
        st.write(key['name']) # nameのみ参照
        track_id = search_song(key["name"], key['original_artist'])
        add_playlist(playlist_id, track_id)

       return data
       
def create_playlist():
   data = spotify.user_playlist_create(username, "myplaylist", public=False)
   st.write(data['id'])
   return data['id']  #プレイリストIDを返す
   

def search_song(name: str, artist: str):
   q = f"{quote_plus(name)} {quote_plus(artist)}"
   data = spotify.search(q, limit=1, offset=0, type='track', market="US")
   st.write(data['tracks']['items'][0]['id'])
   st.write(data)
   return data['tracks']['items'][0]['id'] #トラックURIを返す
   

def add_playlist(playlist_id: str, track_id: str):
   spotify.user_playlist_add_tracks(username, playlist_id, [track_id])

def main():
   st.title("プレイリスト作成アプリ")
   st.write('このアプリはsetlist.fm(https://www.setlist.fm/)のURLからSpotifyのプレイリストを作成するアプリです')
   submit_setlist()

if __name__ == "__main__":
   main()
