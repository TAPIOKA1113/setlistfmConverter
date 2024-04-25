import streamlit as st
import pandas as pd
import chardet
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import json
import re

username = '6w0j4q09g6iki4c318olak6a4' 
my_id ='eed84f1ca1b2496fb69628e871630668' 
my_secret = '381e0a9c2b95490d82353d755c1d600f' 
token = "BQAJuFkB4naZUSDPg8-d5-krObb6vrQMq44McFEQ-9mzcC4L0-Xk-uiPTcVg-4FsAQEQFAKtJbSXUDLzDnBnOm1XhzZlvdWaMb0urWn9ZNKV2Bq2zyZ3xoTO3sXhZEZ1kbu6YFeGjEhhBAhg4W0VXeG69y3e603_b22DjeLwsCuQTKr30Wd1kAsxsCM_2Ht7et602KElpXB5snyPBN9boASB_oj3soW5alxBjw"
spotify = spotipy.Spotify(auth = token)


def submit_setlist():
   url = st.text_input("URLを入力してください")
   submit = st.button("送信")
   if submit:
       # ここで入力されたURLを処理する
       last_hyphen_index = url.rfind("-")
       dot_html_index = url.rfind(".html")

       id_part = url[last_hyphen_index+1:dot_html_index]
       
       #create_playlist()
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

       return data
       
def create_playlist():
   spotify.user_playlist_create(username, "myplaylist", public=False)

#def add_playlist():

   

def main():
   st.title("プレイリスト作成アプリ")
   st.write('このアプリはsetlist.fm(https://www.setlist.fm/)のURLからSpotifyのプレイリストを作成するアプリです')
   submit_setlist()
   create_playlist()


if __name__ == "__main__":
   main()
