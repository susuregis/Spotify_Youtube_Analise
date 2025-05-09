# Spotify & YouTube Data Analysis

Este projeto realiza análises avançadas de dados do Spotify e YouTube, encontrando correlações entre tendências musicais e vídeos populares, analisando engajamento regional e criando visualizações interativas.

## Funcionalidades

1. **Análise de Playlists e Faixas Populares no Spotify**
   - Extração de dados de playlists e faixas salvas
   - Análise de artistas, gêneros, popularidade e duração
   - Visualização de características de áudio das músicas

2. **Tendências de Vídeos Populares no YouTube**
   - Extração de dados de vídeos em alta
   - Análise de categorias, visualizações, likes, comentários e engajamento
   - Visualização de métricas por categorias

3. **Correlação entre Música e Vídeos Populares**
   - Identificação de músicas que aparecem em vídeos populares
   - Análise de correlação entre popularidade no Spotify e métricas do YouTube
   - Visualização das correlações encontradas

4. **Análise de Engajamento por Região**
   - Análise de dados por localização geográfica
   - Identificação de preferências regionais
   - Comparação de métricas de engajamento entre regiões

5. **Visualização Interativa**
   - Dashboards interativos com Plotly e Dash
   - Filtros por tempo, gênero, região e engajamento
   - Gráficos estáticos e interativos

## Requisitos

- Python 3.6+
- Bibliotecas:
  - spotipy
  - google-api-python-client
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - plotly
  - dash (opcional, para visualizações interativas)
  - dash-bootstrap-components (opcional)

## Instalação

1. Clone o repositório:
```
git clone https://github.com/seu-usuario/spotify-youtube-analysis.git
cd spotify-youtube-analysis
```

2. Instale as dependências:
```
pip install spotipy google-api-python-client pandas numpy matplotlib seaborn plotly dash dash-bootstrap-components
```

3. Configure suas credenciais:
   - Crie uma aplicação no [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Obtenha uma chave de API do [Google Cloud Console](https://console.cloud.google.com/) (YouTube Data API v3)
   - Substitua as credenciais no arquivo `spotify_youtube_analysis.py`

## Uso

### Interface Visual (Recomendada)

1. Execute o dashboard interativo completo diretamente:
```
python dashboard.py
```

2. Através do dashboard, você pode:
   - Extrair dados do Spotify (faixas, playlists, artistas)
   - Extrair dados do YouTube (vídeos populares, categorias)
   - Analisar tendências do Spotify (artistas, gêneros, popularidade)
   - Analisar tendências do YouTube (visualizações, engajamento por categoria)
   - Encontrar correlações entre música e vídeos
   - Analisar dados regionais (comparação entre países)
   - Gerar visualizações interativas
   - **Novo:** Acessar dados em tempo real das APIs do Spotify e YouTube

### Configuração das APIs para Dados em Tempo Real

Para utilizar a nova funcionalidade de dados em tempo real:

1. Configure suas credenciais no arquivo `spotify_youtube_analysis.py`:
   - Para o Spotify, registre um aplicativo em [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Para o YouTube, crie uma chave de API na [Google Cloud Console](https://console.cloud.google.com/) (YouTube Data API v3)

2. No dashboard, na aba "Correlações", ative o switch "Usar dados em tempo real" antes de correlacionar os dados.

3. Para verificar se suas APIs estão configuradas corretamente, clique no botão "Configuração de APIs" no painel de controle.



### Modo Demonstração

1. Execute o script de demonstração para uma introdução rápida:
```
python index.py
```

2. Escolha uma das opções disponíveis:
   - Iniciar o dashboard interativo
   - Executar pipeline de análise completo
   - Sair

O dashboard interativo permite:
   - Extrair dados do Spotify e YouTube
   - Analisar playlists e faixas populares do Spotify
   - Analisar tendências de vídeos no YouTube
   - Correlacionar dados entre plataformas
   - Analisar engajamento por região 
   - Gerar visualizações
   - Executar pipeline completo de análise

## Estrutura do Projeto

- `spotify_youtube_analysis.py`: Classe principal com toda a lógica de análise
- `dashboard.py`: Interface web interativa completa usando Dash (recomendada)
- `index.py`: Ponto de entrada da aplicação e exemplo básico de uso das APIs
- `run_analysis.py`: Interface de linha de comando para análises (legado)
- `visualizations/`: Pasta onde as visualizações são salvas

## Notas Importantes

- As APIs do Spotify e YouTube têm limites de requisições. O código está otimizado para minimizar o número de chamadas.
- O primeiro uso requer autenticação no Spotify, que abrirá uma janela do navegador.
- Algumas visualizações interativas requerem conexão com a internet para carregar bibliotecas externas.
