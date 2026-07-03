import requests
import os

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

def search(query: str):
    url = f"{BASE_URL}/search/multi?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(url)
    return response.json().get("results", [])
