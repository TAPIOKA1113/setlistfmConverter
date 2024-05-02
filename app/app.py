import streamlit as st
import pandas as pd
#import chardet
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import oauth2
import sys
import json
import re
from urllib.parse import quote_plus
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv
import base64
from datetime import datetime
load_dotenv()

username = 'gnti7y5zkih9elje0lzd4b84g'  
my_id = '7ca33bfaf9ce41fbbc43a2abeec4e53d'
my_secret = '79b0572f34084761b508cbca34bd3512'
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
   'refresh_token': 'AQDbn04HT4tNMovNt2r3j_xiNOz2qJPXrsIszfJEH7MfEQCR2ZBGsk9vrBeYosvqfy92UM2ciFLONzwd3K8J63wklBh9NBGfIypgOg-wgRpjGiYuPYD6gc933gNR_TpnhNU'
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
         
         check_url = re.match(r'https://www.setlist.fm/', url)

         if check_url == None:
            st.write('URLが正しくありません')
            return

         id_part = generate_url(url)
         
         data = get_setlist(id_part)
         date_part = data['event_date'].strftime('%Y-%m-%d')
         playlist = spotify.user_playlist_create(username, data['artist_name'] + '  ' + data['tour_name'] + '  (' + date_part + ')', public=True)
         
         for key in data['songs']:
            track_id = sp_search_song(key["name"], key['original_artist'])
            sp_add_playlist(playlist['id'], track_id)

         components.iframe("https://open.spotify.com/embed/playlist/" + playlist['id'] , height=500)
      
      elif api_choice == 'YouTube':

         check_url = re.match(r'https://www.setlist.fm/', url)

         if check_url == None:
            st.write('URLが正しくありません')
            return 

         id_part = generate_url(url)

         data = get_to_setlistfm(id_part)
         date_part = data['event_date'].strftime('%Y-%m-%d')
         
         st.write(data)
         st.write(date_part)
         
         title = 'B-life Test 10分〜15分'
         description = '再生時間が10分〜15分の動画の再生リスト'
         privacy_status = 'public'  # 'private'

         # 新規再生リストを追加
         # https://developers.google.com/youtube/v3/docs/playlists/insert
         youtube_auth = build('youtube', 'v3', developerKey=youtube_api_key)
         
         playlists_insert_response = youtube_auth.playlists().insert(
            part="snippet, status",
            body=dict(
               snippet=dict(
                  title=title,
                  description=description
               ),
               status=dict(
                  privacyStatus=privacy_status
               )
            )
         ).execute()

def sp_search_song(name: str, artist: str):
   spotify = spotipy.Spotify(auth = access_token)
   q = f"{quote_plus(name)} {quote_plus(artist)}"
   data = spotify.search(q, limit=1, offset=0, type='track', market="US")
   return data['tracks']['items'][0]['id'] #トラックURIを返す
   

def sp_add_playlist(playlist_id: str, track_id: str):
   spotify = spotipy.Spotify(auth = access_token)
   spotify.user_playlist_add_tracks(username, playlist_id, [track_id])


def generate_url(url): #setlist.fmのURLからID部分を取得する
   last_hyphen_index = url.rfind("-")
   dot_html_index = url.rfind(".html")
         
   id_part = url[last_hyphen_index+1:dot_html_index]

   return id_part

def get_setlist(setlist_fm_id: str):
   url = f"https://api.setlist.fm/rest/1.0/setlist/{setlist_fm_id}"
   headers = {
      "x-api-key": "rvH9s-nOQE4FOGgLByWj1VfmjzqIaEt5Q8wB",
      "Accept": "application/json",
   }
   response = requests.get(url, headers=headers)
   response.raise_for_status()
   data = response.json()

   artist_name = data["artist"]["name"]
   event_date = datetime.strptime(data["eventDate"], '%d-%m-%Y')
   venue_data = data["venue"]
   city_data = venue_data["city"]
   country = city_data["country"]["name"]
   city = f"{city_data['name']}, {country}"
   venue = venue_data["name"]
   tour_name = data["tour"]["name"] if "tour" in data else ""

   setlist_songs = []
   index = 0
   for set_data in data["sets"]["set"]:
      songs = set_data["song"]
      for song_data in songs:
         index += 1
         song_name = song_data["name"]
         is_tape = song_data.get("tape", False)
         is_cover = "cover" in song_data
         medley_parts = song_name.split(" / ")
         is_medley_part = len(medley_parts) > 1

         for medley_part in medley_parts:
               original_artist = song_data["cover"]["name"] if is_cover else artist_name
               song = {
                  'index': index,
                  'name': medley_part,
                  'artist': artist_name,
                  'original_artist': original_artist,
                  'is_tape': is_tape,
                  'is_cover': is_cover,
                  'is_medley_part': is_medley_part
               }
               setlist_songs.append(song)

   setlist = {
      'artist_name':artist_name,
      'event_date': event_date,
      'location': city,
      'venue=': venue,
      'tour_name': tour_name,
      'songs': setlist_songs
   }

   return setlist


def main():
   st.title("プレイリスト作成アプリ")
   st.write('このアプリは[setlist.fm](https://www.setlist.fm/)のURLからSpotifyのプレイリストを作成するアプリです')
   submit_setlist()

if __name__ == "__main__":
   main()
