# 1_🏠_Accueil_et_Connexion.py
import streamlit as st
from shared_code import *
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Accueil - Marlodj Dashboard",
    page_icon="🏠",
    layout="wide"
)






load_and_display_css()

# Initialisation de l'état de session
if 'logged_in' not in st.session_state:
    st.cache_data.clear()
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_profile = None
    st.session_state.df_RH=None
    st.session_state.all_agencies=None
    st.session_state.all_reseau =None

def initialize_session_state():
    """Initialise tous les états nécessaires après une connexion réussie."""
    st.cache_data.clear()
    conn = get_connection()
    all_agencies_df = run_query(conn, SQLQueries().All_Region_Agences)
    
    # Initialiser les filtres
    st.session_state.start_date = datetime.now().date()
    st.session_state.end_date = datetime.now().date()
    st.session_state.selected_agencies = list(all_agencies_df['NomAgence'].unique())
    st.session_state.offline_agencies_in_scope = []
    # Initialiser les conteneurs de données et la clé de "cache manuel"
    st.session_state.df_main = pd.DataFrame()
    st.session_state.last_filter_key = None # Pour forcer le premier chargement


def show_login_page():
    st.title("Connexion au Dashboard Marlodj")
    conn = get_connection()
    df_users = run_query(conn, SQLQueries().ProfilQueries)
    users_dict = dict(zip(df_users['UserName'], df_users['MotDePasse']))
    profiles_dict = dict(zip(df_users['UserName'], df_users['Profil']))

    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")

        if submitted:
            if users_dict.get(username) == password:
                #st.stop()
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.user_profile = profiles_dict.get(username)
                initialize_session_state()
                st.rerun()
                
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")

# Main logic

def show_agent_dashboard():
    """Dashboard spécifique pour les profils 'Caissier' ou 'Clientele'."""
    st.sidebar.title(f"Bienvenue, {st.session_state.username}")
    st.sidebar.header(f"Votre Dashboard - Profil : {st.session_state.user_profile}")
    
    df_queue=st.session_state.df.copy()
    username=st.session_state.username
    df_all_service=df_queue.query('UserName==@username')

    if df_all_service.empty:
        st.warning(f"L'agent {username} n'a de données pour la période sélectionnée.")
        st.stop()
    else:
        service=df_all_service["NomService"].iloc[0]
        df_queue_service=df_queue.query('NomService==@service')
        option_agent(df_all_service,df_queue_service)
    if st.sidebar.button("Se déconnecter"):
        st.session_state.logged_in = False
        st.rerun()

# ==============================================================================
# VUE POUR LE PROFIL ADMIN / SUPERVISEUR (CORRIGÉE)
# ==============================================================================
def show_admin_dashboard():
    """Prépare l'environnement pour les admins et affiche la page d'accueil."""
    
   

    # Affichage de la page d'accueil pour l'admin
    st.title(f"🏠 Bienvenue, {st.session_state.username}!")
    st.info("Utilisez le menu sur la gauche pour naviguer entre les différentes sections d'analyse.")
    
# ==============================================================================
# FONCTION DE DECONNEXION
# ==============================================================================
def logout():
    """Vide la session et force un rerun pour retourner à la page de login."""
    for key in st.session_state.keys():
        del st.session_state[key]

# ==============================================================================
# ROUTEUR PRINCIPAL (CORRIGÉ ET ROBUSTE)
# ==============================================================================
if not st.session_state.logged_in:
    show_login_page()
else:
    load_and_display_css()
    
    if st.session_state.user_profile in ['Caissier', 'Clientele']:
        # Si agent, on exécute sa vue et c'est tout. Pas de navigation multi-pages.
        show_agent_dashboard()
    else:
        # Si admin, on prépare l'environnement multi-pages.
        show_admin_dashboard()