from flask import Flask, render_template
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)

# Exemplo de dados
data = pd.read_csv("Recomendacoes/campanhas.csv")  # Use barra invertida dupla ou barra normal

# Dados dos usuários
user_data = {
    'user_id': [1, 2],
    'favorites': [[458, 602], [900, 186]],
    'localizacao': ['PE', 'SE']
}

# Convertendo para DataFrame
df_campaigns = data[["id_campanha", "campanha", "estado", "Categoria", "Palavra_Chave", "Visualizacoes", "imagem"]]
df_users = pd.DataFrame(user_data)

# Vetorização das palavras-chave
vectorizer = TfidfVectorizer()
keywords_matrix = vectorizer.fit_transform(df_campaigns['Palavra_Chave'])

# Similaridade entre campanhas com base nas palavras-chave
campaign_similarity = cosine_similarity(keywords_matrix)

# Normalização do número de visualizações e avaliações
df_campaigns['views_normalized'] = df_campaigns['Visualizacoes'] / df_campaigns['Visualizacoes'].max()

# Similaridade entre usuários e campanhas com base nas campanhas favoritas
def favorite_similarity(user_favorites, id_campanha):
    return 1 if id_campanha in user_favorites else 0

def categoria_favorite(campanha_categoria, favorite_campanhas):
    return 1 if campanha_categoria in favorite_campanhas else 0

# Função para recomendar campanhas
def recommend_campaigns(user_id, df_users, df_campaigns, campaign_similarity):
    user_favorites = df_users[df_users['user_id'] == user_id]['favorites'].values[0]
    localizacao = df_users[df_users['user_id'] == user_id]['localizacao'].values[0]
    df_campaigns['favorite_similarity'] = df_campaigns['id_campanha'].apply(lambda x: favorite_similarity(user_favorites, x))
    users_favorite_campaigns = df_campaigns[df_campaigns['id_campanha'].isin(user_favorites)]['Categoria']
    df_campaigns['favorite_categoria'] = df_campaigns['Categoria'].apply(lambda x: categoria_favorite(x, users_favorite_campaigns.tolist()))
    
    # Palavras-chave das campanhas favoritas do usuário
    favorite_campaigns = df_campaigns[df_campaigns['id_campanha'].isin(user_favorites)]
    favorite_keywords_matrix = vectorizer.transform(favorite_campaigns['Palavra_Chave'])
    
    # Similaridade entre campanhas favoritas e todas as campanhas
    Similaridade_favorita = cosine_similarity(favorite_keywords_matrix, keywords_matrix)
    
    # Média das similaridades para cada campanha
    df_campaigns['similarity_score'] = Similaridade_favorita.mean(axis=0)

    # Calculando a pontuação final
    df_campaigns['score'] = (df_campaigns['similarity_score'] + df_campaigns['favorite_categoria'] + df_campaigns['views_normalized'] + df_campaigns['favorite_similarity']) / 4
    filtered_campaigns = df_campaigns[df_campaigns['estado'] == localizacao]
    # Ordenando as campanhas pela pontuação
    recommendations = filtered_campaigns.sort_values(by='score', ascending=False)
    return recommendations[['id_campanha', 'campanha', 'estado', 'Categoria','Visualizacoes', 'score','imagem']]

@app.route('/')
def home():
    recommendations = recommend_campaigns(1, df_users, df_campaigns, campaign_similarity)
    # Convertendo o DataFrame para uma lista de dicionários
    recommendations_dict = recommendations.to_dict(orient='records')
    return render_template('index.html', recommendations=recommendations_dict)

if __name__ == '__main__':
    app.run(debug=True)
