# Spotify & YouTube Analyzer - Guia Rápido

## Como Usar o Dashboard

### 1. Extração de Dados

O primeiro passo é extrair os dados das plataformas:

- Clique no botão **Extrair Dados do Spotify** para obter suas faixas salvas, playlists e informações de artistas
- Clique no botão **Extrair Dados do YouTube** para obter os vídeos mais populares (inicialmente do Brasil)

### 2. Análise do Spotify

Após extrair os dados do Spotify:

- Clique em **Analisar Spotify** para gerar visualizações e estatísticas
- Veja os resultados na aba "Spotify Trends"
  - Top artistas por contagem de faixas
  - Distribuição de características de áudio
  - Estatísticas gerais (popularidade, gêneros, etc.)

### 3. Análise do YouTube

Após extrair os dados do YouTube:

- Clique em **Analisar YouTube** para gerar visualizações e estatísticas
- Veja os resultados na aba "YouTube Trends"
  - Engajamento por categoria de vídeo
  - Relação entre visualizações e engajamento
  - Estatísticas gerais (médias, categorias principais)

### 4. Correlações

Com dados de ambas as plataformas:

- Clique em **Correlacionar Dados** para encontrar correspondências entre músicas e vídeos
-  Ative o switch "Usar dados em tempo real" para obter dados frescos das APIs
- Veja os resultados na aba "Correlações"
  - Gráfico de relação entre popularidade no Spotify e visualizações no YouTube
  - Força da correlação com interpretação
  - Lista de correspondências encontradas
  - Análise de músicas virais com índice de viralização
  - Distribuição de gêneros musicais nas músicas virais

#### 4.1 Dados em Tempo Real 

Para utilizar a funcionalidade de dados em tempo real:

- Clique em **Configuração de APIs** no painel de controle para verificar o status da conexão
- Configure suas credenciais de API no arquivo `spotify_youtube_analysis.py` se necessário
- Quando o switch "Usar dados em tempo real" estiver ativado na aba de correlações, o sistema buscará dados atualizados diretamente das APIs para as músicas correspondentes
- Os dados em tempo real proporcionam uma análise mais precisa e atual

### 5. Análise Regional

Para comparar dados entre diferentes países:

- Digite os códigos de região (ex: BR,US,GB,JP,IN) no campo apropriado
- Clique em **Analisar** para comparar o engajamento regional
- Veja os resultados na aba "Análise Regional"
  - Métricas de engajamento por região
  - Categorias populares por região

### 6. Visualizações

- Clique em **Gerar Visualizações** para salvar todos os gráficos na pasta 'visualizations'

### 7. Pipeline Completo

- O botão **Pipeline Completo** automatiza todos os passos anteriores em sequência

## Dicas

- Os dados são salvos apenas temporariamente durante a sessão atual
- Para analisar diversos países, digite os códigos separados por vírgulas
- Os códigos de região devem seguir o padrão ISO de 2 letras (BR, US, GB, etc.)
- Sempre extraia os dados antes de tentar analisá-los

## Solução de Problemas

- Se uma análise falhar, verifique se os dados foram corretamente extraídos
- Se não conseguir visualizar os gráficos, tente recarregar a página
