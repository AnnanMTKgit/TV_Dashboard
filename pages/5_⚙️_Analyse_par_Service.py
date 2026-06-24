# pages/5_⚙️_Analyse_par_Service.py
import streamlit as st
from shared_code import *

# Mettre le minuteur en place dès le début de la page
setup_auto_refresh(interval_minutes=10)


st.markdown("<h1 style='text-align: center;'>Analyse par Service et Type d'Opération</h1>", unsafe_allow_html=True)

st.markdown(""" <style>iframe[title="streamlit_echarts.st_echarts"]{ height: 500px !important } """, unsafe_allow_html=True)
load_and_display_css()

if not st.session_state.get('logged_in'):
    st.error("Veuillez vous connecter pour accéder à cette page.")
    st.stop()
create_sidebar_filters()

# Utiliser les données partagées au lieu de recharger
df = st.session_state.df_main
df_all = df[df['UserName'].notna()].reset_index(drop=True)
df_queue = df.copy()

df_all_filtered = df_all[df_all['NomAgence'].isin(st.session_state.selected_agencies)]
df_queue_filtered = df_queue[df_queue['NomAgence'].isin(st.session_state.selected_agencies)]

if df_all_filtered.empty: 
    st.error("Aucune donnée disponible pour la sélection.")
    st.stop()
# --- 1. Configuration des onglets et de l'état de session ---
# Noms des onglets pour une gestion plus facile
SERVICE_TABS = [
    "Temps de traitement moyen par type de service",
    "Types de transactions les plus courantes",
    "Top 10 Types de transactions en nombre de clients"
]

# Initialisation des états pour contrôler les onglets et le carrousel
if 'active_service_tab_index' not in st.session_state:
    st.session_state.active_service_tab_index = 0
if 'carousel_tab3_index' not in st.session_state: # État pour le carrousel de l'onglet 3
    st.session_state.carousel_tab3_index = 0

# --- 2. Préparation des figures pour chaque onglet ---
# Pré-générer les figures permet à la logique finale de connaître leur nombre.
option_tab1 = GraphsGlob2(df_all_filtered, "Temps Moyen d'opération par Service")
option_tab2 = Top10_Type(df_queue_filtered, title="Top10 des Opérations le plus courantes")
figures_tab3 = analyse_activity(df_queue_filtered, type='Type_Operation', concern='NomService')
total_figures_tab3 = len(figures_tab3)

# --- 3. Affichage du menu de navigation ---
selected_tab = option_menu(
    menu_title=None,
    options=SERVICE_TABS,
    icons=['hourglass-split', 'list-task', 'people'],
    orientation="horizontal",
    default_index=st.session_state.active_service_tab_index,
    styles={
        "container": {"padding": "0!important", "background-color": "white", "border-bottom": "1px solid #333"},
        "icon": {"color": "black", "font-size": "18px"},
        "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "color": "black"},
        "nav-link-selected": {"background-color": "#013447", "color": "white", "border-bottom": "3px solid #013447"},
    }
)

# --- 4. Affichage du contenu de l'onglet sélectionné ---
if selected_tab == SERVICE_TABS[0]:
    st_echarts(option_tab1, height="600px", key="fig_temps_op")

elif selected_tab == SERVICE_TABS[1]:
    st_echarts(option_tab2, height="600px", key='fig_top10')

elif selected_tab == SERVICE_TABS[2]:
    current_index = st.session_state.carousel_tab3_index
    
    st.markdown("<h1 style='text-align: center;font-size:1em;'>Analyse détaillée par Service</h1>", unsafe_allow_html=True)
    st_echarts(options=figures_tab3[current_index], height="500px", key=f"carousel_chart_{current_index}")
    
    # Navigation manuelle (conservée de votre code original)
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        if st.button("◀️ Précédent", use_container_width=True, disabled=(current_index == 0), key="carousel_prev"):
            st.session_state.carousel_tab3_index -= 1
            st.rerun()
    with col2:
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>Service {current_index + 1} / {total_figures_tab3}</p>", unsafe_allow_html=True)
    with col3:
        if st.button("Suivant ▶️", use_container_width=True, disabled=(current_index >= total_figures_tab3 - 1), key='carousel_next'):
            st.session_state.carousel_tab3_index += 1
            st.rerun()

