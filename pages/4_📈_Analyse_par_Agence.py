# pages/4_📈_Analyse_par_Agence.py
import streamlit as st
from shared_code import *

# Mettre le minuteur en place dès le début de la page
setup_auto_refresh(interval_minutes=10)



st.markdown("<h1 style='text-align: center;font-size:1.3em;'>Analyse Détaillée par Agence</h1>", unsafe_allow_html=True)
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


# --- CONFIGURATION ET ÉTAT DE SESSION (SIMPLIFIÉ) ---
TABS = ["Performance par Catégorie", "Agences les Plus Lentes", "Agences les Plus Fréquentées"]
TIME_PER_STEP = 5

if 'active_tab_index' not in st.session_state:
    st.session_state.active_tab_index = 0
if 'tab1_vertical_section_index' not in st.session_state:
    st.session_state.tab1_vertical_section_index = 0
if 'current_area' not in st.session_state:
    st.session_state.current_area = 0

# --- COMPOSANT JAVASCRIPT FIABLE (INCHANGÉ) ---
def scroll_to_anchor(anchor_id):
    js_code = f"""
    <script>
    (function() {{
        function attemptScroll() {{
            const element = parent.document.getElementById('{anchor_id}');
            if (element) {{
                element.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                clearInterval(scrollInterval);
            }}
        }}
        const scrollInterval = setInterval(attemptScroll, 100);
        setTimeout(() => clearInterval(scrollInterval), 5000);
    }})();
    </script>
    """
    html(js_code, height=0)

# --- PRÉPARATION DES FIGURES (INCHANGÉ) ---
figures_tab1 = [
    stacked_chart2(df_all_filtered, 'TempsAttenteReel', 'NomAgence', "Catégorisation du Temps d'Attente"),
    stacked_chart2(df_all_filtered, 'TempOperation', 'NomAgence', "Catégorisation du Temps d'Opération")
]
ANCHORS_TAB1 = ["chart_top", "chart_bottom"]
figures_tab2 = [
    area_graph2(df_all_filtered, concern='NomAgence', time='TempsAttenteReel', date_to_bin='Date_Appel', seuil=15, title="Top 5 Agences Lentes"),
    area_graph2(df_all_filtered, concern='NomAgence', time='TempOperation', date_to_bin='Date_Fin', seuil=5, title="Top 5 Agences Lentes")
]
total_figures_tab2 = len(figures_tab2)

# --- **SOLUTION AU PROBLÈME N°2** : ANCRE MAÎTRESSE EN HAUT DE PAGE ---
st.markdown('<div id="page_top_anchor"></div>', unsafe_allow_html=True)

# --- AFFICHAGE DU MENU (INCHANGÉ) ---
selected_tab = option_menu(
    menu_title=None, options=TABS, icons=['bar-chart-line', 'speedometer2', 'people-fill'],
    orientation="horizontal", default_index=st.session_state.active_tab_index,
    styles={
        "container": {"padding": "0!important", "background-color": "white", "border-bottom": "1px solid #333"},
        "icon": {"color": "black", "font-size": "18px"},
        "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "color": "black"},
        "nav-link-selected": {"background-color": "#013447", "color": "white", "border-bottom": "3px solid #013447"},
    }
)

# --- AFFICHAGE DU CONTENU DES ONGLETS (INCHANGÉ) ---
if selected_tab == TABS[0]:
    
    st.markdown(f'<div id="{ANCHORS_TAB1[0]}"></div>', unsafe_allow_html=True)
    st_echarts(options=figures_tab1[0], height="700px", key="stack_0")
    st.markdown(f'<div id="{ANCHORS_TAB1[1]}"></div>', unsafe_allow_html=True)
    st_echarts(options=figures_tab1[1], height="700px", key="stack_1")
elif selected_tab == TABS[1]:
    
    area_index = st.session_state.current_area
    st_echarts(options=figures_tab2[area_index], height="600px", key=f"area_{area_index}")
    st.markdown(f"<p style='text-align: center; font-weight: bold;'>Figure {area_index + 1} / {total_figures_tab2}</p>", unsafe_allow_html=True)
elif selected_tab == TABS[2]:
    
    c1, c2 = st.columns(2)
    
    with c1:
        # On appelle la nouvelle fonction pour obtenir les options du premier graphique
        options1 = top_agence_freq_echarts(
            df_all, 
            df_queue, 
            title=['Total Tickets', 'Total Traités'],
            color=[green_color, blue_clair_color] # Assurez-vous que ces variables de couleur sont définies
        )
        # On affiche le graphique avec st_echarts
        st_echarts(options=options1, height="500px", key="freq_1")
        
    with c2:
        # On appelle la nouvelle fonction pour obtenir les options du second graphique
        options2 = top_agence_freq_echarts(
            df_all, 
            df_queue, 
            title=['Total Tickets', 'Total Rejetées'],
            color=[green_color, blue_color] # Assurez-vous que ces variables de couleur sont définies
        )
        # On affiche le graphique avec st_echarts
        st_echarts(options=options2, height="500px", key="freq_2")

# --- **LOGIQUE DE DÉFILEMENT FINALE, CORRIGÉE ET FIABILISÉE** ---
# current_tab_index = st.session_state.active_tab_index

# if current_tab_index == 0:
#     v_index = st.session_state.tab1_vertical_section_index
#     total_v_sections = len(ANCHORS_TAB1)

#     # **Phase 1 : Défilement à travers les sections de contenu**
#     # Si l'index est dans la plage des ancres (0, 1, ...), on défile vers la section correspondante.
#     if v_index < total_v_sections:
#         scroll_to_anchor(ANCHORS_TAB1[v_index])
#         st.session_state.tab1_vertical_section_index += 1

#     # **Phase 2 : Étape visible de retour en haut**
#     # Si l'index est égal au nombre de sections, c'est notre étape dédiée au retour en haut.
#     elif v_index == total_v_sections:
#         scroll_to_anchor("page_top_anchor")
#         st.session_state.tab1_vertical_section_index += 1

#     # **Phase 3 : Transition vers l'onglet suivant**
#     # Si l'index a dépassé toutes les étapes précédentes, on change d'onglet.
#     else:
#         st.session_state.tab1_vertical_section_index = 0  # On réinitialise pour la prochaine fois
#         st.session_state.active_tab_index = 1           # On passe à l'onglet suivant

# elif current_tab_index == 1:
#     st.session_state.current_area += 1
#     if st.session_state.current_area >= total_figures_tab2:
#         st.session_state.current_area = 0
#         st.session_state.active_tab_index = 2

# elif current_tab_index == 2:
#     st.session_state.active_tab_index = 0

# # Pause et rafraîchissement global
# time.sleep(TIME_PER_STEP)
# st.rerun()