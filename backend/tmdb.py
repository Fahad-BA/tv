import requests
import os

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

def search(query: str):
    url = f"{BASE_URL}/search/multi?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(url)
    return response.json().get("results", [])

def get_show_details(tmdb_id: int):
    url = f"{BASE_URL}/tv/{tmdb_id}?api_key={TMDB_API_KEY}"
    return requests.get(url).json()

def get_season_details(tmdb_id: int, season_number: int):
    url = f"{BASE_URL}/tv/{tmdb_id}/season/{season_number}?api_key={TMDB_API_KEY}"
    return requests.get(url).json()
