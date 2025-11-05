import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# --- Moteur de recommandation (copié de l'exemple 1) ---

# Créer un jeu de données simple
data = {'title': ['Film A', 'Film B', 'Film C', 'Film D', 'Film E'],
        'description': ['action aventure super-héros',
                        'aventure fantastique magie',
                        'thriller suspense action',
                        'comédie romantique amour',
                        'drame historique biographie'],
        'note_moyenne': [8.5, 8.2, 7.9, 7.1, 8.8]}
df = pd.DataFrame(data)

# Créer une matrice TF-IDF
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['description'])

# Calculer la matrice de similarité cosinus
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Correspondance entre les titres et les indices
indices = pd.Series(df.index, index=df['title']).drop_duplicates()

def get_content_recommendations(title, cosine_sim=cosine_sim):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:4]
    movie_indices = [i[0] for i in sim_scores]
    return df.iloc[movie_indices]

# --- Interface du Dashboard ---

st.title("Dashboard de Recommandation de Films")

st.header("Exploration des Données")
st.write("Aperçu de notre catalogue de films :")
st.dataframe(df)

st.sidebar.title("Paramètres de Recommandation")
st.sidebar.write("Choisissez un film pour obtenir des recommandations.")

# Créer une liste d'options de films pour le menu déroulant
movie_list = df['title'].tolist()
selected_movie = st.sidebar.selectbox("Sélectionnez un film que vous avez aimé", movie_list)

if st.sidebar.button("Obtenir des Recommandations"):
    st.header(f"Recommandations pour '{selected_movie}'")

    try:
        recommendations = get_content_recommendations(selected_movie)
        
        # Afficher les recommandations sous forme de cartes
        cols = st.columns(len(recommendations))
        for i, (index, row) in enumerate(recommendations.iterrows()):
            with cols[i]:
                st.subheader(row['title'])
                st.write(f"**Description:** {row['description']}")
                st.write(f"**Note:** {row['note_moyenne']}/10")

    except Exception as e:
        st.error(f"Une erreur est survenue: {e}")