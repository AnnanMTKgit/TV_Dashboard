# pages/6_🧑‍💼_Performance_Agent.py
import streamlit as st
from shared_code import *

# Mettre le minuteur en place dès le début de la page
setup_auto_refresh(interval_minutes=10)



# -----------------------------------------------

st.markdown("<h1 style='text-align: center;'>Performance des Agents</h1>", unsafe_allow_html=True)

st.markdown(""" <style>iframe[title="streamlit_echarts.st_echarts"]{ height: 600px !important } """, unsafe_allow_html=True)
load_and_display_css()

if not st.session_state.get('logged_in'):
    st.error("Veuillez vous connecter pour accéder à cette page.")
    st.stop()

create_sidebar_filters()

# Utiliser les données partagées au lieu de recharger
df = st.session_state.df_main
df_all = df[df['UserName'].notna()].reset_index(drop=True)
df_queue = df.copy()

df_filtered_global = df_all[df_all['NomAgence'].isin(st.session_state.selected_agencies)]
df_filtered_global = df_filtered_global[df_filtered_global['UserName'].notna()]


if df_filtered_global.empty: 
    st.error("Aucune donnée disponible pour la sélection.")
    st.stop()



# --- DataFrame final pour les visualisations ---
df_selection = filter1(df_filtered_global)

if df_selection.empty:
    st.warning("Aucune donnée pour cette sélection de services et d'agents.")
    st.stop()
    
#st.divider()

# --- 1. Configuration des onglets et de l'état de session ---
AGENT_TABS = ["Performance en Volume", "Performance en Temps", "Evolution en Temps par Agent", "Vue par Catégorie"]

if 'active_agent_tab_index' not in st.session_state:
    st.session_state.active_agent_tab_index = 0
if 'current_stacked_agent' not in st.session_state: # État pour le carrousel de l'onglet 4
    st.session_state.current_stacked_agent = 0

# --- 2. Préparation des figures pour chaque onglet ---
# Onglet 1
pie_option1 = create_pie_chart2(df_selection, title='Traitée')
pie_option2 = create_pie_chart2(df_selection, title='Passée')
pie_option3 = create_pie_chart2(df_selection, title='Rejetée')
# Onglet 2
bar_option1 = create_bar_chart2(df_selection, status='Traitée')
bar_option2 = create_bar_chart2(df_selection, status='Passée', color=green_color)
bar_option3 = create_bar_chart2(df_selection, status='Rejetée', color=blue_clair_color)
# Onglet 3
line_chart_tab3 = plot_line_chart(df_selection)
# Onglet 4 (Carrousel)
figures_tab4 = [
    stacked_chart2(df_selection, 'TempOperation', 'UserName', titre="Total des opérations par Agent et par Catégorie"),
    stacked_agent2(df_selection, concern='UserName', type='Type_Operation', titre="Top 10 des opérations effectuées par Agent")
]
total_figures_tab4 = len(figures_tab4)

# --- 3. Affichage du menu de navigation ---
selected_tab = option_menu(
    menu_title=None,
    options=AGENT_TABS,
    icons=['pie-chart-fill', 'bar-chart-fill', 'graph-up', 'grid-fill'],
    orientation="horizontal",
    default_index=st.session_state.active_agent_tab_index,
    styles={
        "container": {"padding": "0!important", "background-color": "white", "border-bottom": "1px solid #333"},
        "icon": {"color": "black", "font-size": "18px"},
        "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "color": "black"},
        "nav-link-selected": {"background-color": "#013447", "color": "white", "border-bottom": "3px solid #013447"},
    }
)

# --- 4. Affichage du contenu de l'onglet sélectionné ---
if selected_tab == AGENT_TABS[0]:
    c1, c2, c3 = st.columns(3)
    with c1:
        st_echarts(options=pie_option1, height="600px", key='pie_1')
    with c2:
        st_echarts(options=pie_option2, height="600px", key="pie_2")
    with c3:
        st_echarts(options=pie_option3, height="600px", key="pie_3")

elif selected_tab == AGENT_TABS[1]:
    c1, c2, c3 = st.columns(3)
    with c1:
        st_echarts(options=bar_option1, height="600px", key="bar_1")
    with c2:
        st_echarts(options=bar_option2, height="600px", key="bar_2")
    with c3:
        st_echarts(options=bar_option3, height="600px", key="bar_3")

elif selected_tab == AGENT_TABS[2]:
    st.plotly_chart(line_chart_tab3, use_container_width=True)

elif selected_tab == AGENT_TABS[3]:
    stacked_agent_index = st.session_state.current_stacked_agent
    st_echarts(options=figures_tab4[stacked_agent_index], height="600px", key=f"area_{stacked_agent_index}")

    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        if st.button("◀️ Précédent", use_container_width=True, disabled=(stacked_agent_index == 0), key="stacked_agent_prev"):
            st.session_state.current_stacked_agent -= 1
            st.rerun()
    with col2:
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>Figure {stacked_agent_index + 1} / {total_figures_tab4}</p>", unsafe_allow_html=True)
    with col3:
        if st.button("Suivant ▶️", use_container_width=True, disabled=(stacked_agent_index >= total_figures_tab4 - 1), key='stacked_agent_next'):
            st.session_state.current_stacked_agent += 1
            st.rerun()