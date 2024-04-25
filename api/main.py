import requests
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import List

app = FastAPI()

class Song(BaseModel):
    index: int
    name: str
    artist: str
    original_artist: str
    is_tape: bool
    is_cover: bool
    is_medley_part: bool

class Setlist(BaseModel):
    artist_name: str
    #event_date: datetime
    location: str
    venue: str
    tour_name: str
    songs: List[Song]

@app.get("/setlists/{setlist_fm_id}", response_model=Setlist)
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
    #event_date = datetime.fromisoformat(data["eventDate"])
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
                song = Song(
                    index=index,
                    name=medley_part,
                    artist=artist_name,
                    original_artist=original_artist,
                    is_tape=is_tape,
                    is_cover=is_cover,
                    is_medley_part=is_medley_part
                )
                setlist_songs.append(song)

    setlist = Setlist(
        artist_name=artist_name,
        #event_date=event_date,
        location=city,
        venue=venue,
        tour_name=tour_name,
        songs=setlist_songs
    )

    return setlist

    
