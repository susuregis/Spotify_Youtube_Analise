"""
Spotify & YouTube Data Analysis and Correlation Tool
Este script extrai dados das APIs do Spotify e YouTube, realiza análises de tendências de músicas e vídeos,
identifica correlações, analisa o engajamento regional e cria visualizações interativas.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import traceback # Adicionado para melhor depuração de erros da API
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
try:
    from googleapiclient.discovery import build
except ImportError:
    print("Google API Client não encontrado. As chamadas à API do YouTube serão simuladas.")

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except ImportError:
    print("Spotipy não encontrado. As chamadas à API do Spotify serão simuladas.")


# Configuração (credenciais configuradas diretamente)
SPOTIFY_CLIENT_ID = "2543e134da3d42edbf4934f4d9a52d84"
SPOTIFY_CLIENT_SECRET = "d84d737fe68249dd913f5379a7d3e440"
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8888/callback" # Atualizado de localhost
YOUTUBE_API_KEY = "AIzaSyD877MaanmjiisQFwP9AsmE6QAhze7vwjc" # Credenciais fornecidas pelo usuário



class SpotifyYouTubeAnalyzer:
    def __init__(self):
        """Inicializa o analisador de dados do Spotify e YouTube."""
        self.spotify_tracks_df = None
        self.spotify_playlists_df = None
        self.spotify_artists_df = None
        self.youtube_videos_df = None
        self.youtube_categories_df = None
        self.correlation_df = None
        
    def extract_spotify_data(self):
        """Extrai os dados do Spotify usando a API."""
        print("Extraindo dados do Spotify via API...")
        try:
            # Verificar se temos credenciais configuradas
            if SPOTIFY_CLIENT_ID == "seu_client_id_spotify" or SPOTIFY_CLIENT_SECRET == "seu_client_secret_spotify" or \
               not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
                print("ERRO: Credenciais do Spotify não configuradas, são placeholders ou estão vazias. Verifique SPOTIFY_CLIENT_ID e SPOTIFY_CLIENT_SECRET.")
                self.spotify_tracks_df = pd.DataFrame()
                self.spotify_playlists_df = pd.DataFrame()
                self.spotify_artists_df = pd.DataFrame()
                return self.spotify_tracks_df, self.spotify_playlists_df, self.spotify_artists_df
                
            # Inicializar o cliente Spotify
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                redirect_uri=SPOTIFY_REDIRECT_URI,
                scope="user-library-read user-top-read playlist-read-private user-read-recently-played"
            ))
            
            # Extrair tracks salvos (máximo 50)
            print("Buscando suas faixas salvas via API...")
            saved_tracks_response = sp.current_user_saved_tracks(limit=50)
            tracks = []

            if not saved_tracks_response or not saved_tracks_response.get('items'):
                print("Aviso: A API do Spotify não retornou itens de faixas salvas ou a resposta foi inválida.")
            else:
                print(f"API retornou {len(saved_tracks_response['items'])} itens de faixas salvas para processar.")
                for item in saved_tracks_response['items']:
                    track = item.get('track') # Use .get() for safer access

                    if not track or not track.get('id'):
                        print(f"Aviso: Item de faixa inválido ou sem ID encontrado. Item: {item}")
                        continue

                    track_id = track['id']
                    
                    # Inicializar track_data com informações básicas e seguras
                    track_data = {
                        'id': track_id,
                        'name': track.get('name'),
                        'artist': track.get('artists', [{}])[0].get('name') if track.get('artists') else None,
                        'artist_id': track.get('artists', [{}])[0].get('id') if track.get('artists') else None,
                        'album': track.get('album', {}).get('name'),
                        'popularity': track.get('popularity'),
                        'duration_ms': track.get('duration_ms'),
                        'explicit': track.get('explicit'),
                        'added_at': item.get('added_at')
                    }
                    
                    # Obter features de áudio para cada faixa
                    audio_features_data = None
                    try:
                        # sp.audio_features espera uma lista de track_ids
                        audio_features_list = sp.audio_features([track_id]) 
                        if audio_features_list and len(audio_features_list) > 0 and audio_features_list[0] is not None:
                            audio_features_data = audio_features_list[0]
                        else:
                            print(f"Aviso: Não foram encontradas features de áudio para a faixa ID: {track_id}")
                    except Exception as e_af:
                        print(f"Erro ao buscar features de áudio para a faixa ID {track_id}: {e_af}")
                        # Continuar sem audio features se a chamada falhar
                    
                    # Adicionar features de áudio se disponíveis
                    if audio_features_data:
                        audio_keys = ['danceability', 'energy', 'key', 'loudness', 'mode', 
                                    'speechiness', 'acousticness', 'instrumentalness', 
                                    'liveness', 'valence', 'tempo']
                        for key in audio_keys:
                            track_data[key] = audio_features_data.get(key) # Usar .get() para segurança
                    else: # Garantir que as colunas existem mesmo que não haja dados de audio features
                        audio_keys_default = ['danceability', 'energy', 'key', 'loudness', 'mode', 
                                    'speechiness', 'acousticness', 'instrumentalness', 
                                    'liveness', 'valence', 'tempo']
                        for key_default in audio_keys_default:
                             track_data[key_default] = None
                        
                    tracks.append(track_data)
            
            if not tracks:
                print("Aviso: Nenhuma faixa válida foi processada a partir dos dados da API do Spotify.")

            # Extrair playlists do usuário
            print("Buscando suas playlists...")
            playlists_response = sp.current_user_playlists(limit=20)
            playlists = []
            
            for playlist in playlists_response['items']:
                playlist_data = {
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'description': playlist['description'],
                    'owner': playlist['owner']['display_name'],
                    'tracks_total': playlist['tracks']['total'],
                    'followers': 0,  # Requer chamada adicional
                    'image_url': playlist['images'][0]['url'] if playlist['images'] else ''
                }
                playlists.append(playlist_data)
            
            # Extrair informações de artistas
            print("Buscando informações de artistas...")
            artist_ids = list(set(item['artist_id'] for item in tracks))[:10]  # Limitado a 10 artistas
            artists_data = []
            
            if artist_ids:
                artists_response = sp.artists(artist_ids)
                
                for artist in artists_response['artists']:
                    artist_data = {
                        'id': artist['id'],
                        'name': artist['name'],
                        'followers': artist['followers']['total'],
                        'popularity': artist['popularity'],
                        'genres': ', '.join(artist['genres']),
                        'image_url': artist['images'][0]['url'] if artist['images'] else ''
                    }
                    artists_data.append(artist_data)
            
            # Converter para DataFrames
            self.spotify_tracks_df = pd.DataFrame(tracks)
            self.spotify_playlists_df = pd.DataFrame(playlists)
            self.spotify_artists_df = pd.DataFrame(artists_data)
            
            print(f"Extraídas {len(self.spotify_tracks_df)} faixas do Spotify via API")
            print(f"Extraídas {len(self.spotify_playlists_df)} playlists via API")
            print(f"Extraídos {len(self.spotify_artists_df)} artistas via API")
            
            return self.spotify_tracks_df, self.spotify_playlists_df, self.spotify_artists_df
            
        except Exception as e:
            print(f"ERRO na extração de dados do Spotify via API: {e}")
            print(traceback.format_exc())
            # Retornar DataFrames vazios em caso de erro na API
            self.spotify_tracks_df = pd.DataFrame()
            self.spotify_playlists_df = pd.DataFrame()
            self.spotify_artists_df = pd.DataFrame()
            return self.spotify_tracks_df, self.spotify_playlists_df, self.spotify_artists_df
    
    def extract_youtube_data(self, region_code='BR'):
        """Extrai os dados do YouTube em tempo real usando a API."""
        print(f"Extraindo dados do YouTube para região {region_code} via API...")
        try:
            # Verificar se temos a chave de API configurada
            if YOUTUBE_API_KEY == "sua_api_key_youtube" or not YOUTUBE_API_KEY:
                print("ERRO: Chave da API do YouTube não configurada, é placeholder ou está vazia. Verifique YOUTUBE_API_KEY.")
                self.youtube_videos_df = pd.DataFrame()
                self.youtube_categories_df = pd.DataFrame()
                return self.youtube_videos_df, self.youtube_categories_df
                
            # Inicializar o cliente YouTube
            youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
            
            # 1. Buscar vídeos mais populares da região
            print(f"Buscando vídeos populares em {region_code} via API...")
            videos_request = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                chart="mostPopular",
                regionCode=region_code,
                maxResults=50
            )
            videos_response = videos_request.execute()
            
            videos = []
            video_ids = []
            
            for item in videos_response.get('items', []):
                video_ids.append(item['id'])
                
                # Extrair dados do vídeo
                video_data = {
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'channel_title': item['snippet']['channelTitle'],
                    'channel_id': item['snippet']['channelId'],
                    'published_at': item['snippet']['publishedAt'],
                    'category_id': item['snippet'].get('categoryId', ''),
                    'category_name': '',  # Será preenchido depois
                    'category_name_pt': '',  # Será preenchido depois
                    'duration': item['contentDetails']['duration'],
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'like_count': int(item['statistics'].get('likeCount', 0)),
                    'comment_count': int(item['statistics'].get('commentCount', 0)),
                    'region_code': region_code
                }
                
                # Calcular taxa de engajamento
                if video_data['view_count'] > 0:
                    engagement = (video_data['like_count'] + video_data['comment_count']) / video_data['view_count']
                    video_data['engagement_rate'] = engagement
                else:
                    video_data['engagement_rate'] = 0
                    
                videos.append(video_data)
            
            # 2. Buscar informações de categorias
            print("Buscando informações de categorias...")
            categories_request = youtube.videoCategories().list(
                part="snippet",
                regionCode=region_code
            )
            categories_response = categories_request.execute()
            
            categories = []
            category_map = {}  # Para mapear id -> nome
            category_pt_map = {}  # Tradução aproximada para português
            
            for item in categories_response.get('items', []):
                category_id = item['id']
                title = item['snippet']['title']
                
                # Tradução aproximada (ideal seria usar um serviço de tradução)
                title_pt = self._translate_category(title)
                
                category_map[category_id] = title
                category_pt_map[category_id] = title_pt
                
                category_data = {
                    'id': category_id,
                    'title': title,
                    'title_pt': title_pt
                }
                categories.append(category_data)
            
            # Preencher nomes de categorias nos vídeos
            for video in videos:
                cat_id = video['category_id']
                video['category_name'] = category_map.get(cat_id, 'Unknown')
                video['category_name_pt'] = category_pt_map.get(cat_id, 'Desconhecida')
            
            # Converter para DataFrames
            self.youtube_videos_df = pd.DataFrame(videos)
            self.youtube_categories_df = pd.DataFrame(categories)
            
            print(f"Extraídos {len(self.youtube_videos_df)} vídeos do YouTube via API")
            print(f"Extraídas {len(self.youtube_categories_df)} categorias via API")
            
            return self.youtube_videos_df, self.youtube_categories_df
            
        except Exception as e:
            print(f"ERRO na extração de dados do YouTube via API: {str(e)}")
            print(traceback.format_exc())
            # Retornar DataFrames vazios em caso de erro na API
            self.youtube_videos_df = pd.DataFrame()
            self.youtube_categories_df = pd.DataFrame()
            return self.youtube_videos_df, self.youtube_categories_df
            
    def _translate_category(self, category):
        """Traduz categorias do YouTube para português (versão simples)."""
        translations = {
            'Film & Animation': 'Filmes e Animações',
            'Autos & Vehicles': 'Automóveis e Veículos',
            'Music': 'Música',
            'Pets & Animals': 'Animais de Estimação',
            'Sports': 'Esportes',
            'Gaming': 'Jogos',
            'People & Blogs': 'Pessoas e Blogs',
            'Comedy': 'Comédia',
            'Entertainment': 'Entretenimento',
            'News & Politics': 'Notícias e Política',
            'Howto & Style': 'Tutoriais e Estilo',
            'Education': 'Educação',
            'Science & Technology': 'Ciência e Tecnologia',
            'Nonprofits & Activism': 'ONGs e Ativismo',
            'Travel & Events': 'Viagens e Eventos'
        }
        return translations.get(category, category)
    
    def analyze_spotify_trends(self):
        """Analisa tendências nos dados do Spotify."""
        print("Analisando tendências do Spotify...")
        
        if self.spotify_tracks_df is None or self.spotify_artists_df is None:
            print("Sem dados do Spotify para analisar. Por favor, extraia os dados primeiro.")
            return None
        
        analysis = {}
        
        # Top artistas por contagem de faixas
        artist_counts = self.spotify_tracks_df['artist'].value_counts().reset_index()
        artist_counts.columns = ['artist', 'track_count']
        analysis['top_artists_by_count'] = artist_counts.head(10)
        
        # Top gêneros
        if 'genres' in self.spotify_artists_df.columns:
            # Criar uma lista de todos os gêneros separando os valores por vírgulas
            all_genres = self.spotify_artists_df['genres'].str.split(', ').explode().dropna()
            genre_counts = all_genres.value_counts().reset_index()
            genre_counts.columns = ['genre', 'count']
            analysis['top_genres'] = genre_counts.head(10)
        
        # Popularidade média das faixas
        analysis['avg_track_popularity'] = self.spotify_tracks_df['popularity'].mean()
        
        # Distribuição de características de áudio
        audio_features = ['danceability', 'energy', 'speechiness', 'acousticness', 
                          'instrumentalness', 'liveness', 'valence']
        
        feature_means = {}
        for feature in audio_features:
            if feature in self.spotify_tracks_df.columns:
                feature_means[feature] = self.spotify_tracks_df[feature].mean()
        
        analysis['audio_feature_means'] = feature_means
        
        # Distribuição de duração
        if 'duration_ms' in self.spotify_tracks_df.columns:
            self.spotify_tracks_df['duration_min'] = self.spotify_tracks_df['duration_ms'] / 60000
            analysis['avg_duration_min'] = self.spotify_tracks_df['duration_min'].mean()
            analysis['max_duration_min'] = self.spotify_tracks_df['duration_min'].max()
            analysis['min_duration_min'] = self.spotify_tracks_df['duration_min'].min()
        
        return analysis
    
    def analyze_youtube_trends(self):
        """Analisa tendências nos dados do YouTube."""
        print("Analisando tendências do YouTube...")
        
        if self.youtube_videos_df is None:
            print("Sem dados do YouTube para analisar. Por favor, extraia os dados primeiro.")
            return None
        
        analysis = {}
        
        # Top categorias por contagem
        if 'category_name' in self.youtube_videos_df.columns:
            category_counts = self.youtube_videos_df['category_name'].value_counts().reset_index()
            category_counts.columns = ['category', 'count']
            analysis['top_categories_by_count'] = category_counts
        
        # Top canais por contagem de vídeos
        channel_counts = self.youtube_videos_df['channel_title'].value_counts().reset_index()
        channel_counts.columns = ['channel', 'count']
        analysis['top_channels_by_count'] = channel_counts.head(10)
        
        # Médias de visualizações, likes e comentários
        analysis['avg_view_count'] = self.youtube_videos_df['view_count'].mean()
        analysis['avg_like_count'] = self.youtube_videos_df['like_count'].mean()
        analysis['avg_comment_count'] = self.youtube_videos_df['comment_count'].mean()
        analysis['avg_engagement_rate'] = self.youtube_videos_df['engagement_rate'].mean()
        
        # Converter timestamps de publicação para datetime e analisar distribuição por dia
        if 'published_at' in self.youtube_videos_df.columns:
            self.youtube_videos_df['published_date'] = pd.to_datetime(self.youtube_videos_df['published_at'])
            self.youtube_videos_df['publish_day'] = self.youtube_videos_df['published_date'].dt.day_name()
            day_counts = self.youtube_videos_df['publish_day'].value_counts().reset_index()
            day_counts.columns = ['day', 'count']
            analysis['publish_day_distribution'] = day_counts
        
        return analysis    
    
    
    def correlate_spotify_youtube(self, use_real_time_data=False):
        """Tenta correlacionar faixas do Spotify com vídeos do YouTube."""
        print(f"Iniciando correlate_spotify_youtube... (Tempo real: {use_real_time_data})")

        # Check 1: DataFrames exist and are not empty
        if self.spotify_tracks_df is None or self.spotify_tracks_df.empty or \
           self.youtube_videos_df is None or self.youtube_videos_df.empty:
            print("Dados insuficientes (None ou vazios) para correlação.")
            self.correlation_df = pd.DataFrame()
            return self.correlation_df
        print("DataFrames iniciais verificados (existem e não estão vazios).")

        # Check 2: Necessary columns exist
        if 'name' not in self.spotify_tracks_df.columns or 'title' not in self.youtube_videos_df.columns:
             print("Colunas 'name' (Spotify) ou 'title' (YouTube) não encontradas.")
             self.correlation_df = pd.DataFrame()
             return self.correlation_df
        print("Colunas necessárias ('name', 'title') verificadas.")

        try:
            spotify_df = self.spotify_tracks_df.copy()
            youtube_df = self.youtube_videos_df.copy()
            print("Cópias dos DataFrames criadas.")

            correlated_data = []
            max_spotify_tracks = min(len(spotify_df), 200)
            max_youtube_videos = min(len(youtube_df), 500)
            print(f"Limitando a {max_spotify_tracks} faixas Spotify e {max_youtube_videos} vídeos YouTube.")

            spotify_sample = spotify_df.head(max_spotify_tracks)
            youtube_sample = youtube_df.head(max_youtube_videos)
            print("Samples (head) dos DataFrames obtidos.")

            print("Iniciando loops de correlação...")
            processed_spotify = 0
            for idx_s, spotify_row in spotify_sample.iterrows():
                processed_spotify += 1
                # if processed_spotify % 50 == 0: print(f"Processando faixa Spotify #{processed_spotify}...") # Optional debug print

                # Safely get track name and artist name, convert to lower case
                track_name_lower = str(spotify_row.get('name', '')).lower()
                artist_name_lower = str(spotify_row.get('artist', '')).lower()

                # Skip if track name is empty
                if not track_name_lower:
                    continue

                for idx_y, youtube_row in youtube_sample.iterrows():
                    # Safely get video title, convert to lower case
                    video_title_lower = str(youtube_row.get('title', '')).lower()
                    if not video_title_lower:
                        continue

                    # Basic matching: track name is in video title
                    track_match = track_name_lower in video_title_lower
                    # Optional: Add artist match check for better accuracy
                    artist_match = artist_name_lower in video_title_lower if artist_name_lower else False
                    
                    # Podemos fazer um match mais preciso exigindo que o nome do artista também esteja presente
                    # ou podemos deixar apenas o match do nome da faixa para ter mais resultados
                    if track_match:  # Pode mudar para: "if track_match and artist_match:" para maior precisão
                        correlation = {
                            # Use .get() for all fields to prevent KeyError if a column is missing unexpectedly
                            'spotify_track_id': spotify_row.get('id'),
                            'spotify_track_name': spotify_row.get('name'),
                            'spotify_artist': spotify_row.get('artist'),
                            'spotify_popularity': spotify_row.get('popularity'),
                            'spotify_danceability': spotify_row.get('danceability'),
                            'spotify_energy': spotify_row.get('energy'),
                            'youtube_video_id': youtube_row.get('id'),
                            'youtube_video_title': youtube_row.get('title'),
                            'youtube_channel': youtube_row.get('channel_title'),
                            'youtube_view_count': youtube_row.get('view_count'),
                            'youtube_like_count': youtube_row.get('like_count'),
                            'youtube_comment_count': youtube_row.get('comment_count'),
                            'youtube_engagement_rate': youtube_row.get('engagement_rate'),
                            'youtube_category': youtube_row.get('category_name_pt')
                        }
                        correlated_data.append(correlation)

            print("Loops de correlação concluídos.")

            if correlated_data:
                print(f"Encontradas {len(correlated_data)} correlações brutas. Criando DataFrame final...")
                self.correlation_df = pd.DataFrame(correlated_data)
                print("DataFrame criado. Removendo duplicatas...")
                # Ensure columns exist before dropping duplicates
                dup_cols = ['spotify_track_id', 'youtube_video_id']
                if all(col in self.correlation_df.columns for col in dup_cols):
                    self.correlation_df = self.correlation_df.drop_duplicates(subset=dup_cols)
                    print(f"DataFrame final com {len(self.correlation_df)} correlações únicas.")
                else:
                    print("Aviso: Colunas para drop_duplicates não encontradas. Pulando remoção de duplicatas.")
            else:
                print("Nenhuma correlação encontrada.")
                self.correlation_df = pd.DataFrame()

            print("Função correlate_spotify_youtube concluída com sucesso.")
            return self.correlation_df

        except Exception as e:
            print(f"!!! Erro inesperado dentro de correlate_spotify_youtube: {e}")
            import traceback
            print(traceback.format_exc()) # Print full traceback
            self.correlation_df = pd.DataFrame() # Return empty DF on error
            return self.correlation_df
    
    def analyze_regional_engagement(self, regions=['BR', 'US', 'GB'], platform="youtube"):
        """
        Analisa o engajamento em diferentes regiões por plataforma usando apenas dados das APIs.
        Args:
            regions: Lista de códigos de região (ISO-3166) para análise
            platform: 'youtube' ou 'spotify'
        Returns:
            DataFrame com dados de análise regional baseados em dados reais
        """
        print(f"Analisando engajamento regional para {regions} na plataforma {platform.upper()}...")
        
        regional_data = []
        
        # Verificar se já temos dados carregados
        if platform == "youtube" and (self.youtube_videos_df is None or self.youtube_videos_df.empty):
            print("Sem dados do YouTube para analisar. Buscando dados...")
        elif platform == "spotify" and (self.spotify_tracks_df is None or self.spotify_tracks_df.empty):
            print("Sem dados do Spotify para analisar. Buscando dados...")
        
        # Analisar dados para cada região
        for region in regions:
            if platform == "youtube":
                # Extrair dados do YouTube para essa região específica
                print(f"Buscando dados do YouTube para região {region}...")
                self.extract_youtube_data(region_code=region)
                
                # Verificar se temos dados para essa região
                if self.youtube_videos_df is None or self.youtube_videos_df.empty:
                    print(f"Sem dados disponíveis do YouTube para a região {region}. Pulando...")
                    continue
                
                # Filtrar dados apenas desta região (caso tenhamos dados de várias regiões)
                region_videos = self.youtube_videos_df[self.youtube_videos_df['region_code'] == region]
                
                if region_videos.empty:
                    print(f"Sem vídeos para a região {region} após filtragem. Pulando...")
                    continue
                
                # Calcular métricas reais baseadas nos dados da API
                video_count = len(region_videos)
                avg_views = region_videos['view_count'].mean()
                avg_likes = region_videos['like_count'].mean()  
                avg_comments = region_videos['comment_count'].mean()
                avg_engagement = region_videos['engagement_rate'].mean()
                
                # Encontrar categoria mais popular
                if 'category_name' in region_videos.columns and not region_videos['category_name'].empty:
                    top_category = region_videos['category_name'].value_counts().idxmax()
                else:
                    top_category = "Desconhecido"
                
                # Dados reais desta região
                region_stats = {
                    'region': region,
                    'region_name': region, # Poderia ser mapeado para nomes de países se necessário
                    'video_count': video_count,
                    'avg_views': avg_views,
                    'avg_likes': avg_likes,
                    'avg_comments': avg_comments,
                    'avg_engagement': avg_engagement,
                    'top_category': top_category
                }
                
            else:  # platform == "spotify"
                # Para Spotify, precisaremos coletar dados de popularidade de artistas/faixas por região
                # Nota: Isso pode requerer APIs adicionais ou extensão da API Spotify existente
                
                # Tenta usar dados existentes
                if self.spotify_tracks_df is None or self.spotify_tracks_df.empty:
                    print(f"Sem dados do Spotify disponíveis para região {region}. Pulando...")
                    continue
                
                # Métricas de Spotify (baseadas nos dados disponíveis)
                track_count = len(self.spotify_tracks_df)
                avg_popularity = self.spotify_tracks_df['popularity'].mean() if 'popularity' in self.spotify_tracks_df.columns else 0
                
                # Análise de gênero
                top_genre = "Desconhecido"
                genre_count = 0
                
                if self.spotify_artists_df is not None and not self.spotify_artists_df.empty and 'genres' in self.spotify_artists_df.columns:
                    # Extrair gêneros das faixas
                    all_genres = self.spotify_artists_df['genres'].str.split(', ').explode().dropna()
                    if not all_genres.empty:
                        genre_counts = all_genres.value_counts()
                        top_genre = genre_counts.idxmax()
                        genre_count = genre_counts.max()                # Audio features médias
                audio_features = ['danceability', 'energy']
                avg_danceability = self.spotify_tracks_df['danceability'].mean() if 'danceability' in self.spotify_tracks_df.columns else 0
                avg_energy = self.spotify_tracks_df['energy'].mean() if 'energy' in self.spotify_tracks_df.columns else 0
                
                # Dados de região Spotify
                region_stats = {
                    'region': region,
                    'region_name': region,
                    'track_count': track_count,
                    'avg_popularity': avg_popularity,
                    'top_genre': top_genre,
                    'genre_count': genre_count,
                    'top_genre_details': f"Dados baseados na sua biblioteca do Spotify",
                    'avg_danceability': round(avg_danceability, 2),
                    'avg_energy': round(avg_energy, 2)
                }

            regional_data.append(region_stats)

        if not regional_data:
            print("Nenhum dado regional foi coletado. Verifique as configurações de API e as regiões solicitadas.")
            return pd.DataFrame()
            
        regional_df = pd.DataFrame(regional_data)
        return regional_df
    
    def analyze_brazil_regions(self, regions=['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'], platform="youtube"):
        """
        Analisa o engajamento por regiões do Brasil por plataforma utilizando apenas dados reais.
        Args:
            regions: Lista de regiões brasileiras para análise
            platform: 'youtube' ou 'spotify'
        Returns:
            DataFrame com dados de análise regional baseados em dados reais
        """
        print(f"Analisando engajamento para regiões do Brasil na plataforma {platform.upper()} usando dados reais...")
        
        # Mapeamento das regiões brasileiras para códigos ISO dos estados
        # Como a API do YouTube trabalha com códigos de país (BR), precisaremos filtrar por metadados
        # Para o Spotify, podemos usar dados de popularidade regional se disponíveis
        brazil_region_mapping = {
            'Norte': ['AM', 'PA', 'RO', 'RR', 'AC', 'AP', 'TO'],
            'Nordeste': ['MA', 'PI', 'CE', 'RN', 'PB', 'PE', 'AL', 'SE', 'BA'],
            'Centro-Oeste': ['MT', 'MS', 'GO', 'DF'],
            'Sudeste': ['SP', 'RJ', 'MG', 'ES'],
            'Sul': ['PR', 'SC', 'RS']
        }
        
        regional_data = []
        
        # Verificar se já temos dados do Brasil carregados
        if platform == "youtube":
            # Para o YouTube, precisamos garantir que temos dados do Brasil
            if self.youtube_videos_df is None or self.youtube_videos_df.empty:
                print("Buscando dados do YouTube para o Brasil...")
                self.extract_youtube_data(region_code='BR')
                
            if self.youtube_videos_df is None or self.youtube_videos_df.empty:
                print("Não foi possível obter dados do YouTube para o Brasil. Verifique as credenciais da API.")
                return pd.DataFrame()
            
            # Nota: A API do YouTube não fornece dados específicos por região do Brasil
            # Estamos usando dados gerais do Brasil para todas as regiões, mas com análise de conteúdo
            # que pode sugerir popularidade regional como referências a lugares/sotaques/culturas regionais
            br_videos = self.youtube_videos_df[self.youtube_videos_df['region_code'] == 'BR']
            
            if br_videos.empty:
                print("Sem vídeos do Brasil disponíveis nos dados. Verifique a chamada da API.")
                return pd.DataFrame()
                
            # Para cada região do Brasil, analisamos os mesmos vídeos, mas adicionamos um contexto regional
            for region in regions:
                # Estatísticas gerais dos vídeos do Brasil
                video_count = len(br_videos)
                avg_views = br_videos['view_count'].mean()
                avg_likes = br_videos['like_count'].mean()
                avg_comments = br_videos['comment_count'].mean()
                avg_engagement = br_videos['engagement_rate'].mean()
                
                # Categoria mais popular
                top_category = br_videos['category_name'].value_counts().idxmax() if 'category_name' in br_videos.columns else 'Desconhecida'
                
                # Criar registro para a região
                region_stats = {
                    'region': region,
                    'region_name': f'Região {region}',
                    'video_count': video_count,
                    'avg_views': avg_views,
                    'avg_likes': avg_likes,
                    'avg_comments': avg_comments,
                    'avg_engagement': avg_engagement,
                    'top_category': top_category,
                    'top_category_details': f"Dados baseados em vídeos populares do Brasil (BR)"
                }
                
                regional_data.append(region_stats)
                
        elif platform == "spotify":
            # Para o Spotify, verificamos se temos dados
            if self.spotify_tracks_df is None or self.spotify_tracks_df.empty:
                print("Sem dados do Spotify disponíveis. Execute extract_spotify_data() primeiro.")
                return pd.DataFrame()
                
            # Estatísticas gerais do Spotify
            track_count = len(self.spotify_tracks_df)
            avg_popularity = self.spotify_tracks_df['popularity'].mean() if 'popularity' in self.spotify_tracks_df.columns else 0
            
            # Encontrar o gênero mais popular
            top_genre = "Desconhecido"
            genre_count = 0
            
            if self.spotify_artists_df is not None and not self.spotify_artists_df.empty and 'genres' in self.spotify_artists_df.columns:
                all_genres = self.spotify_artists_df['genres'].str.split(', ').explode().dropna()
                if not all_genres.empty:
                    genre_counts = all_genres.value_counts()
                    top_genre = genre_counts.idxmax() if not genre_counts.empty else "Desconhecido"
                    genre_count = genre_counts.max() if not genre_counts.empty else 0
            
            # Audio features médias
            avg_danceability = self.spotify_tracks_df['danceability'].mean() if 'danceability' in self.spotify_tracks_df.columns else 0
            avg_energy = self.spotify_tracks_df['energy'].mean() if 'energy' in self.spotify_tracks_df.columns else 0                # Para cada região do Brasil, usamos os mesmos dados com contexto regional
            for region in regions:
                top_genre_details = f"Dados baseados na sua biblioteca do Spotify"
                region_stats = {
                    'region': region,
                    'region_name': f'Região {region}',
                    'track_count': track_count,
                    'avg_popularity': avg_popularity,
                    'top_genre': top_genre,
                    'genre_count': genre_count,
                    'top_genre_details': top_genre_details,
                    'avg_danceability': round(avg_danceability, 2),
                    'avg_energy': round(avg_energy, 2)
                }
                
                regional_data.append(region_stats)
        
        if not regional_data:
            print("Nenhum dado regional do Brasil foi coletado.")
            return pd.DataFrame()
            
        regional_df = pd.DataFrame(regional_data)
        return regional_df
    
    def create_visualizations(self):
        """Cria visualizações interativas dos dados analisados."""
        print("Criando visualizações...")
        
        # Verificar se os dados estão disponíveis
        if (self.spotify_tracks_df is None or self.youtube_videos_df is None or 
            self.spotify_tracks_df.empty or self.youtube_videos_df.empty):
            print("Os dados do Spotify e do YouTube são necessários para visualizações.")
            return None
        
        # Criar diretório de saída para visualizações
        os.makedirs("visualizations", exist_ok=True)
        
        # 1. Popularidade de Artistas do Spotify
        if self.spotify_artists_df is not None and not self.spotify_artists_df.empty:
            top_artists = self.spotify_artists_df.sort_values(by='popularity', ascending=False).head(15)
            
            plt.figure(figsize=(12, 8))
            sns.barplot(x='popularity', y='name', data=top_artists)
            plt.title('Top 15 Artistas por Popularidade')
            plt.tight_layout()
            plt.savefig('visualizations/top_artists_popularity.png')
            plt.close()
            
        # 2. Distribuição de Características de Áudio
        if self.spotify_tracks_df is not None and not self.spotify_tracks_df.empty:
            features = ['danceability', 'energy', 'speechiness', 'acousticness', 
                      'instrumentalness', 'liveness', 'valence']
            
            available_features = [f for f in features if f in self.spotify_tracks_df.columns]
            
            if available_features:
                features_df = self.spotify_tracks_df[available_features].melt(var_name='feature', value_name='value')
                
                plt.figure(figsize=(14, 8))
                sns.violinplot(x='feature', y='value', data=features_df)
                plt.title('Distribuição de Características de Áudio')
                plt.tight_layout()
                plt.savefig('visualizations/audio_features_dist.png')
                plt.close()
            
        # 3. Engajamento por Categoria no YouTube
        if self.youtube_videos_df is not None and not self.youtube_videos_df.empty and 'category_name' in self.youtube_videos_df.columns:
            category_engagement = self.youtube_videos_df.groupby('category_name').agg({
                'view_count': 'mean',
                'like_count': 'mean',
                'comment_count': 'mean',
                'engagement_rate': 'mean'
            }).reset_index()
            
            # Plotar
            plt.figure(figsize=(14, 8))
            sns.barplot(x='engagement_rate', y='category_name', data=category_engagement.sort_values('engagement_rate'))
            plt.title('Taxa Média de Engajamento por Categoria do YouTube')
            plt.tight_layout()
            plt.savefig('visualizations/youtube_category_engagement.png')
            plt.close()
          # 4. Correlação entre popularidade do Spotify e visualizações do YouTube
        if self.correlation_df is not None and not self.correlation_df.empty:
            if 'spotify_popularity' in self.correlation_df.columns and 'youtube_view_count' in self.correlation_df.columns:
                plt.figure(figsize=(10, 8))
                sns.scatterplot(x='spotify_popularity', y='youtube_view_count', data=self.correlation_df)
                plt.title('Correlação: Popularidade no Spotify vs Visualizações no YouTube')
                plt.tight_layout()
                plt.savefig('visualizations/spotify_youtube_correlation.png')
                plt.close()
            
        # 5. Criar visualização interativa usando Plotly
        if self.youtube_videos_df is not None and not self.youtube_videos_df.empty:
            # Criar gráfico de bolhas de visualizações vs. likes com engajamento como tamanho
            fig = px.scatter(
                self.youtube_videos_df,
                x='view_count',
                y='like_count',
                size='engagement_rate',
                color='category_name',
                hover_name='title',
                log_x=True,
                log_y=True,
                size_max=60,
                title='Vídeos do YouTube: Visualizações vs. Likes por Categoria'
            )
            
            fig.update_layout(
                xaxis_title='Contagem de Visualizações (escala logarítmica)',
                yaxis_title='Contagem de Likes (escala logarítmica)',
                legend_title='Categoria'
            )
            
            fig.write_html('visualizations/interactive_youtube_metrics.html')        # 6. Comparação de engajamento regional
        regional_df = self.analyze_regional_engagement()
        
        if regional_df is not None and not regional_df.empty:
            if 'avg_views' in regional_df.columns:
                plt.figure(figsize=(12, 6))
                sns.barplot(x='region', y='avg_views', data=regional_df)
                plt.title('Média de Visualizações por Região')
                plt.tight_layout()
                plt.savefig('visualizations/regional_views.png')
                plt.close()
                
                # Criar visualização interativa de engajamento regional
                fig = px.bar(
                    regional_df, 
                    x='region', 
                    y=['avg_views', 'avg_likes', 'avg_comments'],
                    barmode='group',
                    title='Métricas de Engajamento do YouTube por Região',
                )
                
                fig.update_layout(
                    xaxis_title='Região',
                    yaxis_title='Média',
                    legend_title='Métrica'
                )
                
                fig.write_html('visualizations/regional_engagement.html')
            fig = px.bar(
                regional_df, 
                x='region', 
                y=['avg_views', 'avg_likes', 'avg_comments'],
                barmode='group',
                title='Métricas de Engajamento do YouTube por Região',
            )
            
            fig.update_layout(
                xaxis_title='Região',
                yaxis_title='Média',
                legend_title='Métrica'
            )
            
            fig.write_html('visualizations/regional_engagement.html')
            
        print(f"Visualizações salvas no diretório 'visualizations'")
    
    def run(self):
        """Executa o pipeline completo de análise."""
        # Extrair dados
        self.extract_spotify_data()
        self.extract_youtube_data()
        
        # Analisar dados
        spotify_analysis = self.analyze_spotify_trends()
        youtube_analysis = self.analyze_youtube_trends()
          # Correlacionar dados
        correlations = self.correlate_spotify_youtube()
        
        # Análise regional
        regional_analysis = self.analyze_regional_engagement()
        
        # Criar visualizações
        self.create_visualizations()
          # Retornar todas as análises
        return {
            'spotify': spotify_analysis,
            'youtube': youtube_analysis,
            'correlations': self.correlation_df,
            'regional': regional_analysis
        }

# Execução principal
if __name__ == "__main__":
    analyzer = SpotifyYouTubeAnalyzer()
    results = analyzer.run()
      # Imprimir resumo dos resultados
    print("\n===== RESUMO DA ANÁLISE =====")
    if results.get('spotify'):
        print("\n----- Tendências do Spotify -----")
        print(f"Top artistas analisados: {len(results['spotify'].get('top_artists_by_count', []))}")
        print(f"Popularidade média das faixas: {results['spotify'].get('avg_track_popularity', 0):.2f}/100")
        if 'avg_duration_min' in results['spotify']:
            print(f"Duração média das faixas: {results['spotify']['avg_duration_min']:.2f} minutos")
    
    if results.get('youtube'):
        print("\n----- Tendências do YouTube -----")
        print(f"Visualizações médias: {results['youtube'].get('avg_view_count', 0):.0f}")
        print(f"Taxa média de engajamento: {results['youtube'].get('avg_engagement_rate', 0):.4f}")
    
    if results.get('correlations') is not None and not results['correlations'].empty:
        print("\n----- Correlações entre Plataformas -----")
        print(f"Correspondências de vídeos musicais encontradas: {len(results['correlations'])}")
    
    if results.get('regional') is not None:
        print("\n----- Análise Regional -----")
        print(f"Regiões analisadas: {len(results['regional'])}")
    
    print("\nAnálise completa! Verifique o diretório 'visualizations' para gráficos detalhados.")