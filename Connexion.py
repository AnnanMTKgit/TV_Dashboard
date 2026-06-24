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
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_profile = None
    st.session_state.df_RH=None
    st.session_state.all_agencies=None
    

def initialize_filters():
    conn = get_connection()
    all_agencies_df = run_query(conn, SQLQueries().AllAgences)
    st.session_state.start_date = datetime.now().date()
    st.session_state.end_date = datetime.now().date()





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
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.user_profile = profiles_dict.get(username)
                initialize_filters()
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

# Logique principale
if not st.session_state.logged_in:
    show_login_page()
else:

    
                
    if st.session_state.user_profile in ['Caissier', 'Clientele']:
        # Masquer la navigation multi-page pour les agents
        create_sidebar_filters()
        st.set_page_config(page_title=f"Dashboard Agent - {st.session_state.username}")
        show_agent_dashboard()
    else:
        
        #st.sidebar.info(f"{st.session_state.username}")
        st.title(f"Bienvenue sur le Dashboard Marlodj, {st.session_state.username}!")
        st.info("Utilisez le menu sur la gauche pour naviguer entre les différentes sections d'analyse.")