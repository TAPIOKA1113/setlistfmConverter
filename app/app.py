import streamlit as st
import pandas as pd
#import chardet
import datetime
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import oauth2
from apiclient.discovery import build
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
access_token = ''
refresh_token = os.getenv("REFRESH_TOKEN") 
sp_oauth = oauth2.SpotifyOAuth(client_id=my_id,client_secret=my_secret,redirect_uri='http://localhost:3000',scope='playlist-modify-public')
token_info = sp_oauth.get_cached_token() 
youtube_api_key = os.getenv("YOUTUBE_API_KEY")

auth_encoded = base64.b64encode(f"{my_id}:{my_secret}".encode('utf-8')).decode('utf-8')
auth_headers = {
   'Authorization': f'Basic {auth_encoded}'
}
auth_data = {
   'grant_type': 'refresh_token',
   'refresh_token': refresh_token
}

def submit_setlist():
   global access_token
   api_choice = st.selectbox(
      "APIを選択してください",
      ('Spotify', 'YouTube')
   )
   url = st.text_input("URLを入力", placeholder="https://www.setlist.fm/")
   submit = st.button("作成")

   if submit:
      # ここで入力されたURLを処理する
      if api_choice == 'Spotify':
         if token_info == None:
            auth_url = 'https://accounts.spotify.com/api/token'
            response = requests.post(auth_url, headers=auth_headers, data=auth_data)
            access_token = response.json()['access_token']
            spotify = spotipy.Spotify(auth = access_token)

         last_hyphen_index = url.rfind("-")
         dot_html_index = url.rfind(".html")
         
         id_part = url[last_hyphen_index+1:dot_html_index]
         
         data = get_to_setlistfm(id_part)
         date_part = data['event_date'].split('T')[0]

         playlist = spotify.user_playlist_create(username, data['artist_name'] + '  ' + data['tour_name'] + '  (' + date_part + ')', public=True)
         
         for key in data['songs']:
            track_id = sp_search_song(key["name"], key['original_artist'])
            sp_add_playlist(playlist['id'], track_id)

         components.iframe("https://open.spotify.com/embed/playlist/" + playlist['id'] , height=500)
      
      elif api_choice == 'YouTube':
         videoId = 'JrGugZqMN1k'

         youtube = build('youtube', 'v3', developerKey=youtube_api_key)
         videos_response = youtube.videos().list(
            part='snippet,statistics',
            id='{},'.format(videoId)
         ).execute()
         # snippet
         snippetInfo = videos_response["items"][0]["snippet"]
         # 動画タイトル
         title = snippetInfo['title']
         # チャンネル名
         channeltitle = snippetInfo['channelTitle']
         st.write(channeltitle)
         st.write(title)


def sp_search_song(name: str, artist: str):
   spotify = spotipy.Spotify(auth = access_token)
   q = f"{quote_plus(name)} {quote_plus(artist)}"
   data = spotify.search(q, limit=1, offset=0, type='track', market="US")
   return data['tracks']['items'][0]['id'] #トラックURIを返す
   

def sp_add_playlist(playlist_id: str, track_id: str):
   spotify = spotipy.Spotify(auth = access_token)
   spotify.user_playlist_add_tracks(username, playlist_id, [track_id])

def get_to_setlistfm(id_part):
   #仮想マシンの8000番をmacの8000番と紐づけているため、仮想マシン上のCLIでこのコードを実行する場合は、urlにローカルホスト（仮想マシン）の8000番を指定しないといけない
   url = f"http://0.0.0.0:8000/setlists/{id_part}"
   headers = {
   "Accept": "application/json",
   }
   response = requests.get(url, headers=headers)
   response.raise_for_status()
   data = response.json()

   return data

def main():
   st.title("プレイリスト作成アプリ")
   st.write('このアプリは[setlist.fm](https://www.setlist.fm/)のURLからSpotifyのプレイリストを作成するアプリです')
   submit_setlist()

if __name__ == "__main__":
   main()
