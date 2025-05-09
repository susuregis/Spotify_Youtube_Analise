

import os
from googleapiclient.discovery import build
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotify_youtube_analysis import SpotifyYouTubeAnalyzer

def main():
    print("\n=== SPOTIFY & YOUTUBE DATA ANALYSIS DEMO ===\n")

    # API Configuration
    YOUTUBE_API_KEY = 'AIzaSyD877MaanmjiisQFwP9AsmE6QAhze7vwjc'
    SPOTIFY_CLIENT_ID = "2543e134da3d42edbf4934f4d9a52d84"
    SPOTIFY_CLIENT_SECRET = "d84d737fe68249dd913f5379a7d3e440"
    SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8888/callback"

    # Initialize API clients
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="user-library-read user-top-read playlist-read-private user-read-recently-played"
    ))

    # Demo 1: Basic Spotify API usage - Get user's saved tracks
    print("=== DEMO 1: SPOTIFY SAVED TRACKS ===")
    results = sp.current_user_saved_tracks(limit=5)
    
    print("Your saved tracks:")
    for i, item in enumerate(results['items']):
        track = item['track']
        print(f"{i+1}. {track['name']} – {track['artists'][0]['name']}")
    
    # Demo 2: Basic YouTube API usage - Get trending videos
    print("\n=== DEMO 2: YOUTUBE TRENDING VIDEOS ===")
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        chart="mostPopular",
        regionCode="BR",
        maxResults=5
    )
    response = request.execute()
    
    print("Trending videos:")
    for i, item in enumerate(response['items']):
        print(f"{i+1}. {item['snippet']['title']} - {item['statistics'].get('viewCount', 0)} views")
        print("\n=== DASHBOARD DE ANÁLISE ===")
    print("Para acessar o dashboard interativo com recursos avançados, execute:")
    print("python dashboard.py")
    
    # Show available options
    print("\nOpções disponíveis:")
    print("1. Iniciar o dashboard completo (python dashboard.py)")
    print("2. Iniciar o dashboard simplificado (python simple_dash.py)")
    print("3. Executar pipeline de análise completo")
    print("4. Sair")
    
    choice = input("\nSelecione uma opção (1-4): ")
    
    if choice == "1":
        print("\nIniciando o dashboard completo...")
        os.system("python dashboard.py")
    elif choice == "2":
        print("\nIniciando o dashboard simplificado...")
        os.system("python simple_dash.py")
    elif choice == "3":
        print("\nExecutando pipeline de análise completo...")
        analyzer = SpotifyYouTubeAnalyzer()
        results = analyzer.run()
        print("\nAnálise completa! Verifique a pasta 'visualizations' para resultados.")

if __name__ == "__main__":
    main()





