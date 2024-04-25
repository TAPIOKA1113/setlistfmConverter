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
token = "BQBLsKCWcjWOiMWgrwUhK4ga8wTrWJyFGadB2sgTohsbaTLod4KX2_2vgFfEciI2s9CHHrkeAvAHDxbJw9wsA4g3tIiZWV9TKNyPKLCCjgDGiEq5Z3sYtn2o439Xnz4xjnPliRPhQP3DM60PGdK2HiaTw4D_6_ja6wR551q2rqlyi_6UmxHv_wdSDNQEdTzQKr6p4IC6ZtzdFy9O6gfTs3eLTfeZTww5-WxALRPv_IIbC0gUKF9jrVj7HSiGfQAxc2c"
spotify = spotipy.Spotify(auth = token)


def submit_setlist():
   url = st.text_input("URLを入力してください")
   submit = st.button("送信")
   if submit:
       # ここで入力されたURLを処理する
       last_hyphen_index = url.rfind("-")
       dot_html_index = url.rfind(".html")

       id_part = url[last_hyphen_index+1:dot_html_index]
       
      #  create_playlist()
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
        search_song(key["name"], key['original_artist'])

       return data
       
def create_playlist():
   spotify.user_playlist_create(username, "myplaylist", public=False)

def search_song(name: str, artist: str):
   q = f"{quote_plus(name)} {quote_plus(artist)}"
   data = spotify.search(q, limit=1, offset=0, type='track', market="US")
   st.write(data)

def add_playlist():
   
def main():
   st.title("プレイリスト作成アプリ")
   st.write('このアプリはsetlist.fm(https://www.setlist.fm/)のURLからSpotifyのプレイリストを作成するアプリです')
   submit_setlist()

if __name__ == "__main__":
   main()
