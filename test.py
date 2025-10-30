# tv_dashboard_final_working_scroll.py
import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime, timedelta
# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="TV Dashboard Demo", layout="wide", page_icon="📺")

# --- 1. CSS ET FONCTION DE DÉFILEMENT (CORRIGÉE) ---

def inject_css(view_mode):
    """Injecte le CSS approprié en fonction du mode d'affichage."""
    if view_mode == 'dashboard':
        st.markdown("""
            <style>
                /* Cache la barre de défilement principale du navigateur */
                body, html {
                    overflow: hidden !important;
                }
                /* Cible le conteneur principal pour le transformer en zone de défilement */
                [data-testid="stAppViewContainer"] > .main {
                    padding: 0;
                    margin: 0;
                    height: 100vh;
                    overflow-y: scroll;
                    scroll-behavior: smooth;
                }
                /* Chaque section est un conteneur qui sera notre point de référence */
                .main .block-container {
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    padding: 2rem 4rem;
                }
                /* Positionne le bouton d'arrêt en haut à droite */
                .stop-button-container {
                    position: fixed;
                    top: 1rem;
                    right: 1rem;
                    z-index: 9999;
                }
            </style>
        """, unsafe_allow_html=True)

def scroll_to_anchor(anchor_id):
    """
    Injecte le JS qui trouve le bon conteneur et le fait défiler.
    """
    js_code = f"""
    <script>
    (function() {{
        function attemptScroll() {{
            // 1. Trouver le conteneur qui a la barre de défilement
            const scrollContainer = parent.document.querySelector('[data-testid="stAppViewContainer"] > .main');
            
            // 2. Trouver l'élément cible (notre ancre)
            const targetElement = parent.document.getElementById('{anchor_id}');

            if (scrollContainer && targetElement) {{
                // 3. Faire défiler le CONTENEUR jusqu'à l'élément
                scrollContainer.scrollTo({{
                    top: targetElement.offsetTop,
                    behavior: 'smooth'
                }});
                clearInterval(scrollInterval); // Arrêter la vérification
            }}
        }}

        // Essayer toutes les 100ms car Streamlit peut être lent à rendre les éléments
        const scrollInterval = setInterval(attemptScroll, 100);
        // Sécurité pour arrêter après 5 secondes si l'élément n'est jamais trouvé
        setTimeout(() => clearInterval(scrollInterval), 5000);
    }})();
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 2. DÉFINITION DES SECTIONS ---
SECTIONS = {
    "kpis": {"title": "Indicateurs Clés de Performance"},
    "chart_1": {"title": "Analyse des Ventes par Région"},
    "chart_2": {"title": "Performance des Agences"},
    "data_table": {"title": "Données Détaillées"},
    "fin_de_cycle": {"title": "Fin du Cycle"},
}

# --- 3. GÉNÉRATION DE DONNÉES FICTIVES (pour l'exemple) ---
@st.cache_data
def generate_fake_data():
    agences = ['Agence Yoff', 'Agence Plateau', 'Agence Mbour', 'Agence Thies', 'Agence St-Louis']
    regions = ['Dakar', 'Dakar', 'Thies', 'Thies', 'St-Louis']
    data = []
    for agence, region in zip(agences, regions):
        data.append({
            "Nom Agence": agence, "Région": region,
            "Temps Moyen Opération (MIN)": random.randint(5, 25),
            "Temps Moyen Attente (MIN)": random.randint(10, 45),
            "Total Clients": random.randint(800, 2000), "Ventes": random.randint(10000, 50000),
        })
    return pd.DataFrame(data)

# --- 4. FONCTIONS DE RENDU POUR CHAQUE SECTION ---
# NOTE IMPORTANTE : Chaque fonction commence maintenant par st.markdown('<div id="..."></div>')
def render_kpis_section(df):
    st.markdown('<div id="kpis"></div>', unsafe_allow_html=True)
    st.header(SECTIONS["kpis"]['title'])
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Temps Moyen Opération", f"{df['Temps Moyen Opération (MIN)'].mean():.0f} min")
    kpi2.metric("Temps Moyen Attente", f"{df['Temps Moyen Attente (MIN)'].mean():.0f} min")
    kpi3.metric("Total Clients", f"{df['Total Clients'].sum():,}")

def render_chart_1_section(df):
    st.markdown('<div id="chart_1"></div>', unsafe_allow_html=True)
    st.header(SECTIONS["chart_1"]['title'])
    ventes_par_region = df.groupby('Région')['Ventes'].sum().reset_index()
    st.bar_chart(ventes_par_region, x='Région', y='Ventes', height=500)

def render_chart_2_section(df):
    st.markdown('<div id="chart_2"></div>', unsafe_allow_html=True)
    st.header(SECTIONS["chart_2"]['title'])
    st.bar_chart(df, x='Nom Agence', y=['Temps Moyen Opération (MIN)', 'Temps Moyen Attente (MIN)'], height=500)

def render_data_table_section(df):
    st.markdown('<div id="data_table"></div>', unsafe_allow_html=True)
    st.header(SECTIONS["data_table"]['title'])
    st.dataframe(df, height=500, use_container_width=True)

def render_end_section(df):
    st.markdown('<div id="fin_de_cycle"></div>', unsafe_allow_html=True)
    st.header(SECTIONS["fin_de_cycle"]['title'])
    st.success("Le défilement va redémarrer depuis le début...")

# --- 5. LOGIQUE PRINCIPALE DE L'APPLICATION ---
# Initialisation de l'état de session
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'view_mode' not in st.session_state: st.session_state.view_mode = 'config'
if 'scroll_duration' not in st.session_state: st.session_state.scroll_duration = 10
if 'section_config' not in st.session_state:
    st.session_state.section_config = {sec_id: True for sec_id in SECTIONS}
if 'current_section_index' not in st.session_state: st.session_state.current_section_index = 0

# --- PAGE DE CONNEXION ---
def show_login_page():
    inject_css('config')
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title("Connexion au Dashboard")
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur (admin)")
            password = st.text_input("Mot de passe (admin)", type="password")
            if st.form_submit_button("Se connecter", use_container_width=True, type="primary"):
                if username == "admin" and password == "admin":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")

# --- PAGE DE CONFIGURATION ---
def render_configuration_page():
    inject_css('config')
    st.title("Configuration du Dashboard TV")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.header("Étape 1 : Période et Durée")
        today = datetime.now().date()
        st.session_state.start_date = st.date_input("Date de début", today - timedelta(days=7))
        st.session_state.end_date = st.date_input("Date de fin", today)
        st.session_state.scroll_duration = st.number_input("Durée de visualisation par section (s)", min_value=3, value=st.session_state.scroll_duration)

    with col2:
        st.header("Étape 2 : Sections à Afficher")
        with st.container(height=400):
            for sec_id, details in SECTIONS.items():
                st.session_state.section_config[sec_id] = st.checkbox(
                    details['title'],
                    value=st.session_state.section_config.get(sec_id, True),
                    key=f"check_{sec_id}"
                )
    st.divider()
    if st.button("▶️ Lancer le Dashboard en Mode TV", use_container_width=True, type="primary"):
        st.session_state.view_mode = 'dashboard'
        st.session_state.current_section_index = 0
        st.rerun()

def render_scrolling_dashboard():
    inject_css('dashboard')

    st.markdown('<div class="stop-button-container">', unsafe_allow_html=True)
    if st.button("⏹️ Arrêter et Reconfigurer"):
        st.session_state.view_mode = 'config'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    df = generate_fake_data()
    render_functions = {
        "kpis": render_kpis_section, "chart_1": render_chart_1_section,
        "chart_2": render_chart_2_section, "data_table": render_data_table_section,
        "fin_de_cycle": render_end_section,
    }

    enabled_anchors = [sec_id for sec_id, enabled in st.session_state.section_config.items() if enabled]
    if not enabled_anchors:
        st.warning("Aucune section activée."); time.sleep(3)
        st.session_state.view_mode = 'config'; st.rerun()

    # Rendre toutes les sections activées
    for anchor in enabled_anchors:
        with st.container():
            render_functions[anchor](df)

    # Logique de défilement
    current_anchor_id = enabled_anchors[st.session_state.current_section_index]
    scroll_to_anchor(current_anchor_id)
    time.sleep(st.session_state.scroll_duration)
    st.session_state.current_section_index = (st.session_state.current_section_index + 1) % len(enabled_anchors)
    st.rerun()

# --- ROUTEUR PRINCIPAL ---
if not st.session_state.logged_in:
    show_login_page()
elif st.session_state.view_mode == 'config':
    inject_css('config')
    render_configuration_page()
else:
    render_scrolling_dashboard()