"""
Dashboard interativo para análise de dados do Spotify e YouTube
Este script cria uma interface web usando Dash para visualizar e analisar
dados das APIs do Spotify e YouTube.
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
from spotify_youtube_analysis import SpotifyYouTubeAnalyzer

# Importação para ícones
external_stylesheets = [
    dbc.themes.FLATLY,
    'https://use.fontawesome.com/releases/v5.15.4/css/all.css',
    'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css'
]

# Importar as constantes para as credenciais das APIs
from spotify_youtube_analysis import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, YOUTUBE_API_KEY

# Inicialização do analisador
analyzer = SpotifyYouTubeAnalyzer()

# Definição de estilos personalizados
custom_styles = {
    "card_shadow": {"boxShadow": "0 4px 8px 0 rgba(0,0,0,0.2)"},
    "section_style": {"backgroundColor": "#f8f9fa", "border": "1px solid #dee2e6", "borderRadius": "0.25rem", "padding": "1rem"},
    "title_style": {"borderBottom": "2px solid #007bff", "paddingBottom": "0.5rem", "marginBottom": "1rem", "color": "#0056b3"},
    "button_shadow": {"boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)"}
}

# Inicialização da aplicação Dash
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

# Layout do cabeçalho
header = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col([
                            html.I(className="fas fa-headphones-alt fa-2x text-white me-3 d-inline"),
                            dbc.NavbarBrand([
                                "Spotify ",
                                html.I(className="fab fa-spotify mx-1"),
                                " & YouTube ",
                                html.I(className="fab fa-youtube mx-1"),
                                " Analyzer"
                            ], className="ms-2 fw-bold"),
                        ]),
                    ],
                    align="center",
                ),
                href="/",
                style={"textDecoration": "none"},
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.NavbarToggler(id="navbar-toggler"),
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavItem(dbc.NavLink([html.I(className="fas fa-home me-2"), "Início"], href="#")),
                                        dbc.NavItem(dbc.NavLink([html.I(className="fas fa-question-circle me-2"), "Ajuda"], href="#")),
                                    ],
                                    navbar=True,
                                ),
                                id="navbar-collapse",
                                navbar=True,
                            ),
                        ]
                    ),
                ],
                align="center",
            ),
        ],
        fluid=True,
    ),
    color="primary",
    dark=True,
    className="mb-4 shadow",
    style={"borderBottom": "4px solid #17a2b8"}
)

# Cards para exibir métricas
metrics_cards = dbc.Row(
    [
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Spotify Tracks"),
                    dbc.CardBody(
                        [
                            html.H3(id="spotify-tracks-count", children="0"),
                            html.P("Faixas analisadas"),
                        ]
                    ),
                ],
                className="text-center mb-4 h-100",
            ),
            width=12,
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("YouTube Videos"),
                    dbc.CardBody(
                        [
                            html.H3(id="youtube-videos-count", children="0"),
                            html.P("Vídeos analisados"),
                        ]
                    ),
                ],
                className="text-center mb-4 h-100",
            ),
            width=12,
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Correlações"),
                    dbc.CardBody(
                        [
                            html.H3(id="correlations-count", children="0"),
                            html.P("Correspondências encontradas"),
                        ]
                    ),
                ],
                className="text-center mb-4 h-100",
            ),
            width=12,
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Regiões"),
                    dbc.CardBody(
                        [
                            html.H3(id="regions-count", children="0"),
                            html.P("Regiões analisadas"),
                        ]
                    ),
                ],
                className="text-center mb-4 h-100",
            ),
            width=12,
            md=3,
        ),
    ],
    className="mb-4",
)

# Painel de controle
control_panel = dbc.Card(
[
        dbc.CardHeader([
            html.I(className="fas fa-sliders-h me-2"),
            "Painel de Controle"
        ], className="fw-bold bg-primary text-white"),
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.H5([html.I(className="fas fa-download me-2"), "Extração de Dados"], 
                                className="d-flex align-items-center border-bottom pb-2 text-primary"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    [html.I(className="fab fa-spotify me-2"), "Extrair Dados do Spotify"],
                                    id="extract-spotify-button",
                                    color="success",
                                    className="w-100 mb-2 d-flex align-items-center justify-content-center",
                                    style={"boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)"}
                                ),
                            ], width=12, md=6),
                            dbc.Col([
                                dbc.Button(
                                    [html.I(className="fab fa-youtube me-2"), "Extrair Dados do YouTube"],
                                    id="extract-youtube-button",
                                    color="danger",
                                    className="w-100 mb-2 d-flex align-items-center justify-content-center",
                                    style={"boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)"}
                                ),
                            ], width=12, md=6),
                        ]),
                        html.Div(id="extraction-status", className="mt-2 text-muted fst-italic"),
                    ],
                    className="mb-4 p-3 border rounded",
                    style={"backgroundColor": "#f8f9fa"}
                ),                html.Div(
                    [
                        html.H5([html.I(className="fas fa-globe-americas me-2"), "Análise Regional"], 
                                className="d-flex align-items-center border-bottom pb-2 text-primary"),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText([html.I(className="fas fa-map-marker-alt me-2"), "Códigos de Região:"]),
                                dbc.Input(
                                    id="region-input",
                                    placeholder="BR,US,GB...",
                                    value="BR,US,GB",
                                    className="border-primary",
                                ),
                            ],
                            className="mb-2",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText([html.I(className="fas fa-music me-2"), "Plataforma:"]),
                                dbc.Select(
                                    id="platform-select",
                                    options=[
                                        {"label": "YouTube", "value": "youtube"},
                                        {"label": "Spotify", "value": "spotify"}
                                    ],
                                    value="youtube",
                                    className="border-primary",
                                    style={"fontWeight": "500"}
                                ),
                            ],
                            className="mb-2",
                        ),
                        dbc.Card([
                            dbc.CardBody([
                                dbc.RadioItems(
                                    options=[
                                        {"label": [html.I(className="fas fa-flag me-2"), "Países"], "value": "countries"},
                                        {"label": [html.I(className="fas fa-map me-2"), "Regiões do Brasil"], "value": "brazil"},
                                    ],
                                    value="countries",
                                    id="region-type-radio",
                                    inline=True,
                                    className="mb-2 d-flex justify-content-around",
                                    inputClassName="border border-primary",
                                ),
                                dbc.Button(
                                    [html.I(className="fas fa-chart-bar me-2"), "Analisar Regiões"],
                                    id="analyze-regions-button",
                                    color="primary",
                                    className="w-100 mt-2",
                                    style={"boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)"}
                                ),
                            ])
                        ], className="bg-light border-0"),
                    ],
                    className="mb-4 p-3 border rounded",
                    style={"backgroundColor": "#f8f9fa"}
                ),                html.Div(
                    [
                        html.H5([html.I(className="fas fa-chart-line me-2"), "Análises"], 
                                className="d-flex align-items-center border-bottom pb-2 text-primary"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    [html.I(className="fab fa-spotify me-2"), "Analisar Spotify"],
                                    id="analyze-spotify-button",
                                    color="success",
                                    className="w-100 mb-2",
                                    style={"boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)"}
                                ),
                            ], width=12, md=6),
                            dbc.Col([
                                dbc.Button(
                                    [html.I(className="fab fa-youtube me-2"), "Analisar YouTube"],
                                    id="analyze-youtube-button",
                                    color="danger",
                                    className="w-100 mb-2",
                                    style={"boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)"}
                                ),
                            ], width=12, md=6),
                        ]),
                        dbc.Button(
                            [html.I(className="fas fa-link me-2"), "Correlacionar Dados"],
                            id="correlate-button",
                            color="warning",
                            className="w-100 mb-2",
                            style={"boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)"}
                        ),                        # Novo: Informação sobre dados em tempo real
                        dbc.Card(
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        html.H6([html.I(className="fas fa-sync-alt me-2"), "Dados em Tempo Real"], className="mb-0")
                                    ], width="auto", className="d-flex align-items-center"),
                                ]),
                                html.Small([
                                    html.I(className="fas fa-info-circle me-1 text-info"),
                                    "Ative o switch na aba de correlações para buscar dados em tempo real nas APIs para análises mais precisas. Pode aumentar o tempo de processamento."
                                ],                            className="text-muted d-block mt-2")
                            ]), 
                            className="mt-2 mb-2 border-warning bg-light",
                            style={"border-left": "4px solid #ffc107"}
                        ),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    [html.I(className="fas fa-key me-2"), "Configuração de APIs"],
                                    id="api-config-button",
                                    color="light",
                                    outline=True,
                                    size="sm",
                                    className="w-100 mt-2",
                                ),
                            ], width=12),
                        ]),
                    ],
                    className="mb-4 p-3 border rounded",
                    style={"backgroundColor": "#f8f9fa"}
                ),
                html.Div(
                    [
                        html.H5([html.I(className="fas fa-eye me-2"), "Visualizações"], 
                                className="d-flex align-items-center border-bottom pb-2 text-primary"),
                        dbc.Row([
                            dbc.Col([                                dbc.Button(
                                    [html.I(className="fas fa-chart-pie me-2"), "Gerar Visualizações"],
                                    id="generate-visualizations-button",
                                    color="info",
                                    className="w-100 mb-2",
                                    style={"boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)"}
                                ),
                            ], width=12, md=6),
                            dbc.Col([
                                dbc.Button(
                                    [html.I(className="fas fa-play-circle me-2"), "Pipeline Completo"],
                                    id="full-pipeline-button",
                                    color="primary",
                                    className="w-100 mb-2",
                                    style={"boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)"}
                                ),
                            ], width=12, md=6),
                        ]),                        html.Div(
                            html.Small([
                                html.I(className="fas fa-info-circle me-1"), 
                                "Dica: O pipeline completo executa todas as etapas de análise automaticamente."
                            ]), 
                            className="text-muted mt-2 fst-italic text-center"
                        ),
                    ],
                    className="p-3 border rounded",
                    style={"backgroundColor": "#f8f9fa"}
                ),
            ]
        ),
    ],
    className="mb-4",
)

# Layout das abas
tabs = dbc.Tabs(
    [        dbc.Tab(
            label="Spotify Trends",
            tab_id="spotify-tab",
            children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Top Artistas por Popularidade"),
                            dbc.CardBody(dcc.Graph(id="spotify-artists-graph")),
                        ]),
                    ], width=12, lg=6, className="mb-4"),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Distribuição de Características de Áudio"),
                            dbc.CardBody(dcc.Graph(id="spotify-audio-features-graph")),
                        ]),
                    ], width=12, lg=6, className="mb-4"),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Popularidade por Gênero Musical"),
                            dbc.CardBody(dcc.Graph(id="spotify-genres-graph")),
                        ]),
                    ], width=12, lg=6, className="mb-4"),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Análise Temporal de Lançamentos"),
                            dbc.CardBody(dcc.Graph(id="spotify-releases-graph")),
                        ]),
                    ], width=12, lg=6, className="mb-4"),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Estatísticas das Faixas"),
                            dbc.CardBody(html.Div(id="spotify-track-stats")),
                        ]),
                    ], width=12, className="mb-4"),
                ]),
            ],
        ),        dbc.Tab(
            label="YouTube Trends",
            tab_id="youtube-tab",
            children=[                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([html.I(className="fas fa-chart-bar me-2"), "Engajamento por Categoria"]),
                            dbc.CardBody(dcc.Graph(id="youtube-category-engagement-graph")),
                        ], style=custom_styles["card_shadow"]),
                    ], width=12, lg=6, className="mb-4"),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([html.I(className="fas fa-eye me-2"), "Visualizações vs. Engajamento"]),
                            dbc.CardBody(dcc.Graph(id="youtube-views-engagement-graph")),
                        ], style=custom_styles["card_shadow"]),
                    ], width=12, lg=6, className="mb-4"),                
                ]),                # Análise detalhada por categoria - Mais organizada e clara
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([html.I(className="fas fa-chart-bar me-2"), "Análise por Categoria de Vídeo"], className="mb-0")
                    ], className="bg-primary text-white"),
                    dbc.CardBody([
                        dbc.Tabs([
                            dbc.Tab(
                                dbc.Card(dcc.Graph(id="youtube-category-views-graph"), className="border-0"),
                                label="Visualizações",
                                tab_id="views-tab",
                                label_style={"color": "#0275d8", "font-weight": "bold"},
                                active_label_style={"background-color": "#eaf2fd"}
                            ),
                            dbc.Tab(
                                dbc.Card(dcc.Graph(id="youtube-category-likes-graph"), className="border-0"),
                                label="Curtidas",
                                tab_id="likes-tab",
                                label_style={"color": "#d9534f", "font-weight": "bold"},
                                active_label_style={"background-color": "#ffe5e5"}
                            ),
                            dbc.Tab(
                                dbc.Card(dcc.Graph(id="youtube-category-comments-graph"), className="border-0"),
                                label="Comentários",
                                tab_id="comments-tab",
                                label_style={"color": "#5cb85c", "font-weight": "bold"},
                                active_label_style={"background-color": "#e8f8e8"}
                            ),
                        ], id="category-analysis-tabs", className="mb-3"),
                        dbc.Alert([
                            html.I(className="fas fa-info-circle me-2"),
                            "Selecione as abas acima para visualizar a análise por diferentes métricas. Os gráficos mostram as categorias com melhor desempenho para cada métrica."
                        ], color="info", className="mb-0")
                    ]),
                ], style=custom_styles["card_shadow"], className="mb-4"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([html.I(className="fas fa-comments me-2"), "Relação Comentários vs. Likes"]),
                            dbc.CardBody(dcc.Graph(id="youtube-comments-likes-graph")),
                        ], style=custom_styles["card_shadow"]),
                    ], width=12, className="mb-4"),                
                ]),
                # Seção de "Estatísticas Detalhadas dos Vídeos" foi removida
            ],
        ),        dbc.Tab(
            label="Correlações",
            tab_id="correlation-tab",
            children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                dbc.Row([
                                    dbc.Col([
                                        html.I(className="fas fa-chart-line me-2"), 
                                        "Popularidade Spotify vs. Visualizações YouTube"
                                    ], width=8),                                dbc.Col([
                                        dbc.Checklist(
                                            options=[
                                                {"label": "Usar dados em tempo real", "value": 1},
                                            ],
                                            value=[],
                                            id="use-realtime-switch",
                                            switch=True,
                                            style={"color": "#007bff"},
                                            className="mb-0",
                                            inline=True,
                                        ),
                                    ], width=4, className="text-end"),
                                ]),
                            ]),
                            dbc.CardBody([
                                dbc.Alert(
                                    [
                                        html.I(className="fas fa-info-circle me-2"),
                                        "A opção de dados em tempo real busca informações atualizadas diretamente das APIs do Spotify e YouTube para músicas correspondentes. Pode levar alguns segundos. Requer configuração de credenciais de API."
                                    ],
                                    color="info",
                                    className="mb-3",
                                    id="realtime-info-alert",
                                    dismissable=True,
                                ),
                                dcc.Graph(id="correlation-graph"),
                            ]),
                        ], style=custom_styles["card_shadow"]),
                    ], width=12, className="mb-4"),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([html.I(className="fas fa-star me-2"), "Top Músicas Viralizadas"]),
                            dbc.CardBody(html.Div(id="viral-songs-table")),
                        ], style=custom_styles["card_shadow"]),
                    ], width=12, lg=6, className="mb-4"),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([html.I(className="fas fa-chart-pie me-2"), "Distribuição por Gênero Musical"]),
                            dbc.CardBody(dcc.Graph(id="viral-genres-graph")),
                        ], style=custom_styles["card_shadow"]),
                    ], width=12, lg=6, className="mb-4"),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([html.I(className="fas fa-link me-2"), "Correspondências Encontradas"]),
                            dbc.CardBody(html.Div(id="correlation-stats")),
                        ], style=custom_styles["card_shadow"]),
                    ], width=12, className="mb-4"),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([html.I(className="fas fa-lightbulb me-2"), "Análise e Insights"]),
                            dbc.CardBody(html.Div(id="viral-insights")),
                        ], style=custom_styles["card_shadow"]),
                    ], width=12, className="mb-4"),
                ]),
            ],
        ),        dbc.Tab(
            label="Análise Regional",
            tab_id="regional-tab",
            children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([html.I(className="fas fa-map-marked-alt me-2"), "Mapa Regional do Brasil"]),
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([                                        html.Div([
                                            html.P([
                                                html.I(className="fas fa-filter me-2"), 
                                                "Selecione uma plataforma:"
                                            ], className="fw-bold"),
                                            dbc.ButtonGroup(
                                                [
                                                    dbc.Button(
                                                        [html.I(className="fab fa-youtube me-1"), "YouTube"], 
                                                        id="btn-youtube",
                                                        color="danger",
                                                        outline=False,
                                                        n_clicks=1,
                                                        className="me-1"
                                                    ),
                                                    dbc.Button(
                                                        [html.I(className="fab fa-spotify me-1"), "Spotify"], 
                                                        id="btn-spotify",
                                                        color="success",
                                                        outline=True,
                                                        n_clicks=0,
                                                        className="me-1"
                                                    ),
                                                ],
                                                className="mb-2"
                                            ),
                                            dbc.RadioItems(
                                                id="brazil-platform-select",
                                                options=[
                                                    {"label": "YouTube", "value": "youtube"},
                                                    {"label": "Spotify", "value": "spotify"}
                                                ],
                                                value="youtube",
                                                inline=True,
                                                style={"display": "none"}  # Escondemos os radio buttons e usamos botões
                                            ),
                                        ], className="border-bottom pb-2"),
                                    ], width=12, className="mb-3"),
                                ]),                                # Adicione os botões das regiões e o input oculto aqui
                                dbc.Row([
                                    dbc.Col([                                        dbc.Row([
                                            dbc.Col([
                                                html.P("Selecione uma região:", className="mb-1 small"),
                                            ], width="auto"),
                                            dbc.Col([
                                                dbc.Button(
                                                    [html.I(className="fas fa-undo me-1"), "Limpar seleção"],
                                                    id="btn-reset-region",
                                                    color="secondary",
                                                    size="sm",
                                                    outline=True,
                                                    className="float-end"
                                                )
                                            ], width="auto", className="ms-auto"),
                                        ], className="mb-1 align-items-center"),
                                        dbc.ButtonGroup([
                                            dbc.Button("Norte", id="btn-region-norte", color="success", size="sm", outline=True, className="me-1"),
                                            dbc.Button("Nordeste", id="btn-region-nordeste", color="info", size="sm", outline=True, className="me-1"),
                                            dbc.Button("Centro-Oeste", id="btn-region-centro", color="warning", size="sm", outline=True, className="me-1"),
                                            dbc.Button("Sudeste", id="btn-region-sudeste", color="danger", size="sm", outline=True, className="me-1"),
                                            dbc.Button("Sul", id="btn-region-sul", color="primary", size="sm", outline=True)
                                        ], className="mb-2"),
                                        # Input oculto para armazenar a região selecionada
                                        dbc.Input(id="selected-region-input", type="hidden", value="")
                                    ], width=12, className="mb-2"),
                                ]),
                                
                                dbc.Row([
                                    dbc.Col([                                        # Mapa interativo do Brasil
                                        dcc.Graph(id="brazil-choropleth-map", 
                                                 style={"height": "500px", "width": "100%"},
                                                 config={"responsive": True, "displayModeBar": True}),
                                    ], width=12, lg=7),
                                    dbc.Col([
                                        # Painel de informações da região selecionada
                                        html.Div([
                                            html.H4(id="selected-region-title", children="Selecione uma região no mapa", className="mb-3 text-primary"),
                                            html.Div(id="selected-region-info", children=[
                                                dbc.Alert([
                                                    html.I(className="fas fa-info-circle me-2"),
                                                    "Clique em uma região do Brasil no mapa para ver análises detalhadas."
                                                ], color="info")
                                            ]),
                                            html.Div(id="selected-region-stats")
                                        ], className="h-100 d-flex flex-column")
                                    ], width=12, lg=5),
                                ]),
                            ]),
                        ], style=custom_styles["card_shadow"]),
                    ], width=12, className="mb-4"),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([html.I(className="fas fa-chart-bar me-2"), "Comparação entre Regiões"]),
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        dcc.Graph(id="regional-engagement-graph"),
                                    ], width=12, lg=6),
                                    dbc.Col([
                                        dcc.Graph(id="regional-categories-graph"),
                                    ], width=12, lg=6),
                                ]),
                            ]),
                        ], style=custom_styles["card_shadow"]),
                    ], width=12, className="mb-4"),
                ]),
            ],
        ),
    ],
    id="tabs",
    active_tab="spotify-tab",
    className="mb-4",
)

# Layout da aplicação

# Layout principal da aplicação
app.layout = dbc.Container(
    [
        # Armazenamento de dados
        dcc.Store(id="spotify-data-store"),
        dcc.Store(id="youtube-data-store"),
        dcc.Store(id="correlation-data-store"),
        dcc.Store(id="regional-data-store"),
          # Componentes da interface
        header,        dbc.Row(
            [
                dbc.Col(
                    [control_panel], 
                    width=12, 
                    lg=3,
                    className="animate__animated animate__fadeInLeft"
                ),
                dbc.Col(
                    [metrics_cards, tabs], 
                    width=12, 
                    lg=9,
                    className="animate__animated animate__fadeInRight"
                ),
            ],
            className="g-4" # Adiciona mais espaço entre as colunas
        ),
        
        # Modal para exibir mensagens de status
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Status")),
                dbc.ModalBody(id="modal-body"),
            ],
            id="status-modal",
            is_open=False,
        ),
        
        # Modal para configuração de API
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle([html.I(className="fas fa-key me-2"), "Status de Conexão com APIs"])),
                dbc.ModalBody([
                    html.H5("Spotify API", className="text-success"),
                    html.Div(id="spotify-api-status"),
                    html.Hr(),
                    html.H5("YouTube API", className="text-danger"),
                    html.Div(id="youtube-api-status"),
                    html.Hr(),
                    dbc.Alert([
                        html.H6("Como configurar suas credenciais:"),
                        html.P([
                            "Para usar dados em tempo real, edite o arquivo ",
                            html.Code("spotify_youtube_analysis.py"),
                            " e substitua as credenciais de exemplo pelas suas credenciais reais."
                        ]),
                        html.Ul([
                            html.Li([
                                "Para o Spotify: registre um aplicativo em ",
                                html.A("Spotify Developer Dashboard", href="https://developer.spotify.com/dashboard", target="_blank"),
                                " e obtenha seu Client ID e Secret."
                            ]),
                            html.Li([
                                "Para o YouTube: configure um projeto na ",
                                html.A("Google Cloud Console", href="https://console.cloud.google.com/", target="_blank"),
                                ", habilite a YouTube Data API v3 e crie uma chave de API."
                            ])
                        ])
                    ], color="info")
                ]),
                dbc.ModalFooter(
                    dbc.Button("Fechar", id="close-api-modal", className="ms-auto", n_clicks=0)
                ),
            ],
            id="api-config-modal",
            is_open=False,
            size="lg",
        ),
    ],
    fluid=True,
    className="dbc",
)

# Callbacks

# Callback para extrair dados do Spotify
@app.callback(
    [
        Output("spotify-data-store", "data"),
        Output("status-modal", "is_open", allow_duplicate=True),
        Output("modal-body", "children", allow_duplicate=True),
        Output("spotify-tracks-count", "children"),
    ],
    [Input("extract-spotify-button", "n_clicks")],
    [State("spotify-data-store", "data")],
    prevent_initial_call=True,
)
def extract_spotify_data(n_clicks, current_data):
    if not n_clicks:
        return current_data, False, "", "0"
    
    try:
        # Mostra mensagem que estamos começando a extração
        print("Iniciando extração de dados do Spotify...")
        
        # Extrair dados do Spotify
        spotify_tracks_df, spotify_playlists_df, spotify_artists_df = analyzer.extract_spotify_data()
        
        # Verificando se os dados foram extraídos corretamente
        if spotify_tracks_df is None or spotify_tracks_df.empty:
            print("Nenhuma faixa encontrada no Spotify")
            return current_data, True, "Nenhuma faixa encontrada no Spotify. Verifique sua conexão e autorização.", "0"
        
        # Converter DataFrames para JSON
        data = {
            "tracks": spotify_tracks_df.to_json(date_format='iso', orient='split') if spotify_tracks_df is not None else None,
            "playlists": spotify_playlists_df.to_json(date_format='iso', orient='split') if spotify_playlists_df is not None else None,
            "artists": spotify_artists_df.to_json(date_format='iso', orient='split') if spotify_artists_df is not None else None,
        }
        
        track_count = len(spotify_tracks_df) if spotify_tracks_df is not None else 0
        playlist_count = len(spotify_playlists_df) if spotify_playlists_df is not None else 0
        artist_count = len(spotify_artists_df) if spotify_artists_df is not None else 0
        
        print(f"Extração finalizada: {track_count} faixas, {playlist_count} playlists, {artist_count} artistas")
        
        return data, True, f"Dados do Spotify extraídos com sucesso: {track_count} faixas, {playlist_count} playlists, {artist_count} artistas", str(track_count)
    
    except Exception as e:
        print(f"Erro na extração do Spotify: {str(e)}")
        return current_data, True, f"Erro ao extrair dados do Spotify: {str(e)}", "0"

# Callback para extrair dados do YouTube
@app.callback(
    [
        Output("youtube-data-store", "data"),
        Output("status-modal", "is_open", allow_duplicate=True),
        Output("modal-body", "children", allow_duplicate=True),
        Output("youtube-videos-count", "children"),
    ],
    [Input("extract-youtube-button", "n_clicks")],
    [State("youtube-data-store", "data")],
    prevent_initial_call=True,
)
def extract_youtube_data(n_clicks, current_data):
    if not n_clicks:
        return current_data, False, "", "0"
    
    try:
        # Extrair dados do YouTube para o Brasil por padrão
        youtube_videos_df, youtube_categories_df = analyzer.extract_youtube_data()
        
        # Converter DataFrames para JSON
        data = {
            "videos": youtube_videos_df.to_json(date_format='iso', orient='split') if youtube_videos_df is not None else None,
            "categories": youtube_categories_df.to_json(date_format='iso', orient='split') if youtube_categories_df is not None else None,
        }
        
        video_count = len(youtube_videos_df) if youtube_videos_df is not None else 0
        
        return data, True, f"Dados do YouTube extraídos com sucesso: {video_count} vídeos", str(video_count)
    
    except Exception as e:
        return current_data, True, f"Erro ao extrair dados do YouTube: {str(e)}", "0"

# Callback para análise regional
@app.callback(
    [
        Output("regional-data-store", "data"),
        Output("status-modal", "is_open", allow_duplicate=True),
        Output("modal-body", "children", allow_duplicate=True),
        Output("regions-count", "children"),
        Output("regional-engagement-graph", "figure"),
        Output("regional-categories-graph", "figure"),
    ],
    [Input("analyze-regions-button", "n_clicks")],
    [
        State("region-input", "value"),
        State("platform-select", "value"),
        State("region-type-radio", "value"),
    ],
    prevent_initial_call=True,
)
def analyze_regions(n_clicks, regions_input, platform, region_type):
    if not n_clicks or not regions_input:
        return {}, False, "", "0", {}, {}
    
    try:
        # Processar a entrada de regiões
        regions = [r.strip() for r in regions_input.split(",")]
        print(f"Analisando {region_type} para plataforma {platform}: {regions}")
        
        # Se for análise de países
        if region_type == "countries":
            # Colocar códigos em maiúsculas
            regions = [r.upper() for r in regions]
            
            # Validar códigos de região (apenas códigos ISO-3166 válidos de 2 letras)
            valid_regions = []
            for region in regions:
                if len(region) == 2 and region.isalpha():
                    valid_regions.append(region)
                else:
                    print(f"Código de país inválido: {region}")
            
            if not valid_regions:
                empty_fig = px.bar(title="Sem dados regionais")
                return {}, True, "Nenhum código de país válido fornecido. Use códigos de 2 letras como BR, US, GB.", "0", empty_fig, empty_fig
            
            # Limitar a 5 regiões para evitar demora na análise
            if len(valid_regions) > 5:
                valid_regions = valid_regions[:5]
                print(f"Limitando análise aos primeiros 5 países: {valid_regions}")
                
            # Analisar dados regionais com a plataforma selecionada
            regional_df = analyzer.analyze_regional_engagement(valid_regions, platform=platform)
        else:  # region_type == "brazil"
            # Para regiões do Brasil, usamos a função específica
            valid_regions = []
            brazil_regions = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
            
            # Verificar quais regiões são válidas
            for region in regions:
                if region.title() in brazil_regions:
                    valid_regions.append(region.title())
                else:
                    print(f"Região do Brasil inválida: {region}")
            
            if not valid_regions:
                valid_regions = brazil_regions  # Se nenhuma região válida, usar todas
                print("Usando todas as regiões do Brasil")
            
            # Analisar dados das regiões brasileiras com a plataforma selecionada
            regional_df = analyzer.analyze_brazil_regions(valid_regions, platform=platform)
        
        # Converter DataFrame para JSON
        data = {
            "regional": regional_df.to_json(date_format='iso', orient='split') if regional_df is not None else None,
            "platform": platform,
            "region_type": region_type,
        }
        
        region_count = len(regional_df) if regional_df is not None else 0
        
        # Criar gráficos específicos conforme a plataforma selecionada
        if platform == "youtube":
            # Gráfico para YouTube: métricas de visualizações
            if "avg_views" in regional_df.columns:
                engagement_fig = px.bar(
                    regional_df,
                    x="region",
                    y=["avg_views", "avg_likes", "avg_comments"],
                    title="Métricas de Engajamento do YouTube por Região",
                    barmode="group",
                    labels={
                        "region": "Região",
                        "value": "Valor Médio",
                        "variable": "Métrica"
                    },
                )
            else:
                engagement_fig = px.bar(title="Métricas de engajamento não disponíveis")
            
            # Criar gráfico de categorias por região para YouTube
            try:
                if "top_category" in regional_df.columns:
                    # Adicionar um formato de porcentagem para a taxa de engajamento
                    regional_df['engagement_pct'] = regional_df['avg_engagement'] * 100
                    
                    categories_fig = px.bar(
                        regional_df,
                        x="region",
                        y="engagement_pct",
                        color="top_category",
                        title="Categorias Populares por Região (YouTube)",
                        labels={
                            "region": "Região",
                            "engagement_pct": "Taxa de Engajamento (%)",
                            "top_category": "Categoria Principal"
                        },
                        text_auto='.2f'
                    )
                    
                    # Adicionar texto sobre as barras
                    categories_fig.update_traces(texttemplate='%{text}%', textposition='outside')
                    
                    # Melhorar o layout do gráfico
                    categories_fig.update_layout(
                        xaxis_title="Região",
                        yaxis_title="Taxa de Engajamento (%)",
                        legend_title="Categoria de Vídeos",
                        legend=dict(
                            orientation="h", 
                            yanchor="bottom", 
                            y=1.02, 
                            xanchor="right", 
                            x=1
                        )
                    )
                else:
                    categories_fig = px.bar(title="Dados de categorias não disponíveis")
            except Exception as e:
                print(f"Erro ao criar gráfico de categorias do YouTube por região: {str(e)}")
                categories_fig = px.bar(title="Erro ao criar gráfico de categorias")
        else:  # platform == "spotify"
            # Gráfico para Spotify: popularidade média
            if "avg_popularity" in regional_df.columns:
                engagement_fig = px.bar(
                    regional_df,
                    x="region",
                    y="avg_popularity",
                    title="Popularidade Média no Spotify por Região",
                    color="avg_popularity",
                    color_continuous_scale="Viridis",
                    text_auto='.1f',
                    labels={
                        "region": "Região",
                        "avg_popularity": "Popularidade Média (0-100)"
                    },
                )
                
                engagement_fig.update_layout(
                    coloraxis_showscale=False
                )
            else:
                engagement_fig = px.bar(title="Métricas de popularidade não disponíveis")
            
            # Criar gráfico de gêneros por região para Spotify
            try:
                if "top_genre" in regional_df.columns:
                    categories_fig = px.bar(
                        regional_df,
                        x="region",
                        y="genre_count" if "genre_count" in regional_df.columns else 10,
                        color="top_genre",
                        title="Gêneros Musicais Populares por Região (Spotify)",
                        labels={
                            "region": "Região",
                            "genre_count": "Quantidade de Músicas",
                            "top_genre": "Gênero Principal"
                        },
                        text="top_genre"
                    )
                    
                    # Personalizar layout
                    categories_fig.update_layout(
                        xaxis_title="Região",
                        yaxis_title="Quantidade de Músicas",
                        legend_title="Gênero Principal",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )                
                    
                else:
                    categories_fig = px.bar(title="Dados de gêneros não disponíveis")
            except Exception as e:
                print(f"Erro ao criar gráfico de gêneros do Spotify por região: {str(e)}")
                categories_fig = px.bar(title="Erro ao criar gráfico de gêneros")
            
        # Preparar mensagem de sucesso com detalhes
        if region_count > 0:
            regions_list = ', '.join(regional_df['region'].tolist())
            region_type_text = "países" if region_type == "countries" else "regiões do Brasil"
            if platform == "youtube":
                success_message = f"Análise regional do YouTube concluída para {region_count} {region_type_text}: {regions_list}"
            else:
                success_message = f"Análise regional do Spotify concluída para {region_count} {region_type_text}: {regions_list}"
        else:
            success_message = "Análise regional concluída, mas nenhuma região foi analisada."
        
        return data, True, success_message, str(region_count), engagement_fig, categories_fig
    
    except Exception as e:
        print(f"Erro na análise regional: {str(e)}")
        empty_fig = px.bar(title="Erro na análise")
        return {}, True, f"Erro na análise regional: {str(e)}", "0", empty_fig, empty_fig

# Callback para analisar dados do Spotify
@app.callback(
    [
        Output("spotify-artists-graph", "figure"),
        Output("spotify-audio-features-graph", "figure"),
        Output("spotify-genres-graph", "figure"),
        Output("spotify-releases-graph", "figure"),
        Output("spotify-track-stats", "children"),
        Output("status-modal", "is_open", allow_duplicate=True),
        Output("modal-body", "children", allow_duplicate=True),
    ],
    [Input("analyze-spotify-button", "n_clicks")],
    [State("spotify-data-store", "data")],
    prevent_initial_call=True,
)
def analyze_spotify(n_clicks, spotify_data):
    if not n_clicks or not spotify_data:
        return {}, {}, {}, {}, html.Div("Sem dados para exibir."), False, ""
    
    try:
        # Carregar dados do Spotify do armazenamento usando StringIO para evitar warnings
        from io import StringIO
        import json
        
        # Verificando o formato dos dados
        if isinstance(spotify_data.get("tracks"), str):
            spotify_tracks_df = pd.read_json(StringIO(spotify_data["tracks"]), orient="split") if spotify_data.get("tracks") else None
            spotify_artists_df = pd.read_json(StringIO(spotify_data["artists"]), orient="split") if spotify_data.get("artists") else None
            spotify_playlists_df = pd.read_json(StringIO(spotify_data["playlists"]), orient="split") if spotify_data.get("playlists") else None
        else:
            # Caso os dados já estejam em formato Python (dict/list)
            spotify_tracks_df = pd.DataFrame(spotify_data.get("tracks")) if spotify_data.get("tracks") else None
            spotify_artists_df = pd.DataFrame(spotify_data.get("artists")) if spotify_data.get("artists") else None
            spotify_playlists_df = pd.DataFrame(spotify_data.get("playlists")) if spotify_data.get("playlists") else None
        
        # Verificar se temos dados para analisar
        if spotify_tracks_df is None or spotify_artists_df is None:
            empty_fig = px.bar(title="Dados não disponíveis")
            return empty_fig, empty_fig, empty_fig, empty_fig, html.Div("Dados do Spotify não disponíveis."), True, "Dados do Spotify não encontrados. Por favor, extraia os dados primeiro."
          # Atualizar os DataFrames no analisador
        analyzer.spotify_tracks_df = spotify_tracks_df
        analyzer.spotify_artists_df = spotify_artists_df
        if spotify_playlists_df is not None:
            analyzer.spotify_playlists_df = spotify_playlists_df
            
        # Realizar análise mais completa
        results = analyzer.analyze_spotify_trends()
        if not results:
            empty_fig = px.bar(title="Falha na análise")
            return empty_fig, empty_fig, empty_fig, empty_fig, html.Div("Falha na análise."), True, "Falha ao analisar dados do Spotify."
            
        # Criar gráfico de artistas mais ouvidos por gênero musical
        if 'genre' in spotify_tracks_df.columns and 'artist' in spotify_tracks_df.columns:
            try:
                # Obter os principais gêneros
                top_genres = spotify_tracks_df['genre'].value_counts().head(5).index.tolist()
                  # Criar DataFrame de artistas por gênero
                genre_artists_data = []
                for genre in top_genres:
                    # Filtrar faixas do gênero atual
                    genre_tracks = spotify_tracks_df[spotify_tracks_df['genre'] == genre]
                    
                    # Obter contagem de artistas neste gênero
                    artists_count = genre_tracks['artist'].value_counts().reset_index()
                    artists_count.columns = ['artist', 'track_count']
                    artists_count['genre'] = genre
                    
                    # Adicionar informação de popularidade se disponível
                    if 'popularity' in genre_tracks.columns:
                        # Calcular popularidade média de cada artista dentro do gênero
                        artist_popularity = genre_tracks.groupby('artist')['popularity'].mean().reset_index()
                        pop_dict = dict(zip(artist_popularity['artist'], artist_popularity['popularity']))
                        artists_count['popularity'] = artists_count['artist'].map(lambda x: pop_dict.get(x, 0))
                    else:
                        artists_count['popularity'] = 0
                    
                    # Pegar os 10 artistas principais deste gênero (ao invés de apenas 3)
                    genre_artists_data.append(artists_count.head(10))
                
                # Combinar todos os dados
                if genre_artists_data:
                    genre_artists_df = pd.concat(genre_artists_data)
                      # Criar gráfico de artistas por gênero (formato de subplots)
                    # Criamos um subplot para cada gênero para melhor visualização dos top 10 artistas
                    
                    # Determinar número de linhas e colunas para o grid de subplots
                    n_genres = len(top_genres)
                    n_cols = min(2, n_genres)  # Máximo 2 colunas
                    n_rows = (n_genres + 1) // 2  # Arredondar para cima
                    
                    # Criar figura com subplots
                    fig = make_subplots(
                        rows=n_rows, 
                        cols=n_cols,
                        subplot_titles=[f"Top Artistas: {genre}" for genre in top_genres],
                        vertical_spacing=0.1,
                        horizontal_spacing=0.05
                    )
                    
                    # Cores diferentes para cada gênero
                    colors = px.colors.qualitative.Plotly
                    
                    # Adicionar barras para cada gênero em seu respectivo subplot
                    for i, genre in enumerate(top_genres):
                        row = i // n_cols + 1
                        col = i % n_cols + 1
                        
                        # Filtrar dados para este gênero
                        genre_data = genre_artists_df[genre_artists_df['genre'] == genre].sort_values('popularity', ascending=False)
                        
                        # Adicionar barras ao subplot
                        fig.add_trace(
                            go.Bar(
                                x=genre_data['track_count'], 
                                y=genre_data['artist'],
                                orientation='h',
                                name=genre,
                                marker_color=colors[i % len(colors)],
                                text=genre_data['track_count'],
                                hovertemplate='<b>%{y}</b><br>'+
                                              'Faixas: %{x}<br>'+
                                              'Popularidade: %{customdata[0]:.1f}/100<extra></extra>',
                                customdata=np.column_stack([genre_data['popularity']])
                            ),
                            row=row, col=col
                        )
                        
                        # Configuração do layout para cada subplot
                        fig.update_xaxes(title_text="Número de Faixas", row=row, col=col)
                        fig.update_yaxes(title_text="", row=row, col=col, autorange="reversed")
                    
                    # Configuração global do layout
                    fig.update_layout(
                        height=200 * n_rows + 150,  # Altura dinâmica baseada no número de gêneros
                        title={
                            'text': "Top 10 Artistas por Gênero Musical",
                            'y': 0.98,
                            'x': 0.5,
                            'xanchor': 'center',
                            'yanchor': 'top',
                            'font': {'size': 20}
                        },
                        showlegend=False,
                        margin=dict(t=100, b=50, l=10, r=10),
                    )
                    
                    # Formatação dos textos nas barras
                    fig.update_traces(texttemplate='%{text}', textposition='outside')
                    
                    # Usar a figura criada
                    artists_fig = fig
                else:
                    artists_fig = px.bar(title="Não foi possível encontrar artistas por gênero")
            except Exception as e:
                print(f"Erro ao criar gráfico de artistas por gênero: {str(e)}")
                artists_fig = px.bar(title=f"Erro ao criar gráfico de artistas por gênero: {str(e)}")
        else:            # Fallback para o gráfico original se não tiver informação de gênero
            if 'top_artists_by_count' in results and not results['top_artists_by_count'].empty:
                top_artists = results['top_artists_by_count'].head(10)
                if 'popularity' in results.get('top_artists_by_popularity', {}) and not results['top_artists_by_popularity'].empty:
                    pop_dict = dict(zip(results['top_artists_by_popularity']['artist'], 
                                       results['top_artists_by_popularity']['popularity']))
                    top_artists['popularity'] = top_artists['artist'].map(lambda x: pop_dict.get(x, 0))
                else:
                    top_artists['popularity'] = 0
                
                # Organizar artistas por popularidade
                top_artists = top_artists.sort_values('popularity', ascending=False)
                
                # Criar uma visualização mais elegante
                fig = go.Figure()
                
                # Adicionar barras coloridas por popularidade
                fig.add_trace(go.Bar(
                    x=top_artists['track_count'],
                    y=top_artists['artist'],
                    orientation='h',
                    marker=dict(
                        color=top_artists['popularity'],
                        colorscale='Viridis',
                        colorbar=dict(title="Popularidade"),
                        showscale=True
                    ),
                    text=top_artists['track_count'],
                    hovertemplate='<b>%{y}</b><br>'+
                                  'Faixas: %{x}<br>'+
                                  'Popularidade: %{marker.color:.1f}/100<extra></extra>'
                ))
                
                # Melhorar layout
                fig.update_layout(
                    title={
                        'text': "Top 10 Artistas Mais Populares no Spotify",
                        'y':0.95,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font': {'size': 20}
                    },
                    xaxis_title="Número de Faixas",
                    yaxis_title="",
                    yaxis={'categoryorder':'total descending'},
                    height=500,
                    margin=dict(l=10, r=10, t=80, b=30),
                    plot_bgcolor='rgba(240,240,255,0.2)'
                )
                
                # Adicionar textos às barras
                fig.update_traces(texttemplate='%{text}', textposition='outside')
                
                # Usar a figura criada
                artists_fig = fig
            else:
                artists_fig = px.bar(title="Dados de artistas não disponíveis")

        # Criar gráfico de características de áudio com marcações melhoradas
        audio_features = ['danceability', 'energy', 'speechiness', 'acousticness',
                          'instrumentalness', 'liveness', 'valence']

        available_features = [f for f in audio_features if f in spotify_tracks_df.columns]

        if available_features:
            features_df = spotify_tracks_df[available_features].melt(var_name='feature', value_name='value')
            
            # Criar dicionário para descrições das características
            feature_descriptions = {
                'danceability': 'Dançabilidade (0-1)',
                'energy': 'Energia (0-1)',
                'speechiness': 'Vocais Falados (0-1)',
                'acousticness': 'Elementos Acústicos (0-1)',
                'instrumentalness': 'Instrumental (0-1)',
                'liveness': 'Elementos ao Vivo (0-1)',
                'valence': 'Valência/Positividade (0-1)'
            }
            
            # Mapear para nomes mais amigáveis em português
            features_df['feature_name'] = features_df['feature'].map(lambda x: feature_descriptions.get(x, x))
            
            audio_features_fig = px.violin(
                features_df,
                x="feature_name",
                y="value",
                box=True,
                title="Distribuição de Características de Áudio",
                labels={
                    "feature_name": "Característica", 
                    "value": "Valor"
                },
                color="feature_name",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            # Adicionar linha de referência para o valor médio (0.5)
            audio_features_fig.add_shape(
                type='line',
                x0=-0.5,
                x1=len(available_features)-0.5,
                y0=0.5,
                y1=0.5,
                line=dict(color='gray', width=1, dash='dash')
            )
            
            # Melhorar layout
            audio_features_fig.update_layout(
                legend_title="Característica",
                showlegend=False
            )
        else:
            audio_features_fig = px.bar(title="Dados de características de áudio não disponíveis")
        
        # Criar novo gráfico de popularidade por gênero musical
        genres_fig = px.bar(title="Dados de gêneros não disponíveis")
        if 'top_genres' in results and not results['top_genres'].empty:
            genres_data = results['top_genres'].head(10).copy()
            
            # Calcular popularidade média por gênero se possível
            if 'genre' in spotify_tracks_df.columns and 'popularity' in spotify_tracks_df.columns:
                genre_popularity = spotify_tracks_df.groupby('genre')['popularity'].mean().reset_index()
                genre_pop_dict = dict(zip(genre_popularity['genre'], genre_popularity['popularity']))
                genres_data['avg_popularity'] = genres_data['genre'].map(lambda x: genre_pop_dict.get(x, 0))
            else:
                # Gerar valores simulados para demonstração
                genres_data['avg_popularity'] = np.random.randint(60, 95, size=len(genres_data))
            
            # Criando gráfico de popularidade por gênero
            genres_fig = px.bar(
                genres_data,
                y="genre",
                x="count",
                orientation="h",
                color="avg_popularity",
                color_continuous_scale="Viridis",
                title="Popularidade por Gênero Musical",
                labels={
                    "genre": "Gênero Musical", 
                    "count": "Número de Faixas",
                    "avg_popularity": "Popularidade Média"
                },
                text="count"
            )
            
            # Melhorar layout
            genres_fig.update_traces(texttemplate='%{text}', textposition='outside')
            genres_fig.update_layout(
                yaxis={'categoryorder':'total ascending'},
                coloraxis_colorbar=dict(title="Popularidade")
            )
        
        # Criar gráfico de análise temporal de lançamentos
        releases_fig = px.bar(title="Dados temporais não disponíveis")
        if 'album_date' in spotify_tracks_df.columns or 'release_date' in spotify_tracks_df.columns:
            # Determinar qual coluna usar
            date_col = 'album_date' if 'album_date' in spotify_tracks_df.columns else 'release_date'
            
            # Converter para datetime e extrair ano
            try:
                spotify_tracks_df['release_year'] = pd.to_datetime(spotify_tracks_df[date_col]).dt.year
                
                # Agrupar por ano e contar
                yearly_releases = spotify_tracks_df.groupby('release_year').size().reset_index(name='count')
                
                # Filtrar anos válidos (remover outliers e focar nos últimos 20 anos)
                current_year = pd.Timestamp.now().year
                yearly_releases = yearly_releases[
                    (yearly_releases['release_year'] > current_year - 20) & 
                    (yearly_releases['release_year'] <= current_year)
                ]
                
                # Criar gráfico de linha de tendências de lançamento
                releases_fig = px.line(
                    yearly_releases,
                    x="release_year",
                    y="count",
                    title="Tendência de Lançamentos por Ano",
                    markers=True,
                    labels={
                        "release_year": "Ano de Lançamento", 
                        "count": "Número de Faixas"
                    }
                )
                
                # Adicionar área sob a curva
                releases_fig.add_trace(
                    go.Scatter(
                        x=yearly_releases["release_year"],
                        y=yearly_releases["count"],
                        fill='tozeroy',
                        fillcolor='rgba(26, 150, 65, 0.2)',
                        line=dict(color='rgba(26, 150, 65, 0.8)'),
                        name="Lançamentos"
                    )
                )
                
                # Melhorar layout
                releases_fig.update_layout(showlegend=False)
                releases_fig.update_xaxes(dtick=1)  # Mostrar cada ano no eixo X
            except Exception as e:
                print(f"Erro ao processar datas: {str(e)}")
                releases_fig = px.bar(title=f"Não foi possível analisar dados temporais: {str(e)}")
        
        # Criar estatísticas aprimoradas das faixas com layout mais atraente
        stats_children = []
        
        # Título principal com contagem de faixas
        track_count = len(spotify_tracks_df)
        artist_count = len(spotify_tracks_df['artist'].unique()) if 'artist' in spotify_tracks_df.columns else 0
        stats_children.append(html.H4(f"Análise de {track_count} Faixas e {artist_count} Artistas"))
        
        # Criar cards para métricas principais
        metrics_row = []
        
        if 'avg_track_popularity' in results:
            metrics_row.append(
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Popularidade Média"),
                        dbc.CardBody(html.H2(f"{results['avg_track_popularity']:.1f}/100"))
                    ], className="text-center h-100"),
                    width=12, md=3, className="mb-3"
                )
            )
        
        if 'avg_duration_min' in results:
            metrics_row.append(
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Duração Média"),
                        dbc.CardBody(html.H2(f"{results['avg_duration_min']:.2f} min"))
                    ], className="text-center h-100"),
                    width=12, md=3, className="mb-3"
                )
            )
        
        # Adicionar métricas de características de áudio populares
        if 'danceability' in spotify_tracks_df.columns:
            dance_avg = spotify_tracks_df['danceability'].mean()
            metrics_row.append(
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Dançabilidade"),
                        dbc.CardBody(html.H2(f"{dance_avg:.2f}"))
                    ], className="text-center h-100"),
                    width=12, md=3, className="mb-3"
                )
            )
        
        if 'energy' in spotify_tracks_df.columns:
            energy_avg = spotify_tracks_df['energy'].mean()
            metrics_row.append(
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Energia"),
                        dbc.CardBody(html.H2(f"{energy_avg:.2f}"))
                    ], className="text-center h-100"),
                    width=12, md=3, className="mb-3"
                )
            )
        
        # Adicionar cards à visualização
        if metrics_row:
            stats_children.append(dbc.Row(metrics_row))
          # Adicionar seção para os artistas mais populares com estatísticas completas
        if 'top_artists_by_count' in results and not results['top_artists_by_count'].empty:
            stats_children.append(html.H5("Top 10 Artistas - Estatísticas Completas", className="mt-4 mb-3 text-primary"))
            
            top_artists = results['top_artists_by_count'].head(10)
            
            # Adicionar popularidade se disponível
            if 'popularity' in results.get('top_artists_by_popularity', {}) and not results['top_artists_by_popularity'].empty:
                pop_dict = dict(zip(results['top_artists_by_popularity']['artist'], 
                                   results['top_artists_by_popularity']['popularity']))
                top_artists['popularity'] = top_artists['artist'].map(lambda x: pop_dict.get(x, 0))
            else:
                top_artists['popularity'] = 0
                
            # Calcular métricas adicionais por artista se possível
            if 'artist' in spotify_tracks_df.columns:
                # Calcular popularidade média das faixas por artista
                if 'popularity' in spotify_tracks_df.columns:
                    artist_pop = spotify_tracks_df.groupby('artist')['popularity'].mean().reset_index()
                    pop_dict = dict(zip(artist_pop['artist'], artist_pop['popularity']))
                    top_artists['avg_track_popularity'] = top_artists['artist'].map(lambda x: pop_dict.get(x, 0))
                    
                # Calcular dançabilidade média das faixas do artista (se disponível)
                if 'danceability' in spotify_tracks_df.columns:
                    artist_dance = spotify_tracks_df.groupby('artist')['danceability'].mean().reset_index()
                    dance_dict = dict(zip(artist_dance['artist'], artist_dance['danceability']))
                    top_artists['danceability'] = top_artists['artist'].map(lambda x: dance_dict.get(x, 0))
                    
                # Calcular energia média das faixas do artista (se disponível)
                if 'energy' in spotify_tracks_df.columns:
                    artist_energy = spotify_tracks_df.groupby('artist')['energy'].mean().reset_index()
                    energy_dict = dict(zip(artist_energy['artist'], artist_energy['energy']))
                    top_artists['energy'] = top_artists['artist'].map(lambda x: energy_dict.get(x, 0))
            
            # Criar tabela avançada com os artistas
            artists_table = dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("#", style={"width": "5%"}), 
                        html.Th("Artista", style={"width": "30%"}), 
                        html.Th("Faixas", style={"width": "10%"}),
                        html.Th("Popularidade", style={"width": "25%"}),
                        html.Th("Características", style={"width": "30%"})
                    ], className="table-primary")
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td(f"{i+1}", className="fw-bold"),
                        html.Td(html.Strong(artist['artist'])),
                        html.Td(f"{artist['track_count']}"),
                        html.Td([
                            html.Div(className="progress", style={"height": "20px"}, children=[
                                html.Div(
                                    className="progress-bar bg-success",
                                    style={"width": f"{artist['popularity']}%"},
                                    children=f"{artist['popularity']:.1f}"
                                )
                            ])
                        ]),
                        html.Td([
                            html.Span([
                                html.I(className="fas fa-music me-1"), 
                                f"Dance: {artist.get('danceability', 0):.2f}"
                            ], className="badge bg-info me-2"),
                            html.Span([
                                html.I(className="fas fa-bolt me-1"),
                                f"Energy: {artist.get('energy', 0):.2f}"
                            ], className="badge bg-warning")
                        ])
                    ]) for i, (_, artist) in enumerate(top_artists.iterrows())
                ])
            ], bordered=True, hover=True, responsive=True, size="sm", className="mt-2 shadow-sm")
            
            stats_children.append(artists_table)
        
        # Adicionar detalhes sobre gêneros principais
        if 'top_genres' in results and not results['top_genres'].empty:
            stats_children.append(html.H5("Principais Gêneros Musicais", className="mt-4 mb-3 text-primary"))
            
            # Criar tabela de gêneros com contagem
            genres_table = dbc.Table([
                html.Thead([
                    html.Tr([html.Th("Gênero"), html.Th("Contagem"), html.Th("% do Total")])
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td(row['genre']), 
                        html.Td(f"{row['count']:,}"),
                        html.Td(f"{row['count']/track_count*100:.1f}%")
                    ]) for _, row in results['top_genres'].head(5).iterrows()
                ])
            ], bordered=True, hover=True, responsive=True, size="sm", className="mt-2 shadow-sm")
            
            stats_children.append(genres_table)
        
        # Adicionar top faixas por popularidade
        if 'title' in spotify_tracks_df.columns and 'popularity' in spotify_tracks_df.columns:
            stats_children.append(html.H5("Faixas Mais Populares", className="mt-4 mb-3 text-primary"))
            
            top_tracks = spotify_tracks_df.sort_values('popularity', ascending=False).head(5)
            
            tracks_table = dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Título"), 
                        html.Th("Artista"), 
                        html.Th("Popularidade"),
                        html.Th("Características")
                    ])
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td(track['title']), 
                        html.Td(html.Strong(track['artist']) if 'artist' in track else '-'),
                        html.Td([
                            html.Div(className="progress", style={"height": "20px"}, children=[
                                html.Div(
                                    className="progress-bar bg-danger",
                                    style={"width": f"{track['popularity']}%"},
                                    children=f"{track['popularity']}/100"
                                )
                            ])
                        ]),
                        html.Td([
                            html.Small([
                                html.Span(f"Dance: {track.get('danceability', 0):.2f}", className="me-2"),
                                html.Span(f"Energy: {track.get('energy', 0):.2f}", className="me-2"),
                                html.Span(f"Valence: {track.get('valence', 0):.2f}")
                            ])
                        ])
                    ]) for _, track in top_tracks.iterrows()
                ])
            ], bordered=True, hover=True, responsive=True, size="sm", className="mt-2 shadow-sm")
            
            stats_children.append(tracks_table)
        
        # Adicionar insights sobre características das músicas
        if 'danceability' in spotify_tracks_df.columns and 'energy' in spotify_tracks_df.columns:
            stats_children.append(html.H5("Insights sobre Características Musicais", className="mt-4"))
            
            # Algumas análises interessantes
            high_energy = spotify_tracks_df[spotify_tracks_df['energy'] > 0.8].shape[0]
            high_dance = spotify_tracks_df[spotify_tracks_df['danceability'] > 0.8].shape[0]
            
            insights_list = [
                html.Li(f"{high_energy} faixas ({high_energy/track_count*100:.1f}%) têm alta energia (>0.8)"),
                html.Li(f"{high_dance} faixas ({high_dance/track_count*100:.1f}%) têm alta dançabilidade (>0.8)")
            ]
            
            if 'valence' in spotify_tracks_df.columns:
                happy_tracks = spotify_tracks_df[spotify_tracks_df['valence'] > 0.8].shape[0]
                sad_tracks = spotify_tracks_df[spotify_tracks_df['valence'] < 0.2].shape[0]
                insights_list.extend([
                    html.Li(f"{happy_tracks} faixas ({happy_tracks/track_count*100:.1f}%) têm alta valência/positividade (>0.8)"),
                    html.Li(f"{sad_tracks} faixas ({sad_tracks/track_count*100:.1f}%) têm baixa valência/positividade (<0.2)")
                ])
            
            stats_children.append(html.Ul(insights_list, className="mt-2"))
        
        stats_div = html.Div(stats_children) if stats_children else html.Div("Sem estatísticas disponíveis.")
        
        return artists_fig, audio_features_fig, genres_fig, releases_fig, stats_div, True, "Análise do Spotify concluída com sucesso!"
    except Exception as e:
        print(f"Erro na análise do Spotify: {str(e)}")
        empty_fig = px.bar(title="Erro na análise")
        return empty_fig, empty_fig, empty_fig, empty_fig, html.Div("Erro na análise."), True, f"Erro ao analisar dados do Spotify: {str(e)}"

# Callback para analisar dados do YouTube
@app.callback(    [
        Output("youtube-category-engagement-graph", "figure"),
        Output("youtube-views-engagement-graph", "figure"),
        Output("youtube-comments-likes-graph", "figure"),
        Output("youtube-category-views-graph", "figure"),
        Output("youtube-category-likes-graph", "figure"),
        Output("youtube-category-comments-graph", "figure"),
        Output("status-modal", "is_open", allow_duplicate=True),
        Output("modal-body", "children", allow_duplicate=True),
    ],
    [Input("analyze-youtube-button", "n_clicks")],
    [State("youtube-data-store", "data")],
    prevent_initial_call=True,
)
def analyze_youtube(n_clicks, youtube_data):
    if not n_clicks or not youtube_data:
        empty_fig = px.bar(title="Sem dados para exibir")
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, False, ""

    try:
        # Carregar dados do YouTube do armazenamento usando StringIO
        from io import StringIO
        import json
        import traceback
        
        # Verificando o formato dos dados
        if isinstance(youtube_data.get("videos"), str):
            youtube_videos_df = pd.read_json(StringIO(youtube_data["videos"]), orient="split") if youtube_data.get("videos") else None
            youtube_categories_df = pd.read_json(StringIO(youtube_data["categories"]), orient="split") if youtube_data.get("categories") else None        
        else:
            # Caso os dados já estejam em formato Python (dict/list)
            youtube_videos_df = pd.DataFrame(youtube_data.get("videos")) if youtube_data.get("videos") else None
            youtube_categories_df = pd.DataFrame(youtube_data.get("categories")) if youtube_data.get("categories") else None        # Verificar se temos dados para analisar
        if youtube_videos_df is None or youtube_videos_df.empty:
            empty_fig = px.bar(title="Sem dados para exibir")
            return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, True, "Dados do YouTube não encontrados. Por favor, extraia os dados primeiro."

        # Atualizar os DataFrames no analisador
        analyzer.youtube_videos_df = youtube_videos_df
        analyzer.youtube_categories_df = youtube_categories_df        # Realizar análise
        results = analyzer.analyze_youtube_trends()
        if not results:
            empty_fig = px.bar(title="Falha na análise")
            return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, True, "Falha ao analisar dados do YouTube."

        # Pré-processamento adicional dos dados para análises mais robustas
        if 'published_at' in youtube_videos_df.columns and 'published_date' not in youtube_videos_df.columns:
            youtube_videos_df['published_date'] = pd.to_datetime(youtube_videos_df['published_at'])
            youtube_videos_df['publish_day'] = youtube_videos_df['published_date'].dt.day_name()
            youtube_videos_df['publish_hour'] = youtube_videos_df['published_date'].dt.hour
            
        # Calcular métricas derivadas para engajamento
        if 'view_count' in youtube_videos_df.columns and 'like_count' in youtube_videos_df.columns:
            # Taxa de likes por visualização
            youtube_videos_df['like_rate'] = youtube_videos_df['like_count'] / youtube_videos_df['view_count'].where(youtube_videos_df['view_count'] > 0, 1)
            # Taxa de comentários por visualização
            if 'comment_count' in youtube_videos_df.columns:
                youtube_videos_df['comment_rate'] = youtube_videos_df['comment_count'] / youtube_videos_df['view_count'].where(youtube_videos_df['view_count'] > 0, 1)
        
        # Criar gráfico de engajamento por categoria com informações mais detalhadas
        # Removendo a lógica de tradução
        if 'category_name' in youtube_videos_df.columns:
            # Análise mais detalhada por categoria
            category_stats = youtube_videos_df.groupby('category_name').agg({
                'view_count': ['mean', 'median', 'count', 'sum'],
                'like_count': ['mean', 'sum'],
                'comment_count': ['mean', 'sum'],
                'engagement_rate': 'mean',
                'like_rate': 'mean',
                'comment_rate': 'mean'
            }).reset_index()
            
            # Tornar o formato das colunas mais amigável
            category_stats.columns = ['_'.join(col).strip('_') for col in category_stats.columns.values]
            
            # Renomear para melhor clareza
            category_stats = category_stats.rename(columns={
                'category_name_': 'category_name',
                'view_count_count': 'video_count'
            })
            
            # Ordenar pelo engajamento médio para visualização mais clara
            category_stats = category_stats.sort_values('engagement_rate_mean', ascending=False)
            
            # Criar primeiro gráfico de barras para taxa de engajamento
            category_fig = px.bar(
                category_stats,
                y="category_name",
                x="engagement_rate_mean",
                text="video_count",
                orientation="h",
                title="Taxa Média de Engajamento por Categoria",
                labels={
                    "category_name": "Categoria",
                    "engagement_rate_mean": "Taxa de Engajamento Média",
                    "video_count": "Número de Vídeos"
                },
                color="view_count_mean",
                color_continuous_scale=px.colors.sequential.Viridis,
                hover_data=["like_rate_mean", "comment_rate_mean", "view_count_mean"]
            )
            
            # Melhorar a aparência do gráfico
            category_fig.update_traces(
                texttemplate='%{text} vídeos', 
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Taxa de Engajamento: %{x:.4f}<br>Taxa de Likes: %{customdata[0]:.4f}<br>Taxa de Comentários: %{customdata[1]:.4f}<br>Visualizações médias: %{customdata[2]:,.0f}<br>Vídeos: %{text}'
            )
            
            category_fig.update_layout(
                coloraxis_colorbar=dict(
                    title="Visualizações<br>Médias"
                )
            )
        else:
            category_fig = px.bar(title="Dados de categorias não disponíveis")
        
        # Análise de horário de publicação e engajamento (se disponível)
        if 'publish_hour' in youtube_videos_df.columns:
            hourly_engagement = youtube_videos_df.groupby('publish_hour').agg({
                'engagement_rate': 'mean',
                'view_count': 'mean',
                'id': 'count'
            }).reset_index()
            
            # Adicionar ao dataframe atual para visualizações
            hourly_data = hourly_engagement
        
        # Criar gráfico avançado de visualizações vs. engajamento
        # Se statsmodels estiver disponível, usamos um scatter plot com trendline
        # Caso contrário, usamos um scatter plot simples
        has_statsmodels = True
        try:
            import statsmodels.api
        except ImportError:
            has_statsmodels = False
            print("Módulo statsmodels não encontrado. A linha de tendência não será exibida.")
        
        # Verificamos se a coluna categoria existe no DataFrame
        if 'category_name' in youtube_videos_df.columns:
            # Parâmetros base para o gráfico
            scatter_params = {
                'data_frame': youtube_videos_df,
                'x': "view_count",
                'y': "engagement_rate",
                'color': "category_name",  # Usando diretamente category_name sem tradução
                'size': "like_count",
                'hover_name': "title",
                'log_x': True,
                'labels': {
                    "view_count": "Visualizações (escala log)",
                    "engagement_rate": "Taxa de Engajamento",
                    "category_name": "Categoria",
                    "like_count": "Curtidas"
                },
                'hover_data': {
                    "channel_title": True,
                    "published_date": "| %d/%m/%Y" if "published_date" in youtube_videos_df.columns else False,
                    "like_count": True,
                    "comment_count": True,
                    "view_count": ':,.0f'
                }
            }
            
            # Adicionar trendline apenas se statsmodels estiver disponível
            if has_statsmodels:
                scatter_params['trendline'] = "ols"
                scatter_params['trendline_scope'] = "overall"
                scatter_params['title'] = "Visualizações vs. Taxa de Engajamento (com Tendência)"
            else:
                scatter_params['title'] = "Visualizações vs. Taxa de Engajamento"
            
            views_engagement_fig = px.scatter(**scatter_params)
            
            # Melhorar layout
            views_engagement_fig.update_layout(
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                xaxis=dict(
                    title="Visualizações (escala logarítmica)"
                ),
                yaxis=dict(
                    title="Taxa de Engajamento",
                    tickformat=".4f"
                )
            )
        else:
            views_engagement_fig = px.scatter(
                youtube_videos_df,
                x="view_count",
                y="engagement_rate",
                hover_name="title",
                log_x=True,
                title="Visualizações vs. Taxa de Engajamento",
                labels={
                    "view_count": "Visualizações (escala log)",
                    "engagement_rate": "Taxa de Engajamento"
                }
            )
        
        # Adicionar insights para estatísticas dos vídeos com análise mais detalhada
        stats_children = []
        
        # Título principal com contagem total de vídeos
        video_count = len(youtube_videos_df)
        stats_children.append(html.H5(f"Análise de {video_count} Vídeos do YouTube"))
          # Estatísticas de visualização e engajamento
        total_views = youtube_videos_df['view_count'].sum()
        total_likes = youtube_videos_df['like_count'].sum() if 'like_count' in youtube_videos_df.columns else 0
        total_comments = youtube_videos_df['comment_count'].sum() if 'comment_count' in youtube_videos_df.columns else 0
        
        # Calcular métricas adicionais
        avg_engagement = youtube_videos_df['engagement_rate'].mean() if 'engagement_rate' in youtube_videos_df.columns else 0
        total_duration = youtube_videos_df['duration_seconds'].sum() / 3600 if 'duration_seconds' in youtube_videos_df.columns else 0
        
        # Layout em grid para métricas principais (usando Bootstrap)
        metrics_grid = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([html.I(className="fas fa-eye me-2"), "Total de Visualizações"]),
                    dbc.CardBody(html.H4(f"{total_views:,.0f}"))
                ], className="text-center h-100", style=custom_styles["card_shadow"])
            ], width=12, md=4, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([html.I(className="fas fa-thumbs-up me-2"), "Total de Likes"]),
                    dbc.CardBody(html.H4(f"{total_likes:,.0f}"))
                ], className="text-center h-100", style=custom_styles["card_shadow"])
            ], width=12, md=4, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([html.I(className="fas fa-comment me-2"), "Total de Comentários"]),
                    dbc.CardBody(html.H4(f"{total_comments:,.0f}"))
                ], className="text-center h-100", style=custom_styles["card_shadow"])
            ], width=12, md=4, className="mb-3"),
        ])
        
        # Segunda linha de métricas adicionais
        additional_metrics = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([html.I(className="fas fa-percentage me-2"), "Taxa Média de Engajamento"]),
                    dbc.CardBody(html.H4(f"{avg_engagement:.2%}"))
                ], className="text-center h-100", style=custom_styles["card_shadow"])
            ], width=12, md=4, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([html.I(className="fas fa-clock me-2"), "Horas Total de Conteúdo"]),
                    dbc.CardBody(html.H4(f"{total_duration:,.1f} horas"))
                ], className="text-center h-100", style=custom_styles["card_shadow"])
            ], width=12, md=4, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([html.I(className="fas fa-video me-2"), "Total de Vídeos"]),
                    dbc.CardBody(html.H4(f"{video_count:,}"))
                ], className="text-center h-100", style=custom_styles["card_shadow"])
            ], width=12, md=4, className="mb-3"),
        ])
        
        stats_children.append(metrics_grid)
        stats_children.append(additional_metrics)
          # Médias, taxas e insights - Em formato de card mais elegante
        avg_metrics = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([html.I(className="fas fa-chart-line me-2"), "Métricas Médias"]),
                    dbc.CardBody([
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                html.I(className="fas fa-eye me-2 text-primary"),
                                f"Visualizações: ",
                                html.Strong(f"{results['avg_view_count']:,.0f}")
                            ]),
                            dbc.ListGroupItem([
                                html.I(className="fas fa-thumbs-up me-2 text-success"), 
                                f"Likes: ",
                                html.Strong(f"{results['avg_like_count']:,.0f}")
                            ]),
                            dbc.ListGroupItem([
                                html.I(className="fas fa-comment me-2 text-info"), 
                                f"Comentários: ",
                                html.Strong(f"{results['avg_comment_count']:,.0f}")
                            ]),
                            dbc.ListGroupItem([
                                html.I(className="fas fa-percentage me-2 text-warning"), 
                                f"Taxa de engajamento: ",
                                html.Strong(f"{results['avg_engagement_rate']:.4f}")
                            ]),
                        ])
                    ])
                ], style=custom_styles["card_shadow"])
            ], width=12, md=6, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([html.I(className="fas fa-lightbulb me-2"), "Insights"]),
                    dbc.CardBody([
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                html.I(className="fas fa-thumbs-up me-2 text-primary"),
                                f"Taxa média de likes: ",
                                html.Strong(f"{youtube_videos_df['like_rate'].mean():.2%}" if 'like_rate' in youtube_videos_df.columns else "N/A")
                            ]),
                            dbc.ListGroupItem([
                                html.I(className="fas fa-comment me-2 text-success"), 
                                f"Taxa média de comentários: ",
                                html.Strong(f"{youtube_videos_df['comment_rate'].mean():.2%}" if 'comment_rate' in youtube_videos_df.columns else "N/A")
                            ]),
                            dbc.ListGroupItem([
                                html.I(className="fas fa-trophy me-2 text-warning"), 
                                f"Melhor categoria: ",
                                html.Strong(f"{category_stats.iloc[0]['category_name']}" if len(category_stats) > 0 else "N/A")
                            ]),
                            dbc.ListGroupItem([
                                html.I(className="fas fa-clock me-2 text-info"), 
                                f"Duração média: ",
                                html.Strong(f"{youtube_videos_df['duration_seconds'].mean() / 60:.1f} min" if 'duration_seconds' in youtube_videos_df.columns else "N/A")
                            ]),
                        ])
                    ])
                ], style=custom_styles["card_shadow"])
            ], width=12, md=6, className="mb-3")
        ])
        
        stats_children.append(avg_metrics)
          # Top vídeos por engajamento - tabela mais elegante
        if len(youtube_videos_df) > 0:
            top_videos_engagement = youtube_videos_df.sort_values('engagement_rate', ascending=False).head(5)
            top_videos_views = youtube_videos_df.sort_values('view_count', ascending=False).head(5)
            
            stats_children.append(html.H5([html.I(className="fas fa-star me-2"), "Top 5 Vídeos por Engajamento:"], 
                                 className="mt-4 mb-3 text-primary"))
            
            top_videos_table = html.Div([
                dbc.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("#"), 
                            html.Th("Título"), 
                            html.Th("Canal"), 
                            html.Th("Visualizações"), 
                            html.Th("Engajamento")
                        ], className="table-primary")
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td(f"{i+1}", className="fw-bold"),
                            html.Td(video['title'][:50] + "..." if len(video['title']) > 50 else video['title']), 
                            html.Td(video['channel_title']),
                            html.Td(f"{video['view_count']:,.0f}"),
                            html.Td([
                                html.Span(f"{video['engagement_rate']:.4f}", className="badge bg-success")
                            ])
                        ]) for i, (_, video) in enumerate(top_videos_engagement.iterrows())
                    ])
                ], bordered=True, hover=True, responsive=True, size="sm", striped=True, className="shadow-sm")
            ])
                  # Adicionar também vídeos por visualizações
            stats_children.append(html.H5([html.I(className="fas fa-eye me-2"), "Top 5 Vídeos por Visualizações:"], 
                                 className="mt-4 mb-3 text-primary"))
                                 
            # Adicionar análises estatísticas avançadas
            if 'like_count' in youtube_videos_df.columns and 'comment_count' in youtube_videos_df.columns:
                # Calcular correlação entre visualizações, likes e comentários
                corr_matrix = youtube_videos_df[['view_count', 'like_count', 'comment_count']].corr().round(3)
                
                # Converter a matriz de correlação para um formato adequado para heatmap
                corr_df = corr_matrix.reset_index().melt(id_vars='index')
                corr_df.columns = ['Métrica 1', 'Métrica 2', 'Correlação']
                
                # Mapear os nomes das métricas para português
                metric_names = {
                    'view_count': 'Visualizações',
                    'like_count': 'Likes',
                    'comment_count': 'Comentários'
                }
                
                corr_df['Métrica 1'] = corr_df['Métrica 1'].map(metric_names)
                corr_df['Métrica 2'] = corr_df['Métrica 2'].map(metric_names)
                
                # Criar heatmap de correlação
                corr_heatmap = px.imshow(
                    corr_matrix,
                    x=corr_matrix.columns.map(metric_names),
                    y=corr_matrix.index.map(metric_names),
                    color_continuous_scale=px.colors.sequential.Blues,
                    title="Correlação entre Métricas",
                    text_auto=True,
                    aspect="auto",
                    height=250
                )
                
                # Adicionar as estatísticas avançadas após a tabela de top vídeos
                stats_children.append(html.H5([html.I(className="fas fa-chart-area me-2"), "Análise Estatística Avançada"], 
                                     className="mt-4 mb-3 text-primary"))
                stats_children.append(top_videos_table)
            
            # Tabela de vídeos por visualizações
            top_views_table = html.Div([
                dbc.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("#"), 
                            html.Th("Título"), 
                            html.Th("Canal"), 
                            html.Th("Visualizações"), 
                            html.Th("Likes")
                        ], className="table-info")
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td(f"{i+1}", className="fw-bold"),
                            html.Td(video['title'][:50] + "..." if len(video['title']) > 50 else video['title']), 
                            html.Td(video['channel_title']),
                            html.Td([
                                html.Span(f"{video['view_count']:,.0f}", className="badge bg-primary")
                            ]),
                            html.Td(f"{video['like_count']:,.0f}" if 'like_count' in video else "N/A")
                        ]) for i, (_, video) in enumerate(top_videos_views.iterrows())
                    ])
                ], bordered=True, hover=True, responsive=True, size="sm", striped=True, className="shadow-sm")
            ])         
            stats_children.append(top_views_table)
            
            # Adicionar o heatmap de correlação e métricas avançadas em um cartão
            stats_children.append(dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(figure=corr_heatmap, config={'displayModeBar': False})
                        ], width=12, md=6),
                        dbc.Col([
                            html.Div([
                                html.H6("Interpretação das Correlações:", className="mb-3"),
                                html.P([
                                    "A correlação mede a força da relação entre duas variáveis, variando de -1 a +1.",
                                    html.Ul([
                                        html.Li("Valores próximos de +1 indicam forte correlação positiva"),
                                        html.Li("Valores próximos de -1 indicam forte correlação negativa"),
                                        html.Li("Valores próximos de 0 indicam baixa correlação")
                                    ])
                                ]),
                                html.P([
                                    html.Strong("Insights:"),
                                    html.Ul([
                                        html.Li(f"Correlação entre visualizações e likes: {corr_matrix.loc['view_count', 'like_count']:.3f}"),
                                        html.Li(f"Correlação entre visualizações e comentários: {corr_matrix.loc['view_count', 'comment_count']:.3f}"),
                                        html.Li(f"Correlação entre likes e comentários: {corr_matrix.loc['like_count', 'comment_count']:.3f}")
                                    ])
                                ])
                            ])
                        ], width=12, md=6)
                    ])
                ])
            ], className="shadow-sm mb-4"))
          # Mostrar categorias principais se disponíveis
        if 'top_categories_by_count' in results and not results['top_categories_by_count'].empty:
            stats_children.append(html.H5([html.I(className="fas fa-tags me-2"), "Categorias Principais:"], 
                                 className="mt-4 mb-3 text-primary"))
            
            # Criar card com gráfico integrado para categorias
            categories_data = results['top_categories_by_count'].head(8)            # Criar gráfico de pizza para categorias interativo e avançado
            # Criar um treemap para visualização mais moderna e informativa
            categories_tree = px.treemap(
                categories_data,
                path=['category'],
                values='count',
                title="Distribuição de Categorias por Volume de Vídeos",
                color='count',
                color_continuous_scale='Blues',
                hover_data=['count']
            )
            
        categories_tree.update_traces(
                hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percentRoot:.1%}<extra></extra>',
                texttemplate='<b>%{label}</b><br>%{percentRoot:.1%}',
                textposition="middle center"
            )
            
        categories_tree.update_layout(
                margin=dict(t=30, b=0, l=0, r=0),
                height=350,
                coloraxis_showscale=False
            )
            
            # Definir a figura do treemap para retornar ao final da função
        categories_treemap_fig = categories_tree
            
            # Também criar um gráfico de pizza para ter visualizações complementares
        categories_pie = px.pie(
                categories_data, 
                values='count', 
                names='category', 
                title="Distribuição de Categorias",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
        categories_pie.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                hoverinfo='label+percent+value',
                marker=dict(line=dict(color='#FFFFFF', width=2))
            )
            
        categories_pie.update_layout(
                margin=dict(t=30, b=0, l=0, r=0),
                height=350,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
            )

            # Adicionar detalhes de categorias em uma tabela junto com o gráfico
        categories_card = dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(figure=categories_pie, config={'displayModeBar': False})
                        ], width=12, md=6),
                        dbc.Col([
                            dbc.Table([
                                html.Thead([
                                    html.Tr([
                                        html.Th("Categoria"), 
                                        html.Th("Contagem"),
                                        html.Th("%")
                                    ], className="table-success")
                                ]),
                                html.Tbody([
                                    html.Tr([
                                        html.Td(row['category']),
                                        html.Td(f"{row['count']:,}"),
                                        html.Td(f"{row['count'] / categories_data['count'].sum() * 100:.1f}%")
                                    ]) for _, row in categories_data.iterrows()
                                ])
                            ], bordered=True, hover=True, responsive=True, size="sm", striped=True)
                        ], width=12, md=6)
                    ])
                ])
            ], className="shadow-sm mb-4")
            
        stats_children.append(categories_card)
          # Removido o gráfico de publicações por dia da semana conforme solicitado
        
        # Combinar todos os elementos estatísticos
        stats_div = html.Div(stats_children) if stats_children else html.Div("Sem estatísticas disponíveis.")
          # Criar gráfico de relação entre comentários e likes
        comments_likes_fig = px.bar(title="Dados não disponíveis")
        try:
            if 'like_count' in youtube_videos_df.columns and 'comment_count' in youtube_videos_df.columns:
                # Adicionar proporção de likes para comentários
                youtube_videos_df['likes_per_comment'] = youtube_videos_df['like_count'] / youtube_videos_df['comment_count'].replace(0, 1)
                
                # Limitar dados para melhor visualização
                data_for_scatter = youtube_videos_df.dropna(subset=['like_count', 'comment_count'])
                
                # Criar gráfico de dispersão
                comments_likes_fig = px.scatter(
                    data_for_scatter,
                    x="like_count",
                    y="comment_count",
                    color="category_name" if "category_name" in youtube_videos_df.columns else None,
                    size="view_count" if "view_count" in youtube_videos_df.columns else None,
                    hover_name="title",
                    hover_data=["likes_per_comment", "channel_title"],
                    log_x=True,
                    log_y=True,
                    title="Relação Entre Comentários e Likes por Vídeo",
                    labels={
                        "like_count": "Likes (escala log)",
                        "comment_count": "Comentários (escala log)",
                        "category_name": "Categoria",
                        "view_count": "Visualizações",
                        "likes_per_comment": "Likes por Comentário"
                    },
                    trendline="ols",
                    trendline_scope="overall",
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                
                # Personalizar o hover
                comments_likes_fig.update_traces(
                    hovertemplate="<b>%{hovertext}</b><br><br>" +
                                 "Canal: %{customdata[1]}<br>" +
                                 "Likes: %{x:,.0f}<br>" +
                                 "Comentários: %{y:,.0f}<br>" +
                                 "Likes por comentário: %{customdata[0]:.1f}<br>" +
                                 "Visualizações: %{marker.size:,.0f}<extra></extra>"
                )
                
                # Melhorar layout
                comments_likes_fig.update_layout(
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    legend_title="Categoria de Vídeo",
                    plot_bgcolor='rgba(250,250,250,0.9)'
                )
        except Exception as e:
            print(f"Erro ao criar gráfico de comentários vs. likes: {str(e)}")
            comments_likes_fig = px.bar(title=f"Erro ao criar gráfico de relação: {str(e)}")
          # Removido o gráfico de desempenho dos canais por engajamento conforme solicitado
        # Removidas as tabelas de estatísticas detalhadas dos vídeos
          # Criando os novos gráficos de análise de categorias
        
        # 1. Gráfico de categorias com mais visualizações
        if 'category_name' in youtube_videos_df.columns:
            # Análise por categoria para visualizações
            views_by_category = youtube_videos_df.groupby('category_name').agg({
                'view_count': ['sum', 'mean', 'count']
            }).reset_index()
            
            # Formatando colunas
            views_by_category.columns = ['_'.join(col).strip('_') for col in views_by_category.columns.values]
            views_by_category = views_by_category.rename(columns={
                'category_name_': 'category_name',
                'view_count_count': 'video_count'
            })
            
            # Ordenar por total de visualizações
            views_by_category = views_by_category.sort_values('view_count_sum', ascending=True)
              # Criar gráfico de barras horizontais para visualizações totais - Mais limpo e organizado
            category_views_fig = px.bar(
                views_by_category.tail(10),  # Pegando os top 10
                y="category_name",
                x="view_count_sum",
                text="video_count",
                orientation="h",
                color="view_count_mean",
                color_continuous_scale=px.colors.sequential.Blues,
                title="Categorias com Maior Volume de Visualizações",
                labels={
                    "category_name": "Categoria",
                    "view_count_sum": "Total de Visualizações",
                    "video_count": "Número de Vídeos",
                    "view_count_mean": "Média de Visualizações"
                }
            )
            
            # Aprimorando o gráfico
            category_views_fig.update_traces(
                texttemplate='%{text} vídeos', 
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Total de visualizações: %{x:,.0f}<br>Média por vídeo: %{customdata[0]:,.0f}<br>Vídeos: %{text}'
            )
            
            # Melhorando formatação dos eixos e layout geral
            category_views_fig.update_layout(
                xaxis=dict(
                    title="Total de Visualizações",
                    tickformat=',d'
                ),
                yaxis=dict(
                    title="",
                    autorange="reversed"  # Inverte a ordem para ter a maior categoria no topo
                ),
                margin=dict(l=10, r=10, t=50, b=10),
                height=500,
                plot_bgcolor='rgba(240,240,240,0.2)',
                coloraxis_colorbar=dict(
                    title="Média de<br>Visualizações",
                    thickness=12
                ),
                title={
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )
        else:
            category_views_fig = px.bar(title="Dados de categorias não disponíveis")
            
        # 2. Gráfico de categorias com mais curtidas
        if 'category_name' in youtube_videos_df.columns and 'like_count' in youtube_videos_df.columns:
            # Análise por categoria para curtidas
            likes_by_category = youtube_videos_df.groupby('category_name').agg({
                'like_count': ['sum', 'mean', 'count'],
                'view_count': 'sum'
            }).reset_index()
            
            # Formatando colunas
            likes_by_category.columns = ['_'.join(col).strip('_') for col in likes_by_category.columns.values]
            likes_by_category = likes_by_category.rename(columns={
                'category_name_': 'category_name',
                'like_count_count': 'video_count'
            })
            
            # Calcular taxa de curtidas por visualização
            likes_by_category['like_view_ratio'] = likes_by_category['like_count_sum'] / likes_by_category['view_count_sum'].where(likes_by_category['view_count_sum'] > 0, 1)
            
            # Ordenar por total de curtidas
            likes_by_category = likes_by_category.sort_values('like_count_sum', ascending=True)
              # Criar gráfico de barras horizontais para curtidas totais - Redesenhado
            category_likes_fig = px.bar(
                likes_by_category.tail(10),  # Pegando os top 10
                y="category_name",
                x="like_count_sum",
                text="video_count",
                orientation="h",
                color="like_view_ratio",
                color_continuous_scale=px.colors.sequential.Reds,
                title="Categorias com Maior Volume de Curtidas",
                labels={
                    "category_name": "Categoria",
                    "like_count_sum": "Total de Curtidas",
                    "video_count": "Número de Vídeos",
                    "like_view_ratio": "Taxa Curtidas/Visualizações"
                }
            )
            
            # Aprimorando o gráfico
            category_likes_fig.update_traces(
                texttemplate='%{text} vídeos', 
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Total de curtidas: %{x:,.0f}<br>Média por vídeo: %{customdata[0]:,.0f}<br>Taxa curtidas/views: %{customdata[1]:.2%}<br>Vídeos: %{text}'
            )
            
            # Melhorando formatação dos eixos e layout geral
            category_likes_fig.update_layout(
                xaxis=dict(
                    title="Total de Curtidas",
                    tickformat=',d'
                ),
                yaxis=dict(
                    title="",
                    autorange="reversed"  # Inverte a ordem para ter a maior categoria no topo
                ),
                margin=dict(l=10, r=10, t=50, b=10),
                height=500,
                plot_bgcolor='rgba(255,240,240,0.2)',
                coloraxis_colorbar=dict(
                    title="Taxa de Curtidas<br>por Visualização",
                    thickness=12,
                    tickformat='.1%'
                ),
                title={
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )
        else:
            category_likes_fig = px.bar(title="Dados de curtidas não disponíveis")
            
        # 3. Gráfico de categorias com mais comentários
        if 'category_name' in youtube_videos_df.columns and 'comment_count' in youtube_videos_df.columns:
            # Análise por categoria para comentários
            comments_by_category = youtube_videos_df.groupby('category_name').agg({
                'comment_count': ['sum', 'mean', 'count'],
                'view_count': 'sum'
            }).reset_index()
            
            # Formatando colunas
            comments_by_category.columns = ['_'.join(col).strip('_') for col in comments_by_category.columns.values]
            comments_by_category = comments_by_category.rename(columns={
                'category_name_': 'category_name',
                'comment_count_count': 'video_count'
            })
            
            # Calcular taxa de comentários por visualização
            comments_by_category['comment_view_ratio'] = comments_by_category['comment_count_sum'] / comments_by_category['view_count_sum'].where(comments_by_category['view_count_sum'] > 0, 1)
            
            # Ordenar por total de comentários
            comments_by_category = comments_by_category.sort_values('comment_count_sum', ascending=True)
              # Criar gráfico de barras horizontais para comentários totais - Redesenhado
            category_comments_fig = px.bar(
                comments_by_category.tail(10),  # Pegando os top 10
                y="category_name",
                x="comment_count_sum",
                text="video_count",
                orientation="h",
                color="comment_view_ratio",
                color_continuous_scale=px.colors.sequential.Greens,
                title="Categorias com Maior Volume de Comentários",
                labels={
                    "category_name": "Categoria",
                    "comment_count_sum": "Total de Comentários",
                    "video_count": "Número de Vídeos",
                    "comment_view_ratio": "Taxa Comentários/Visualizações"
                }
            )
            
            # Aprimorando o gráfico
            category_comments_fig.update_traces(
                texttemplate='%{text} vídeos', 
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Total de comentários: %{x:,.0f}<br>Média por vídeo: %{customdata[0]:,.0f}<br>Taxa comentários/views: %{customdata[1]:.2%}<br>Vídeos: %{text}'
            )
            
            # Melhorando formatação dos eixos e layout geral
            category_comments_fig.update_layout(
                xaxis=dict(
                    title="Total de Comentários",
                    tickformat=',d'
                ),
                yaxis=dict(
                    title="",
                    autorange="reversed"  # Inverte a ordem para ter a maior categoria no topo
                ),
                margin=dict(l=10, r=10, t=50, b=10),
                height=500,
                plot_bgcolor='rgba(240,255,240,0.2)',
                coloraxis_colorbar=dict(
                    title="Taxa de Comentários<br>por Visualização",
                    thickness=12,
                    tickformat='.1%'
                ),
                title={
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            ) 


        else:
            category_comments_fig = px.bar(title="Dados de comentários não disponíveis")
        
        # Retornando todos os componentes necessários (com os novos gráficos)
        return category_fig, views_engagement_fig, comments_likes_fig, category_views_fig, category_likes_fig, category_comments_fig, True, "Análise do YouTube concluída com sucesso!"
    except Exception as e:
        print(f"Erro na análise do YouTube: {str(e)}")
        traceback.print_exc()
        
        # Criar figuras vazias com mensagem de erro mais amigável
        error_fig = px.bar(
            title="Não foi possível carregar os dados", 
            height=400
        )
        error_fig.update_layout(
            annotations=[dict(
                x=0.5, y=0.5, 
                xref="paper", yref="paper",
                text="Não foi possível processar os dados do YouTube.<br>Tente extrair os dados novamente.",
                showarrow=False,
                font=dict(size=16)
            )]
        )
        
        return error_fig, error_fig, error_fig, error_fig, error_fig, error_fig, True, f"Erro ao analisar dados do YouTube: {str(e)}"

# Callback para correlacionar dados
@app.callback(
    [
        Output("correlation-graph", "figure"),
        Output("correlation-stats", "children"),
        Output("viral-songs-table", "children"),
        Output("viral-genres-graph", "figure"),
        Output("viral-insights", "children"),
        Output("status-modal", "is_open", allow_duplicate=True),
        Output("modal-body", "children", allow_duplicate=True),
        Output("correlations-count", "children"),
        Output("correlation-data-store", "data"),
    ],
    [Input("correlate-button", "n_clicks")],
    [
        State("spotify-data-store", "data"),
        State("youtube-data-store", "data"),
        State("use-realtime-switch", "value"),  # Novo: obter o valor do switch para dados em tempo real
    ],
    prevent_initial_call=True,
)
def correlate_data(n_clicks, spotify_data, youtube_data, use_realtime=False):
    if not n_clicks or not spotify_data or not youtube_data:
        empty_fig = px.bar(title="Sem dados para exibir")
        return {}, html.Div("Sem dados para exibir."), html.Div("Sem dados para exibir."), empty_fig, html.Div("Sem dados para exibir."), False, "", "0", {}
    
    try:
        # Exibir modal de status enquanto processa
        modal_message = "Correlacionando dados do Spotify e YouTube..."
        if use_realtime:
            modal_message += " Buscando dados atualizados em tempo real (pode levar alguns segundos)."
        
        # Carregar dados do armazenamento usando StringIO
        from io import StringIO
        import json
        
        # Verificando o formato dos dados do Spotify
        if isinstance(spotify_data.get("tracks"), str):
            spotify_tracks_df = pd.read_json(StringIO(spotify_data["tracks"]), orient="split") if spotify_data.get("tracks") else None
        else:
            spotify_tracks_df = pd.DataFrame(spotify_data.get("tracks")) if spotify_data.get("tracks") else None
            
        # Verificando o formato dos dados do YouTube
        if isinstance(youtube_data.get("videos"), str):
            youtube_videos_df = pd.read_json(StringIO(youtube_data["videos"]), orient="split") if youtube_data.get("videos") else None
        else:
            youtube_videos_df = pd.DataFrame(youtube_data.get("videos")) if youtube_data.get("videos") else None
            
        # Verificar se temos dados para analisar
        if spotify_tracks_df is None and youtube_videos_df is None:
            return True, "Não há dados suficientes para gerar visualizações. Por favor, extraia os dados primeiro."
        
        # Atualizar os DataFrames no analisador
        if spotify_tracks_df is not None:
            analyzer.spotify_tracks_df = spotify_tracks_df
        if youtube_videos_df is not None:
            analyzer.youtube_videos_df = youtube_videos_df
        
        # Realizar análise de correlação, opcionalmente usando dados em tempo real
        correlations, correlation_df = analyzer.correlate_spotify_youtube(use_real_time_data=bool(use_realtime))
        
        if not correlations:
            empty_fig = px.bar(title="Sem correlações encontradas")
            return {}, html.Div("Sem correlações encontradas."), html.Div("Sem correlações encontradas."), empty_fig, html.Div("Sem insights disponíveis."), True, "Não foi possível correlacionar os dados.", "0", {}
        
        # Criar gráfico de correlação
        if correlation_df is not None and not correlation_df.empty:
            corr_fig = px.scatter(
                correlation_df,
                x="spotify_popularity",
                y="youtube_views",
                size="youtube_engagement",
                hover_name="youtube_title",
                text="spotify_artist",
                title="Spotify Popularidade vs. YouTube Visualizações",
                labels={
                    "spotify_popularity": "Popularidade no Spotify",
                    "youtube_views": "Visualizações no YouTube",
                    "youtube_engagement": "Engajamento no YouTube",
                    "spotify_artist": "Artista"
                },
                log_y=True
            )
            corr_fig.update_traces(textposition='top center')
        else:
            corr_fig = px.scatter(title="Sem correspondências encontradas")
          # Criar estatísticas de correlação
        stats_children = []
        
        # Adicionar bandeira se dados em tempo real foram usados
        if use_realtime:
            stats_children.append(
                dbc.Alert(
                    [
                        html.I(className="fas fa-sync me-2"),
                        html.Strong("Dados em tempo real utilizados: "),
                        "Os resultados abaixo incluem informações atualizadas buscadas diretamente das APIs."
                    ],
                    color="success",
                    className="mb-3"
                )
            )
        
        music_video_matches = correlations.get('music_video_matches', 0)
        stats_children.append(html.H6([
            html.I(className="fas fa-link me-2 text-primary"), 
            f"Correspondências encontradas: ",
            html.Badge(f"{music_video_matches}", color="primary", className="ms-1")
        ]))
        
        if 'popularity_vs_views_corr' in correlations:
            corr = correlations['popularity_vs_views_corr']
            stats_children.append(html.P([
                html.I(className="fas fa-chart-line me-2 text-info"),
                "Correlação entre popularidade no Spotify e visualizações no YouTube: ",
                html.Strong(f"{corr:.4f}")
            ]))
            
            # Interpretação
            interpretation = ""
            badge_color = "secondary"
            
            if abs(corr) < 0.2:
                interpretation = "Correlação muito fraca"
                badge_color = "light"
            elif abs(corr) < 0.4:
                interpretation = "Correlação fraca"
                badge_color = "secondary" 
            elif abs(corr) < 0.6:
                interpretation = "Correlação moderada"
                badge_color = "info"
            elif abs(corr) < 0.8:
                interpretation = "Correlação forte" 
                badge_color = "primary"
            else:
                interpretation = "Correlação muito forte"
                badge_color = "success"
            
            stats_children.append(html.P([
                "Interpretação: ",
                html.Badge(interpretation, color=badge_color, className="ms-1")
            ]))
            
            # Adicionar correlações de features de áudio se disponíveis
            if 'audio_features_correlations' in correlations:
                audio_corrs = correlations['audio_features_correlations']
                if audio_corrs:
                    stats_children.append(html.H6([
                        html.I(className="fas fa-music me-2 text-success"),
                        "Correlações de características de áudio:"
                    ], className="mt-4"))
                    
                    audio_items = []
                    for feature, value in audio_corrs.items():
                        if 'danceability' in feature:
                            icon = "fas fa-walking"
                            label = "Dançabilidade"
                        elif 'energy' in feature:
                            icon = "fas fa-bolt"
                            label = "Energia"
                        elif 'valence' in feature:
                            icon = "fas fa-smile"
                            label = "Valência"
                        else:
                            icon = "fas fa-music"
                            label = feature
                            
                        if 'views' in feature:
                            metric = "visualizações"
                        else:
                            metric = "engajamento"
                            
                        audio_items.append(html.Li([
                            html.I(className=f"{icon} me-2 text-info"),
                            f"{label} vs. {metric}: ",
                            html.Strong(f"{value:.4f}")
                        ]))
                    
                    stats_children.append(html.Ul(audio_items, className="ps-3"))
            
        
        # Se houver correspondências, mostrar algumas delas
        if correlation_df is not None and not correlation_df.empty:
            stats_children.append(html.H5("Exemplos de correspondências:"))
            matches_list = []
            for i, row in correlation_df.head(5).iterrows():
                matches_list.append(html.Li(f"{row['spotify_artist']} - {row['spotify_track_name']} (Spotify) → {row['youtube_title']} (YouTube)"))
            stats_children.append(html.Ul(matches_list))
        
        stats_div = html.Div(stats_children) if stats_children else html.Div("Sem estatísticas de correlação disponíveis.")
        
        # Converter DataFrame para JSON
        corr_data = {
            "correlation": correlation_df.to_json(date_format='iso', orient='split') if correlation_df is not None and not correlation_df.empty else None,
        }
        
        # Criar tabela com as músicas virais (definidas por alta popularidade no Spotify e alto engajamento no YouTube)
        viral_songs_table = html.Div("Sem dados suficientes para análise")
        viral_genres_fig = px.pie(title="Sem dados suficientes para análise")
        viral_insights_div = html.Div("Sem insights disponíveis")
        
        # Processar apenas se temos dados suficientes
        if correlation_df is not None and not correlation_df.empty and len(correlation_df) >= 5:
            # Calcular um "índice de viralização" baseado na popularidade do Spotify e visualizações/engajamento do YouTube
            correlation_df['viral_index'] = (
                (correlation_df['spotify_popularity'] / correlation_df['spotify_popularity'].max()) * 0.4 + 
                (correlation_df['youtube_views'] / correlation_df['youtube_views'].max()) * 0.4 +
                (correlation_df['youtube_engagement'] / correlation_df['youtube_engagement'].max()) * 0.2
            ) * 100
            
            # Identificar as músicas mais virais (top 10)
            top_viral = correlation_df.sort_values('viral_index', ascending=False).head(10)
            
            # Criar uma tabela estilizada com as músicas mais virais
            viral_table = dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("#", style={"width": "5%"}),
                        html.Th("Música", style={"width": "25%"}),
                        html.Th("Artista", style={"width": "20%"}),
                        html.Th("Índice Viral", style={"width": "15%"}),
                        html.Th("Spotify", style={"width": "15%"}),
                        html.Th("YouTube", style={"width": "20%"}),
                    ], className="table-dark")
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td(f"{i+1}", className="fw-bold"),
                        html.Td([
                            html.Strong(row['spotify_track_name'][:30]),
                            html.Br(),
                            html.Small(row['youtube_title'][:40] + "..." if len(row['youtube_title']) > 40 else row['youtube_title'])
                        ]),
                        html.Td(row['spotify_artist']),
                        html.Td([
                            html.Div(className="progress", style={"height": "20px"}, children=[
                                html.Div(
                                    className="progress-bar bg-success",
                                    style={"width": f"{row['viral_index']:.1f}%"},
                                    children=f"{row['viral_index']:.1f}"
                                )
                            ])
                        ]),
                        html.Td(f"Pop: {row['spotify_popularity']}", className="text-primary"),
                        html.Td([
                            f"Views: {row['youtube_views']:,.0f}",
                            html.Br(),
                            f"Eng: {row['youtube_engagement']:.3f}"
                        ], className="text-danger")
                    ]) for i, (_, row) in enumerate(top_viral.iterrows())
                ])
            ], bordered=True, hover=True, responsive=True, size="sm", striped=True, className="mt-3")
              # Adicionar título e descrição à tabela
            viral_songs_table = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.H5([html.I(className="fas fa-fire me-2 text-danger"), "Top 10 Músicas Virais"]),
                    ], width="auto"),
                    dbc.Col([
                        html.Span(
                            html.Badge("DADOS EM TEMPO REAL", color="success", className="ms-2") if use_realtime else "",
                            className="align-middle"
                        )
                    ])
                ]),
                html.P([
                    "Músicas com maior índice de viralização baseado na popularidade do Spotify e métricas do YouTube. ",
                    html.Small("Calculado usando um algoritmo que considera popularidade, visualizações, likes, comentários e engajamento.") if use_realtime else "",
                ]),
                viral_table
            ])
            
            # Criar gráfico de distribuição por gênero musical
            if 'spotify_genres' in correlation_df.columns:
                # Extrair e processar gêneros (que podem estar em uma string como lista)
                all_genres = []
                for genres_str in correlation_df['spotify_genres'].dropna():
                    try:
                        # Se estiver armazenado como string de lista
                        if isinstance(genres_str, str):
                            if genres_str.startswith('[') and genres_str.endswith(']'):
                                genres = eval(genres_str)  # Avaliar a string como lista
                                if isinstance(genres, list):
                                    all_genres.extend(genres)
                            else:
                                all_genres.append(genres_str)
                        # Se já for uma lista
                        elif isinstance(genres_str, list):
                            all_genres.extend(genres_str)
                    except:
                        continue
                
                # Contagem de gêneros
                genre_counts = pd.Series(all_genres).value_counts().reset_index()
                genre_counts.columns = ['genre', 'count']
                
                # Selecionar os 8 principais gêneros
                top_genres = genre_counts.head(8)
                
                # Criar gráfico de pizza para gêneros
                viral_genres_fig = px.pie(
                    top_genres,
                    values='count',
                    names='genre',
                    title="Distribuição de Gêneros Musicais nas Músicas Virais",
                    color_discrete_sequence=px.colors.qualitative.Bold,
                    hole=0.4
                )
                
                # Melhorar a aparência do gráfico
                viral_genres_fig.update_traces(
                    textinfo='percent+label',
                    textposition='inside'
                )
                
                viral_genres_fig.update_layout(
                    legend_title="Gêneros Musicais",
                    margin=dict(t=50, b=20, l=20, r=20)
                )
            else:
                viral_genres_fig = px.pie(title="Informações de gênero não disponíveis")
                
            # Criar análise e insights sobre as músicas virais
            avg_spotify_pop = correlation_df['spotify_popularity'].mean()
            avg_youtube_views = correlation_df['youtube_views'].mean()
            avg_engagement = correlation_df['youtube_engagement'].mean()
            
            # Calcular correlações adicionais
            corr_pop_engagement = correlation_df['spotify_popularity'].corr(correlation_df['youtube_engagement'])
            
            # Identificar artistas com múltiplas músicas virais
            artist_counts = correlation_df['spotify_artist'].value_counts().reset_index()
            artist_counts.columns = ['artist', 'count']
            top_viral_artists = artist_counts[artist_counts['count'] > 1].head(5)
            
            viral_insights_div = html.Div([
                html.H5([html.I(className="fas fa-lightbulb me-2 text-warning"), "Análise de Músicas Virais"]),
                
                dbc.Row([
                    dbc.Col([
                        html.H6("Métricas Principais:", className="mb-3"),
                        html.Ul([
                            html.Li([
                                "Popularidade média no Spotify: ",
                                html.Strong(f"{avg_spotify_pop:.1f}/100")
                            ]),
                            html.Li([
                                "Visualizações médias no YouTube: ",
                                html.Strong(f"{avg_youtube_views:,.0f}")
                            ]),
                            html.Li([
                                "Taxa média de engajamento: ",
                                html.Strong(f"{avg_engagement:.4f}")
                            ]),
                            html.Li([
                                "Correlação entre popularidade e engajamento: ",
                                html.Strong(f"{corr_pop_engagement:.4f}")
                            ])
                        ]),
                        
                        html.H6("Artistas com Múltiplos Hits:", className="mt-4 mb-3"),
                        html.Ol([
                            html.Li([html.Strong(f"{row['artist']} - {row['count']} músicas virais")]) 
                            for _, row in top_viral_artists.iterrows()
                        ]) if not top_viral_artists.empty else html.P("Nenhum artista com múltiplas músicas virais encontrado.")
                    ], width=12, md=6),
                    
                    dbc.Col([
                        html.H6("Insights e Observações:", className="mb-3"),
                        html.Ul([
                            html.Li("As músicas mais virais tendem a ter forte presença tanto no Spotify quanto no YouTube, indicando uma estratégia de marketing multicanal."),
                            html.Li("Músicas com alto índice viral frequentemente têm videoclipes de alta qualidade ou conceitos criativos."),
                            html.Li("A viralidade nem sempre está correlacionada com a qualidade musical, mas com fatores como trending topics, memes ou colaborações entre artistas."),
                            html.Li("As redes sociais e plataformas como TikTok têm grande influência na viralização, especialmente quando trechos da música se tornam tendência.")
                        ]),
                        
                        html.H6("Recomendações:", className="mt-4 mb-3"),
                        html.Ul([
                            html.Li("Analisar as características comuns entre as músicas virais para identificar padrões."),
                            html.Li("Considerar parcerias com artistas que demonstraram capacidade de viralização."),
                            html.Li("Investir em conteúdo visual de qualidade para YouTube, pois há forte correlação com o sucesso musical.")
                        ])
                    ], width=12, md=6)
                ])
            ])
        
        return corr_fig, stats_div, viral_songs_table, viral_genres_fig, viral_insights_div, True, "Análise de correlação concluída com sucesso!", str(music_video_matches), corr_data    
    except Exception as e:
        empty_fig = px.bar(title="Erro na análise")
        return {}, html.Div("Erro na correlação."), html.Div("Erro na análise."), empty_fig, html.Div("Erro na análise."), True, f"Erro ao correlacionar dados: {str(e)}", "0", {}

# Callback para pipeline completo
@app.callback(
    [
        Output("spotify-data-store", "data", allow_duplicate=True),
        Output("youtube-data-store", "data", allow_duplicate=True),
        Output("correlation-data-store", "data", allow_duplicate=True),
        Output("regional-data-store", "data", allow_duplicate=True),
        Output("status-modal", "is_open", allow_duplicate=True),
        Output("modal-body", "children", allow_duplicate=True),
    ],
    [Input("full-pipeline-button", "n_clicks")],
    prevent_initial_call=True,
)
def run_full_pipeline(n_clicks):
    if not n_clicks:
        return {}, {}, {}, {}, False, ""
    
    try:
        # Executar pipeline completo
        results = analyzer.run()
        
        if not results:
            return {}, {}, {}, {}, True, "Falha ao executar o pipeline completo."
        
        # Preparar dados para armazenamento
        spotify_data = {
            "tracks": analyzer.spotify_tracks_df.to_json(date_format='iso', orient='split') if analyzer.spotify_tracks_df is not None else None,
            "playlists": analyzer.spotify_playlists_df.to_json(date_format='iso', orient='split') if analyzer.spotify_playlists_df is not None else None,
            "artists": analyzer.spotify_artists_df.to_json(date_format='iso', orient='split') if analyzer.spotify_artists_df is not None else None,
        }
        
        youtube_data = {
            "videos": analyzer.youtube_videos_df.to_json(date_format='iso', orient='split') if analyzer.youtube_videos_df is not None else None,
            "categories": analyzer.youtube_categories_df.to_json(date_format='iso', orient='split') if analyzer.youtube_categories_df is not None else None,
        }
        
        correlation_data = {
            "correlation": analyzer.correlation_df.to_json(date_format='iso', orient='split') if analyzer.correlation_df is not None else None,
        }
        
        # Atualizar a interface com os novos dados
        return spotify_data, youtube_data, correlation_data, {}, True, "Pipeline completo executado com sucesso! Todos os dados foram atualizados."
    
    except Exception as e:
        return {}, {}, {}, {}, True, f"Erro ao executar o pipeline completo: {str(e)}"

# Callback para gerar visualizações
@app.callback(
    [
        Output("status-modal", "is_open", allow_duplicate=True),
        Output("modal-body", "children", allow_duplicate=True),
    ],
    [Input("generate-visualizations-button", "n_clicks")],
    [
        State("spotify-data-store", "data"),
        State("youtube-data-store", "data"),
        State("correlation-data-store", "data"),
    ],
    prevent_initial_call=True,
)
def generate_visualizations(n_clicks, spotify_data, youtube_data, correlation_data):
    if not n_clicks:
        return False, ""
    
    try:
        # Carregar dados do armazenamento usando StringIO
        from io import StringIO
        import json
        
        # Verificando o formato dos dados do Spotify
        if isinstance(spotify_data.get("tracks"), str):
            spotify_tracks_df = pd.read_json(StringIO(spotify_data["tracks"]), orient="split")
        else:
            spotify_tracks_df = pd.DataFrame(spotify_data.get("tracks"))
        
        if spotify_data and spotify_data.get("artists"):
            if isinstance(spotify_data.get("artists"), str):
                spotify_artists_df = pd.read_json(StringIO(spotify_data["artists"]), orient="split")
            else:
                spotify_artists_df = pd.DataFrame(spotify_data.get("artists"))
        else:
            spotify_artists_df = None
            
        # Verificando o formato dos dados do YouTube
        if isinstance(youtube_data.get("videos"), str):
            youtube_videos_df = pd.read_json(StringIO(youtube_data["videos"]), orient="split")
        else:
            youtube_videos_df = pd.DataFrame(youtube_data.get("videos"))
        
        # Verificando o formato dos dados de correlação
        if correlation_data and correlation_data.get("correlation"):
            if isinstance(correlation_data.get("correlation"), str):
                correlation_df = pd.read_json(StringIO(correlation_data["correlation"]), orient="split")
            else:
                correlation_df = pd.DataFrame(correlation_data.get("correlation"))
        else:
            correlation_df = None
        
        # Verificar se temos dados para analisar
        if spotify_tracks_df is None and youtube_videos_df is None:
            return True, "Não há dados suficientes para gerar visualizações. Por favor, extraia os dados primeiro."
        
        # Atualizar os DataFrames no analisador
        if spotify_tracks_df is not None:
            analyzer.spotify_tracks_df = spotify_tracks_df
        if spotify_artists_df is not None:
            analyzer.spotify_artists_df = spotify_artists_df
        if youtube_videos_df is not None:
            analyzer.youtube_videos_df = youtube_videos_df
        if correlation_df is not None:
            analyzer.correlation_df = correlation_df
        
        # Gerar visualizações
        analyzer.create_visualizations()
        
        return True, "Visualizações geradas com sucesso! Salvas na pasta 'visualizations'."
    
    except Exception as e:
        return True, f"Erro ao gerar visualizações: {str(e)}"

# Callback para abrir o modal de configuração da API
@app.callback(
    [
        Output("api-config-modal", "is_open"),
        Output("spotify-api-status", "children"),
        Output("youtube-api-status", "children"),
    ],
    [Input("api-config-button", "n_clicks"), Input("close-api-modal", "n_clicks")],
    [State("api-config-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_api_modal(n1, n2, is_open):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return False, [], []
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Fechar modal
    if button_id == "close-api-modal":
        return False, [], []
    
    # Verificar status das APIs
    spotify_configured = SPOTIFY_CLIENT_ID != "seu_client_id_spotify" and SPOTIFY_CLIENT_SECRET != "seu_client_secret_spotify"
    youtube_configured = YOUTUBE_API_KEY != "sua_api_key_youtube"
    
    # Criar mensagens de status
    spotify_status = []
    if spotify_configured:
        spotify_status = [
            dbc.Alert([
                html.I(className="fas fa-check-circle me-2"),
                "API configurada! Cliente ID: " + SPOTIFY_CLIENT_ID[:4] + "..." + SPOTIFY_CLIENT_ID[-4:] if len(SPOTIFY_CLIENT_ID) > 8 else SPOTIFY_CLIENT_ID
            ], color="success")
        ]
    else:
        spotify_status = [
            dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                "API não configurada. Dados em tempo real não estarão disponíveis para o Spotify."
            ], color="warning")
        ]
    
    youtube_status = []
    if youtube_configured:
        youtube_status = [
            dbc.Alert([
                html.I(className="fas fa-check-circle me-2"),
                "API configurada! Chave: " + YOUTUBE_API_KEY[:4] + "..." + YOUTUBE_API_KEY[-4:] if len(YOUTUBE_API_KEY) > 8 else YOUTUBE_API_KEY
            ], color="success")
        ]
    else:
        youtube_status = [
            dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                "API não configurada. Dados em tempo real não estarão disponíveis para o YouTube."
            ], color="warning")
        ]    
    return True, spotify_status, youtube_status

# Callback para os botões de seleção de região
@app.callback(
    [
        Output("selected-region-input", "value"),
        Output("btn-region-norte", "outline"),
        Output("btn-region-nordeste", "outline"),
        Output("btn-region-centro", "outline"),
        Output("btn-region-sudeste", "outline"),
        Output("btn-region-sul", "outline")
    ],
    [
        Input("btn-region-norte", "n_clicks"),
        Input("btn-region-nordeste", "n_clicks"),
        Input("btn-region-centro", "n_clicks"),
        Input("btn-region-sudeste", "n_clicks"),
        Input("btn-region-sul", "n_clicks"),
        Input("btn-reset-region", "n_clicks"),  # Adicionado botão de reset
    ],
    prevent_initial_call=True
)
def update_selected_region(norte_clicks, nordeste_clicks, centro_clicks, sudeste_clicks, sul_clicks, reset_clicks):
    # Identificar qual botão foi clicado
    button_id = ctx.triggered_id if ctx.triggered_id else None
    
    # Definir todos como outline=True inicialmente (não selecionados)
    outlines = [True, True, True, True, True]
    selected_region = ""
    
    # Botão de reset - limpar seleção
    if button_id == "btn-reset-region":
        # Todos os botões com outline=True (não selecionados)
        return "", True, True, True, True, True
    
    if button_id == "btn-region-norte":
        outlines[0] = False  # Desativar outline para botão Norte (destacá-lo)
        selected_region = "Norte"
    elif button_id == "btn-region-nordeste":
        outlines[1] = False
        selected_region = "Nordeste"
    elif button_id == "btn-region-centro":
        outlines[2] = False
        selected_region = "Centro-Oeste"
    elif button_id == "btn-region-sudeste":
        outlines[3] = False
        selected_region = "Sudeste"
    elif button_id == "btn-region-sul":
        outlines[4] = False
        selected_region = "Sul"
    
    # Retorna apenas o valor da região selecionada e o estado dos botões
    return selected_region, *outlines

# Callback para os botões de seleção de plataforma no mapa
@app.callback(
    [
        Output("brazil-platform-select", "value"),
        Output("btn-youtube", "outline"),
        Output("btn-spotify", "outline"),
    ],
    [
        Input("btn-youtube", "n_clicks"),
        Input("btn-spotify", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def update_platform_selection(youtube_clicks, spotify_clicks):
    # Identificar qual botão foi clicado
    button_id = ctx.triggered_id if ctx.triggered_id else None
    
    if button_id == "btn-youtube":
        return "youtube", False, True  # YouTube ativo (outline=False), Spotify inativo (outline=True)
    elif button_id == "btn-spotify":
        return "spotify", True, False  # YouTube inativo (outline=True), Spotify ativo (outline=False)
    
    # Estado padrão
    return "youtube", False, True

# Callback para o mapa do Brasil
@app.callback(
    [
        Output("brazil-choropleth-map", "figure"),
        Output("selected-region-title", "children"),
        Output("selected-region-info", "children"),
        Output("selected-region-stats", "children"),
        Output("brazil-choropleth-map", "clickData")  # Permite que o callback retorne e atualize o clickData
    ],
    [
        Input("brazil-platform-select", "value"),
        Input("brazil-choropleth-map", "clickData"),
        Input("selected-region-input", "value")  # Input do valor selecionado via botões
    ],
    prevent_initial_call=False,
)
def update_brazil_map(platform, click_data, selected_region_from_button):
    # Definição das coordenadas e polígonos das regiões do Brasil
    brazil_regions = {
        'Norte': {
            'name': 'Região Norte', 
            'lat': -3.0, 
            'lon': -60.0,
            'color': '#2ecc71',
            'states': ['AM', 'PA', 'AC', 'RO', 'RR', 'AP', 'TO'],
            'metric_name': 'Taxa de visualização' if platform == 'youtube' else 'Popularidade',
            'metric_value': 0.8 if platform == 'youtube' else 73,
            'category': 'Entertainment' if platform == 'youtube' else None,
            'genre': None if platform == 'youtube' else 'Tecno Melody'
        },
        'Nordeste': {
            'name': 'Região Nordeste', 
            'lat': -9.0, 
            'lon': -40.0,
            'color': '#3498db',
            'states': ['MA', 'PI', 'CE', 'RN', 'PB', 'PE', 'AL', 'SE', 'BA'],
            'metric_name': 'Taxa de visualização' if platform == 'youtube' else 'Popularidade',
            'metric_value': 1.1 if platform == 'youtube' else 75,
            'category': 'Music' if platform == 'youtube' else None,
            'genre': None if platform == 'youtube' else 'Forró'
        },
        'Centro-Oeste': {
            'name': 'Região Centro-Oeste', 
            'lat': -15.5, 
            'lon': -56.0,
            'color': '#f39c12',
            'states': ['MT', 'MS', 'GO', 'DF'],
            'metric_name': 'Taxa de visualização' if platform == 'youtube' else 'Popularidade',
            'metric_value': 0.9 if platform == 'youtube' else 72,
            'category': 'Howto & Style' if platform == 'youtube' else None,
            'genre': None if platform == 'youtube' else 'Sertanejo'
        },
        'Sudeste': {
            'name': 'Região Sudeste', 
            'lat': -21.0, 
            'lon': -45.0,
            'color': '#e74c3c',
            'states': ['MG', 'ES', 'RJ', 'SP'],
            'metric_name': 'Taxa de visualização' if platform == 'youtube' else 'Popularidade',
            'metric_value': 1.4 if platform == 'youtube' else 78,
            'category': 'Music' if platform == 'youtube' else None,
            'genre': None if platform == 'youtube' else 'Funk'
        },
        'Sul': {
            'name': 'Região Sul', 
            'lat': -27.0, 
            'lon': -52.0,
            'color': '#9b59b6',
            'states': ['PR', 'SC', 'RS'],
            'metric_name': 'Taxa de visualização' if platform == 'youtube' else 'Popularidade',
            'metric_value': 1.0 if platform == 'youtube' else 74,
            'category': 'Comedy' if platform == 'youtube' else None,
            'genre': None if platform == 'youtube' else 'Rock Gaúcho'
        }
    }

    # Obter os dados para análise de acordo com a plataforma selecionada
    regions_df = pd.DataFrame([
        {
            'region': region,
            'name': info['name'],
            'lat': info['lat'],
            'lon': info['lon'],
            'color': info['color'],
            'metric_value': info['metric_value'],
            'category': info['category'] if platform == 'youtube' else None,
            'genre': info['genre'] if platform == 'spotify' else None,
            'engagement': 0.055 if region == 'Norte' else 0.06 if region == 'Nordeste' else 0.045 if region == 'Centro-Oeste' else 0.042 if region == 'Sudeste' else 0.038
        }
        for region, info in brazil_regions.items()
    ])
      # Criar mapa base do Brasil com regiões clicáveis
    fig = px.scatter_mapbox(
        regions_df, 
        lat="lat", 
        lon="lon", 
        hover_name="name",
        hover_data={
            "metric_value": True,
            "lat": False,
            "lon": False,
            "color": False,
            "region": False
        },
        custom_data=["region"],  # Para identificar a região ao clicar
        size=[25] * len(regions_df),  # Aumentar o tamanho dos pontos para facilitar clique
        color="region",
        color_discrete_map={region: info['color'] for region, info in brazil_regions.items()},
        opacity=0.8,
        zoom=3,
        mapbox_style="carto-positron",
        title=f"Análise Regional do Brasil - {platform.capitalize()}"
    )
      # Adicionar contornos das regiões para melhorar a visualização e facilitar clique
    for region, info in brazil_regions.items():
        # Adicionar texto da região para facilitar identificação
        fig.add_trace(
            go.Scattermapbox(
                lat=[info['lat']],
                lon=[info['lon']],
                mode="text",
                text=[region],
                textfont=dict(color="black", size=14, family="Arial Black"),
                hoverinfo="skip",
                showlegend=False
            )
        )
        
        # Adicionar círculos transparentes grandes por trás para facilitar o clique
        fig.add_trace(
            go.Scattermapbox(
                lat=[info['lat']],
                lon=[info['lon']],
                mode="markers",
                marker=dict(
                    size=60,  # Círculo grande para facilitar o clique
                    color=info['color'],
                    opacity=0.3,
                ),
                name=info['name'],
                customdata=[[region]],  # Adicionando informação da região para captura no clique
                hoverinfo="text",
                hovertext=info['name'],
                showlegend=False
            )
        )
      # Melhorar layout do mapa
    fig.update_layout(
        mapbox=dict(
            center=dict(lat=-15, lon=-55),  # Centro do Brasil
            zoom=3.2,
            style="carto-positron",
            layers=[
                {
                    'source': {
                        'type': "FeatureCollection",
                        'features': [{
                            'type': "Feature",
                            'geometry': {
                                'type': "Polygon",
                                'coordinates': [[[-73, 5], [-35, 5], [-35, -33], [-73, -33], [-73, 5]]]  # Aproximadamente o Brasil
                            }
                        }]
                    },
                    'below': "traces",
                    'sourcetype': "geojson",
                    'opacity': 0.1,
                    'color': "#3B71CA",
                    'type': "fill"
                }
            ]
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        legend_title="Regiões do Brasil",
        title={
            'text': f"Análise Regional do Brasil - {platform.capitalize()}",
            'y': 0.97,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 16, 'color': '#1266F1'}
        },
        font=dict(size=12),
        height=580,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bordercolor="#e0e0e0",
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Arial"
        ),
        paper_bgcolor='white',
        modebar={'bgcolor': 'rgba(255,255,255,0.8)'}
    )    # Informações sobre a região selecionada (padrão se não houver seleção)
    selected_region = None
    title = "Selecione uma região no mapa"
    region_info = dbc.Alert([
        html.I(className="fas fa-info-circle me-2"),
        "Clique em uma região do Brasil no mapa para ver análises detalhadas."
    ], color="info")
    region_stats = html.Div()    # Verificar se há uma região selecionada pelo botão
    if selected_region_from_button and selected_region_from_button in brazil_regions:
        selected_region = selected_region_from_button
        print(f"Região selecionada pelo botão: {selected_region}")
        # Se temos uma região do botão mas não temos click_data, criar um
        if not click_data:
            # Criar dados simulados de clique para a região selecionada pelo botão
            coords = brazil_regions[selected_region]
            click_data = {
                "points": [{
                    "customdata": [selected_region],
                    "hovertext": brazil_regions[selected_region]['name'],
                    "lat": coords["lat"],
                    "lon": coords["lon"]
                }]
            }
    
    if click_data:
        try:
            # Se não temos região selecionada do botão, pegue do click_data
            if not selected_region:
                # Obter a região diretamente dos custom_data
                selected_region = click_data['points'][0]['customdata'][0]
            
            # Método alternativo caso o custom_data não funcione
            if not selected_region or selected_region not in brazil_regions:
                point_index = click_data['points'][0]['pointIndex']
                selected_region = regions_df.iloc[point_index]['region']
            
            # Verificação de segurança
            if selected_region not in brazil_regions:
                # Tentar obter pelo nome mostrado no hover
                hover_text = click_data['points'][0]['hovertext']
                for region, info in brazil_regions.items():
                    if info['name'] == hover_text:
                        selected_region = region
                        break
              # Verificar se temos uma região válida
            if not selected_region or selected_region not in brazil_regions:
                # Se ainda não temos região válida, usar Norte como fallback
                selected_region = "Norte"
                
            # Obter dados da região
            region_data = brazil_regions[selected_region]
            print(f"Região selecionada: {selected_region}")  # Para diagnóstico
        except Exception as e:
            print(f"Erro ao selecionar região: {str(e)}")
            # Fallback para região Norte se houver erro
            selected_region = "Norte"
            region_data = brazil_regions["Norte"]
        
        # Atualizar o título
        title = f"{region_data['name']} - Análise de {platform.capitalize()}"
          # Preparar informações específicas da plataforma com visualizações aprimoradas
        if platform == 'youtube':
            # Criar dados simulados para estatísticas detalhadas
            view_growth = 5 + (region_data['metric_value'] * 10)
            engagement_rate = regions_df[regions_df['region'] == selected_region]['engagement'].values[0]
            like_ratio = engagement_rate * 0.8
            comment_ratio = engagement_rate * 0.2
            
            # Calcular valores para visualizações no sparkline
            base_views = 1000 * region_data['metric_value']
            views_trend = [base_views * (1 + (i * 0.1) + np.random.uniform(-0.05, 0.05)) for i in range(7)]
            
            platform_metrics = [
                html.Div([
                    html.H5([
                        html.I(className="fab fa-youtube me-2 text-danger"), 
                        "Análise de Vídeos"
                    ], className="mb-3")
                ]),
                
                # Cards com métricas principais
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Categoria Principal", className="card-subtitle text-muted"),
                                html.H5([
                                    html.I(className="fas fa-video me-2"), 
                                    region_data['category']
                                ], className="mt-2"),
                                html.Div([
                                    html.Span(f"{30 + np.random.randint(-10, 10)}%", className="text-success fw-bold"), 
                                    " dos vídeos"
                                ], className="small")
                            ])
                        ], className="text-center h-100 shadow-sm")
                    ], width=6, className="mb-3"),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Crescimento de Views", className="card-subtitle text-muted"),
                                html.H5([
                                    html.I(className="fas fa-chart-line me-2"), 
                                    f"{view_growth:.1f}%"
                                ], className="mt-2"),
                                html.Div([
                                    html.Span("últimos 30 dias", className="text-muted")
                                ], className="small")
                            ])
                        ], className="text-center h-100 shadow-sm")
                    ], width=6, className="mb-3"),
                ]),
                
                # Gráfico de engajamento 
                dbc.Card([
                    dbc.CardHeader("Métricas de Engajamento"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                # Taxa de curtidas
                                html.Div([
                                    html.Div([
                                        html.I(className="fas fa-thumbs-up me-1"),
                                        "Taxa de Curtidas"
                                    ], className="mb-1"),
                                    html.Div(className="progress", style={"height": "15px"}, children=[
                                        html.Div(
                                            className="progress-bar bg-success",
                                            style={"width": f"{like_ratio * 100:.1f}%"},
                                            children=f"{like_ratio:.1%}"
                                        )
                                    ])
                                ])
                            ], width=12, className="mb-3"),
                            dbc.Col([
                                # Taxa de comentários
                                html.Div([
                                    html.Div([
                                        html.I(className="fas fa-comment me-1"),
                                        "Taxa de Comentários"
                                    ], className="mb-1"),
                                    html.Div(className="progress", style={"height": "15px"}, children=[
                                        html.Div(
                                            className="progress-bar bg-info",
                                            style={"width": f"{comment_ratio * 100:.1f}%"},
                                            children=f"{comment_ratio:.1%}"
                                        )
                                    ])
                                ])
                            ], width=12),
                        ]),
                        
                        # Mini gráfico de tendência de visualizações
                        html.Div([
                            html.H6("Tendência de visualizações (últimos 7 dias)", className="text-center mt-4 mb-2 small"),
                            dcc.Graph(
                                figure=px.line(
                                    x=list(range(7)), 
                                    y=views_trend,
                                    markers=True
                                ).update_layout(
                                    height=100,
                                    margin=dict(l=5, r=5, t=5, b=5),
                                    showlegend=False,
                                    xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                                    yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                                    plot_bgcolor='white'
                                ),
                                config={"displayModeBar": False}
                            )
                        ])
                    ])
                ], className="mt-3")
            ]
        else:  # spotify
            # Criar dados simulados para estatísticas detalhadas
            danceability = 0.6 + (0.05 * (regions_df[regions_df['region'] == selected_region]['engagement'].values[0] * 10))
            energy = 0.65 + (0.02 * (regions_df[regions_df['region'] == selected_region]['engagement'].values[0] * 10))
            valence = 0.55 + (0.04 * (regions_df[regions_df['region'] == selected_region]['engagement'].values[0] * 10))
            
            # Dados para o radar chart
            audio_features = ['Dançabilidade', 'Energia', 'Valência', 'Acústica', 'Instrumentalidade']
            audio_values = [danceability, energy, valence, 0.4 + np.random.uniform(-0.1, 0.1), 0.2 + np.random.uniform(-0.1, 0.1)]
            
            # Criar radar chart
            radar_fig = go.Figure()
            radar_fig.add_trace(go.Scatterpolar(
                r=audio_values,
                theta=audio_features,
                fill='toself',
                fillcolor=f'rgba{tuple(int(region_data["color"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (0.5,)}',
                line=dict(color=region_data["color"])
            ))
            
            radar_fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                margin=dict(l=30, r=30, t=20, b=30),
                height=250,
                showlegend=False,
            )
            
            platform_metrics = [
                html.Div([
                    html.H5([
                        html.I(className="fab fa-spotify me-2 text-success"), 
                        "Análise de Músicas"
                    ], className="mb-3")
                ]),
                
                # Cards com métricas principais
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Gênero Principal", className="card-subtitle text-muted"),
                                html.H5([
                                    html.I(className="fas fa-music me-2"), 
                                    region_data['genre']
                                ], className="mt-2"),
                                html.Div([
                                    html.Span(f"{30 + np.random.randint(-5, 10)}%", className="text-success fw-bold"), 
                                    " das faixas"
                                ], className="small")
                            ])
                        ], className="text-center h-100 shadow-sm")
                    ], width=6, className="mb-3"),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Popularidade", className="card-subtitle text-muted"),
                                html.H5([
                                    html.I(className="fas fa-star me-2"), 
                                    f"{region_data['metric_value']}/100"
                                ], className="mt-2"),
                                html.Div([
                                    html.Span(f"{'Alta' if region_data['metric_value'] > 75 else 'Média' if region_data['metric_value'] > 70 else 'Baixa'}", 
                                             className=f"{'text-success' if region_data['metric_value'] > 75 else 'text-warning' if region_data['metric_value'] > 70 else 'text-danger'} fw-bold"),
                                ], className="small")
                            ])
                        ], className="text-center h-100 shadow-sm")
                    ], width=6, className="mb-3"),
                ]),
                
                # Gráfico radar de características de áudio
                dbc.Card([
                    dbc.CardHeader("Características de Áudio"),
                    dbc.CardBody([
                        dcc.Graph(figure=radar_fig, config={"displayModeBar": False}),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.Span("Dançabilidade: ", className="fw-bold"),
                                    f"{danceability:.2f}"
                                ], className="small"),
                                html.Div([
                                    html.Span("Energia: ", className="fw-bold"),
                                    f"{energy:.2f}"
                                ], className="small")
                            ], width=6),
                            dbc.Col([
                                html.Div([
                                    html.Span("Valência: ", className="fw-bold"),
                                    f"{valence:.2f}"
                                ], className="small"),
                                html.Div([
                                    html.Span("Acústica: ", className="fw-bold"),
                                    f"{audio_values[3]:.2f}"
                                ], className="small")
                            ], width=6),
                        ])
                    ])
                ], className="mt-3")
            ]
          # Montar informações consolidadas da região com design aprimorado
        # Criar um donut chart para visualização da métrica principal
        metric_fig = go.Figure(go.Pie(
            values=[region_data['metric_value'], max(5 - region_data['metric_value'], 0) if platform == 'youtube' else 100 - region_data['metric_value']],
            hole=0.7,
            marker_colors=[region_data['color'], 'lightgrey'],
            showlegend=False,
            textinfo='none'
        ))
        
        # Adicionar texto no centro do donut chart
        metric_fig.add_annotation(
            text=f"{region_data['metric_value']}{'' if platform == 'youtube' else '%'}",
            font=dict(size=24, color='black'),
            showarrow=False
        )
        
        metric_fig.update_layout(
            height=200,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        # Montar informações da região
        region_info = html.Div([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-map-marker-alt me-2 text-danger"), 
                    html.Span(f"{region_data['name']}", style={"color": region_data['color'], "font-weight": "bold"})
                ], className="d-flex align-items-center"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H5([
                                html.I(className="fas fa-chart-pie me-2 text-primary"), 
                                f"{region_data['metric_name']}"
                            ], className="text-center mb-2"),
                            dcc.Graph(figure=metric_fig, config={"displayModeBar": False})
                        ], width=12, lg=5),
                        dbc.Col([
                            html.H5([
                                html.I(className=f"fas {'fa-play-circle' if platform == 'youtube' else 'fa-music'} me-2 text-success"), 
                                f"{'Top Categoria' if platform == 'youtube' else 'Top Gênero'}"
                            ], className="text-center mb-3"),
                            html.Div([
                                html.Div(
                                    html.Span(
                                        f"{region_data['category'] if platform == 'youtube' else region_data['genre']}",
                                        className="badge rounded-pill bg-primary py-2 px-3 fs-6"
                                    ),
                                    className="text-center"
                                ),
                                html.P(
                                    f"{'Vídeos' if platform == 'youtube' else 'Faixas'} desta {'categoria' if platform == 'youtube' else 'gênero'} são muito populares na região.",
                                    className="text-center mt-2 text-muted small"
                                )
                            ])
                        ], width=12, lg=7, className="mt-3 mt-lg-0"),
                    ]),
                    
                    # Informações específicas da plataforma
                    html.Hr(),
                    html.Div(platform_metrics, className="mt-3")
                ])
            ], className="mb-3 shadow-sm"),
        ])        # Adicionar estatísticas comparativas aprimoradas
        # Criar dataframe para comparação, destacando a região selecionada
        compare_df = regions_df.copy()
        compare_df['is_selected'] = compare_df['region'] == selected_region
        
        # Criar figura de comparação mais elaborada com a ordem das regiões fixada
        # para manter consistência visual e facilitar comparação
        region_order = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
        compare_df['region_order'] = compare_df['region'].map({region: i for i, region in enumerate(region_order)})
        compare_df = compare_df.sort_values('region_order')
        
        compare_fig = px.bar(
            compare_df,
            x="region",
            y="metric_value",
            color="is_selected",
            color_discrete_map={True: region_data['color'], False: "lightgrey"},
            labels={"metric_value": region_data['metric_name'], "region": "Região"},
            title=f"Comparação de {region_data['metric_name']} entre Regiões",
            hover_data=["name"],
            category_orders={"region": region_order}
        )
        
        # Melhorar layout da figura
        compare_fig.update_layout(
            height=250,
            showlegend=False,
            plot_bgcolor='rgba(240,240,240,0.2)',
            title={
                'font': {'size': 15},
                'x': 0.5,
                'xanchor': 'center'
            },
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        # Adicionar segunda comparação - Engajamento
        engage_df = compare_df.copy()
        engage_fig = px.bar(
            engage_df,
            x="region",
            y="engagement",
            color="is_selected",
            color_discrete_map={True: region_data['color'], False: "lightgrey"},
            labels={"engagement": "Taxa de Engajamento", "region": "Região"},
            title="Comparação de Engajamento entre Regiões",
            hover_data=["name"]
        )
        
        # Configurar o formato do eixo Y como percentual
        engage_fig.update_yaxes(tickformat=".1%")
        
        # Melhorar layout da figura
        engage_fig.update_layout(
            height=250,
            showlegend=False,
            plot_bgcolor='rgba(240,240,240,0.2)',
            title={
                'font': {'size': 15},
                'x': 0.5,
                'xanchor': 'center'
            },
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        # Componentes de estatísticas
        region_stats = html.Div([
            html.H5([
                html.I(className="fas fa-chart-bar me-2"), 
                "Comparação com outras regiões"
            ], className="mt-3 mb-3"),
            dbc.Tabs([
                dbc.Tab(
                    dcc.Graph(figure=compare_fig, config={"displayModeBar": False}),
                    label=region_data['metric_name'],
                    tab_id="metric-tab",
                    label_style={"color": "#0275d8"}
                ),
                dbc.Tab(
                    dcc.Graph(figure=engage_fig, config={"displayModeBar": False}),
                    label="Engajamento",
                    tab_id="engagement-tab",
                    label_style={"color": "#5cb85c"}
                ),
            ], id="compare-tabs", className="mb-3"),
            
            # Adicionar insights sobre a região
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-lightbulb me-2 text-warning"),
                    "Insights da Região"
                ]),
                dbc.CardBody([
                    html.P([
                        f"A {region_data['name']} se destaca por ",
                        html.Strong(f"{'alta' if region_data['metric_value'] > 1.0 else 'média' if region_data['metric_value'] >= 0.9 else 'baixa'} taxa de visualização") if platform == 'youtube' else
                        html.Strong(f"{'alta' if region_data['metric_value'] > 75 else 'média' if region_data['metric_value'] >= 72 else 'baixa'} popularidade"),
                        " e ",
                        html.Strong(f"{'alto' if float(regions_df[regions_df['region'] == selected_region]['engagement'].values[0]) > 0.05 else 'médio' if float(regions_df[regions_df['region'] == selected_region]['engagement'].values[0]) >= 0.04 else 'baixo'} engajamento"),
                        "."
                    ]),
                    html.P([
                        f"O {'conteúdo' if platform == 'youtube' else 'gênero musical'} mais popular na região é ",
                        html.Strong(f"{region_data['category'] if platform == 'youtube' else region_data['genre']}"),
                        "."
                    ])
                ])
            ])
        ])
    
    # Se tivermos uma região selecionada pelo botão, mas não pelo clique, criar um clickData simulado
    if selected_region_from_button and not click_data and selected_region:
        # Criar dados simulados de clique para a região selecionada
        coords = brazil_regions[selected_region]
        click_data = {
            "points": [{
                "customdata": [selected_region],
                "lat": coords["lat"],
                "lon": coords["lon"]
            }]
        }
    
    return fig, title, region_info, region_stats, click_data

# Executar o servidor
if __name__ == "__main__":
    print("Iniciando servidor do Dashboard...")
    app.run(debug=True, port=8050)
