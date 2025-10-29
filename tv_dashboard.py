# tv_dashboard_final_no_sidebar.py
import streamlit as st
import pandas as pd
import time
from streamlit.components.v1 import html
from datetime import datetime

# Assurez-vous que shared_code.py est dans le même dossier
try:
    from shared_code import *
except ImportError:
    st.error("ERREUR : Le fichier 'shared_code.py' est introuvable. Assurez-vous qu'il se trouve dans le même répertoire.")
    st.stop()

# --- 1. CONFIGURATION DE LA PAGE & INITIALISATION ---
st.set_page_config(page_title="Marlodj TV Dashboard", layout="wide", page_icon="📺")


def load_base_css():
    """Charge les CSS qui s'appliquent à TOUTE l'application."""
    try:
        with open("styles.css") as f: st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        with open("led.css") as f: st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError as e:
        st.error(f"Erreur de chargement CSS: Le fichier {e.filename} est introuvable.")

def inject_scrolling_css():
    """Injecte le CSS SPÉCIFIQUE au mode défilement plein écran."""
    st.markdown("""
        <style>
            /* Cache la barre de défilement du corps principal */
            body {
                overflow: hidden;
            }
            /* Cible le conteneur principal de la vue Streamlit pour le transformer en conteneur de défilement */
            [data-testid="stAppViewContainer"] > .main {
                padding: 0;
                margin: 0;
                height: 100vh;
                overflow-y: scroll;
                scroll-snap-type: y mandatory;
                scroll-behavior: smooth;
            }
            /* Chaque section est un point d'arrêt plein écran */
            .main [data-testid="stVerticalBlock"] {
                scroll-snap-align: start;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: space-evenly; /* Distribue l'espace verticalement */
            }
            
            /* --- NOUVELLE RÈGLE POUR RÉDUIRE L'ESPACE SOUS LES TITRES --- */
            /* Cible tous les titres (h1, h2, h3) qui sont à l'intérieur d'un bloc vertical */
            .main [data-testid="stVerticalBlock"] h1,
            .main [data-testid="stVerticalBlock"] h2,
            .main [data-testid="stVerticalBlock"] h3 {
                margin-bottom: 0.5rem !important; /* Réduit la marge inférieure. '!important' pour forcer la priorité */
            }
        </style>
    """, unsafe_allow_html=True)
# Initialisation de l'état de session
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'initial_date_selected' not in st.session_state: st.session_state.initial_date_selected = False
if 'view_mode' not in st.session_state: st.session_state.view_mode = 'config' # 'config' or 'dashboard'
if 'scrolling_active' not in st.session_state: st.session_state.scrolling_active = False
if 'current_section_index' not in st.session_state: st.session_state.current_section_index = 0
if 'section_config' not in st.session_state: st.session_state.section_config = {}
if 'selected_agencies' not in st.session_state: st.session_state.selected_agencies = []

# --- 2. DÉFINITION DES SECTIONS ET MÉCANISME DE DÉFILEMENT ---
SECTIONS = {
    "kpis_et_carte": {"title": "Vue d'Ensemble : KPIs et Carte"},
    "analyse_agence_performance": {"title": "Analyse Agence : Performance & Lenteur"},
    "analyse_agence_frequentation": {"title": "Analyse Agence : Fréquentation"},
    "analyse_service": {"title": "Analyse Détaillée par Service"}, # Exception à 3 graphiques
    "top_sevice": {"title": "Type d'activité par Service"},
    "performance_agent_volume_temps": {"title": "Performance Agent : Volume & Temps Moyen"},
    "performance_agent_evolution_categorie": {"title": "Performance Agent : Évolution & Catégorie"},
    "analyse_attente_hebdomadaire": {"title": "Analyse Attente : Tendance Hebdo"},
    "supervision_monitoring": {"title": "Supervision : Monitoring Temps Réel"},
   # "prediction_affluence": {"title": "Prédiction de l'Affluence Future"},
    "fin_de_cycle": {"title": "Fin du Cycle"},
}

st.markdown("""
    <style>
    /* Cible les éléments avec un ID (nos ancres) */
    [id] {
        scroll-margin-top: 80px; /* Ajustez cette valeur selon la hauteur de votre en-tête */
    }
    </style>
""", unsafe_allow_html=True)
def scroll_to_anchor(anchor_id):
    """
    Injecte du JS qui attend que l'ancre soit disponible, puis fait défiler la page.
    """
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
    # Dans un vrai projet Streamlit, vous utiliseriez st.components.v1.html
    # Pour un notebook, `display(HTML(js_code))` est correct.
    # Ici, nous allons simuler l'appel pour l'exemple.
    st.components.v1.html(js_code, height=0)

# --- 3. CHARGEMENT CENTRALISÉ DES DONNÉES ---
@st.cache_data(ttl=600)
def load_all_data(start_date, end_date):
    conn = get_connection()
    df_main = run_query(conn, SQLQueries().AllQueueQueries, params=(start_date, end_date))
    df_all = df_main[df_main['UserName'].notna()].reset_index(drop=True)
    df_queue = df_main.copy()
    return df_all, df_queue

@st.cache_resource
def load_agencies_regions_info():
    conn = get_connection()
    return run_query(conn, SQLQueries().All_Region_Agences, params=None)

# --- 4. FONCTIONS DE RENDU (Inchangées) ---
def render_kpis_and_map_section(agg_global):
    
    st.markdown('<div id="kpis_et_carte"></div>', unsafe_allow_html=True)
    title=SECTIONS["kpis_et_carte"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    TMO = agg_global["Temps Moyen d'Operation (MIN)"].mean() if not agg_global.empty else 0
    TMA = agg_global["Temps Moyen d'Attente (MIN)"].mean() if not agg_global.empty else 0
    NMC = agg_global['Total Tickets'].sum() if not agg_global.empty else 0
    c1,c2,c3=st.columns(3)
    with c1: c1.metric("Temps Moyen d'Opération (MIN)", f"{TMO:.0f}")
    with c2 :c2.metric("Temps Moyen d'Attente (MIN)", f"{TMA:.0f}")
    with c3 :c3.metric("Nombre Total de Clients", f"{NMC:.0f}")
    
    # agg_map = agg_global.rename(columns={"Nom d'Agence": 'NomAgence', 'Capacité': 'Capacites', "Temps Moyen d'Attente (MIN)": 'Temps_Moyen_Attente', 'Nbs de Clients en Attente': 'AttenteActuel'})
    # map_html = create_folium_map(agg_map)
    # with st.container(): html(map_html, height=200)
    st.divider()
# def render_kpis_and_map_section(agg_global, **kwargs):
#     # L'ancre et le titre restent, mais ils sont maintenant gérés par la mise en page Flexbox
#     st.markdown(f"<h1 style='text-align: center;'>{SECTIONS['kpis_et_carte']['title']}</h1>", unsafe_allow_html=True)
#     with open("styles.css") as f: st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
#     # Les KPIs sont placés dans leurs colonnes
#     TMO = agg_global["Temps Moyen d'Operation (MIN)"].mean() if not agg_global.empty else 0
#     TMA = agg_global["Temps Moyen d'Attente (MIN)"].mean() if not agg_global.empty else 0
#     NMC = agg_global['Total Tickets'].sum() if not agg_global.empty else 0
    
#     kpi1, kpi2, kpi3 = st.columns(3)
#     kpi1.metric("Temps Moyen d'Opération (MIN)", f"{TMO:.0f}")
#     kpi2.metric("Temps Moyen d'Attente (MIN)", f"{TMA:.0f}")
#     kpi3.metric("Nombre Total de Clients", f"{NMC:.0f}")
    
#     # La carte est le dernier élément, elle prendra l'espace restant
#     agg_map = agg_global.rename(columns={
#         "Nom d'Agence": 'NomAgence', 
#         'Capacité': 'Capacites', 
#         "Temps Moyen d'Attente (MIN)": 'Temps_Moyen_Attente', 
#         'Nbs de Clients en Attente': 'AttenteActuel'
#     })
#     map_html = create_folium_map(agg_map)
    
#     # On donne une hauteur généreuse à la carte
#     html(map_html, height=600, scrolling=True)
def render_top_sevice(df_all):
    st.markdown('<div id="top_sevice"></div>', unsafe_allow_html=True)
    title=SECTIONS["top_sevice"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    figures_activity = analyse_activity(df_all, type='Type_Operation', concern='NomService')
    with c1:
        
        
        st_echarts(options=figures_activity[0], height="600px", key="service_activity_1")
   
    with c2:
        
        st_echarts(options=figures_activity[1], height="600px", key="service_activity_2")

   
      



# --- NOUVELLES FONCTIONS DE RENDU POUR L'ANALYSE PAR AGENCE ---

def render_agency_analysis_performance_section(df_all):
    
    st.markdown('<div id="analyse_agence_performance"></div>', unsafe_allow_html=True)
    title=SECTIONS["analyse_agence_performance"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st_echarts(options=stacked_chart2(df_all, 'TempsAttenteReel', 'NomAgence', "Catégorisation du Temps d'Attente"), height="500px")
    with c2:
        st_echarts(options=area_graph2(df_all, concern='NomAgence', time='TempOperation', date_to_bin='Date_Fin', seuil=5, title="Top 5 - Temps d'Opération"), height="500px")
    st.markdown("<hr>", unsafe_allow_html=True)

def render_agency_analysis_frequentation_section(df_all, df_queue):
    st.markdown('<div id="analyse_agence_frequentation"></div>', unsafe_allow_html=True)
    title=SECTIONS["analyse_agence_frequentation"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(top_agence_freq(df_all, df_queue, title=['Total Tickets', 'Total Traités']), use_container_width=True)
    with c2:
        st.plotly_chart(top_agence_freq(df_all, df_queue, title=['Total Tickets', 'Total Rejetées'], color=[green_color, blue_color]), use_container_width=True)
    st.markdown("<hr>", unsafe_allow_html=True)

def render_service_analysis_section(df_all, df_queue):
    st.markdown('<div id="analyse_service"></div>', unsafe_allow_html=True)
    title=SECTIONS["analyse_service"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    col1, col2= st.columns(2)
    with col1:
        st_echarts(options=GraphsGlob2(df_all, "Temps Moyen par Service"), height="600px")
    with col2:
        st_echarts(options=Top10_Type(df_queue, title="Top 10 Opérations"), height="600px")
    
    st.markdown("<hr>", unsafe_allow_html=True)

# --- NOUVELLES FONCTIONS DE RENDU POUR LA PERFORMANCE DES AGENTS ---

def render_agent_performance_volume_temps_section(df_all):
    st.markdown('<div id="performance_agent_volume_temps"></div>', unsafe_allow_html=True)
    title=SECTIONS["performance_agent_volume_temps"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st_echarts(options=create_pie_chart2(df_all, title='Opérations Traitées'), height="500px", key='pie_agent')
    with c2:
        st_echarts(options=create_bar_chart2(df_all, status='Traitée'), height="500px", key="bar_agent")
    st.markdown("<hr>", unsafe_allow_html=True)

def render_agent_performance_evolution_categorie_section(df_all):
    st.markdown('<div id="performance_agent_evolution_categorie"></div>', unsafe_allow_html=True)
    title=SECTIONS["performance_agent_evolution_categorie"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_line_chart(df_all), use_container_width=True)
    with c2:
        st_echarts(options=stacked_chart2(df_all, 'TempOperation', 'UserName', titre="Opérations par Catégorie"), height="600px")
    st.markdown("<hr>", unsafe_allow_html=True)

def render_wait_time_analysis_section(df_queue):
    st.markdown('<div id="analyse_attente_hebdomadaire"></div>', unsafe_allow_html=True)
    title=SECTIONS["analyse_attente_hebdomadaire"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    rapport_pd = run_analysis_pipeline(df_queue, filtrer_semaine=False)
    if rapport_pd.empty:
        st.warning("Données insuffisantes pour l'analyse de l'attente.")
    else:
        rapport_moyen = calculer_moyenne_hebdomadaire(rapport_pd)
        charge_journaliere_df = calculer_charge_journaliere_moyenne(rapport_moyen)
        c1, c2 = st.columns(2)
        with c1:
             st.subheader("Charge Moyenne par Jour")
             if not charge_journaliere_df.empty:
                max_charge = charge_journaliere_df['Charge_Journaliere'].max()
                bar_data = [{"value": round(r['Charge_Journaliere'], 2), "itemStyle": {"color": "#546E7A"} if r['Charge_Journaliere'] == max_charge else {"color": "#6c8dff"}} for _, r in charge_journaliere_df.iterrows()]
                options_bar = {"tooltip": {"trigger": "axis"}, "xAxis": {"type": "category", "data": charge_journaliere_df['Jour_semaine'].tolist()}, "yAxis": {"type": "value"}, "series": [{"type": "bar", "data": bar_data}]}
                st_echarts(options=options_bar, height="500px")
        with c2:
            st.subheader("Heatmap de la Charge Moyenne")
            heures_int = sorted(rapport_moyen['Heure_jour'].unique())
            jours_a_afficher_inverse = rapport_moyen['Jour_semaine'].cat.categories[::-1]
            heatmap_data = [[x, y, round(float(rapport_moyen[(rapport_moyen['Jour_semaine'] == jour) & (rapport_moyen['Heure_jour'] == heure)]['nb_attente_moyen'].values[0]), 2)] for y, jour in enumerate(jours_a_afficher_inverse) for x, heure in enumerate(heures_int) if not rapport_moyen[(rapport_moyen['Jour_semaine'] == jour) & (rapport_moyen['Heure_jour'] == heure)].empty]
            options_heatmap = {"tooltip": {}, "xAxis": {"type": "category", "data": [f"{h:02d}h" for h in heures_int]}, "yAxis": {"type": "category", "data": jours_a_afficher_inverse.tolist()}, "visualMap": {"min": float(rapport_moyen['nb_attente_moyen'].min()), "max": float(rapport_moyen['nb_attente_moyen'].max()), "calculable": True, "orient": "horizontal", "left": "center", "bottom": "5%"}, "series": [{"type": "heatmap", "data": heatmap_data, "label": {"show": True}}]}
            st_echarts(options=options_heatmap, height="500px")
    st.markdown("<hr>", unsafe_allow_html=True)

def render_supervision_monitoring_section(df_all, df_queue, df_agencies_regions):
    st.markdown('<div id="supervision_monitoring"></div>', unsafe_allow_html=True)
    title=SECTIONS["supervision_monitoring"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    # --- Définir les styles au début pour la lisibilité ---
    online_card_style = """
        background-color: #F8F9F9; 
        border: 1px solid #D5D8DC; 
        border-radius: 10px; 
        padding: 12px 16px; 
        margin-bottom: 10px;
        color: black;
        min-height: 170px;
    """
    offline_card_style = """
        background-color: #FEF2F2; 
        border: 1px solid #F8C6C6; 
        border-radius: 10px; 
        padding: 12px 16px; 
        margin-bottom: 10px;
        color: black;
        min-height: 170px;
    """
    section_title_style = """
        text-align: center; 
        width: 100%; 
        margin-top: 10px; 
        margin-bottom: 20px;
        color: #555555;
        font-size: 1.5em; 
        font-weight: 500;
    """
    st.markdown("""
        <style>
            /* Cible le conteneur créé par st.columns */
            [data-testid="stHorizontalBlock"] {
                /* Réduit l'espace en dessous de la grille */
                margin-bottom: 0px; 
            }
        </style>
        """, unsafe_allow_html=True)

     



   
    _, agg_global = AgenceTable(df_all, df_queue)
   
    agg_global = agg_global[agg_global["Nom d'Agence"].isin(st.session_state.selected_agencies)]
    if not agg_global.empty:
        st.markdown(f"<h3 style='{section_title_style}'>Agences en Lignes</h3>", unsafe_allow_html=True)
        
    agg_global = agg_global.sort_values(by='Nbs de Clients en Attente', ascending=False)
    agences_a_afficher = agg_global["Nom d'Agence"].unique()
    num_agences = len(agences_a_afficher)
    
    # Définir le nombre de colonnes, 4 est une bonne valeur pour la lisibilité
    num_cols = 3
    
    # Créer les colonnes dynamiquement
    j=0
    
    agences_a_afficher=list(agences_a_afficher)
    #agences_a_afficher.extend(st.session_stat
    columns_online = st.columns(num_cols)
    for i, nom_agence in enumerate(agences_a_afficher):
        col_index = i % num_cols
        
        agence_data = agg_global[agg_global["Nom d'Agence"] == nom_agence]
        
        # Votre logique de récupération de données reste la même
        max_cap = agence_data['Capacité'].values[0]
        queue_now = agence_data['Nbs de Clients en Attente'].values[0]
        df_agence_queue = df_queue[df_queue['NomAgence'] == nom_agence]
        services_agence = df_agence_queue['NomService'].unique()
        
        service_dict = {}
        for service in services_agence:
            df_service_queue = df_agence_queue[df_agence_queue['NomService'] == service]
            attente_service = current_attente(df_service_queue, nom_agence)
            service_dict[service]=attente_service
            
        row = {
            "NomAgence": nom_agence,
            "Clients en Attente": queue_now,
            "Services": service_dict,
            "Status": get_status_info(queue_now, capacite=max_cap)
        }
        
        # with open("led.css") as f:
        #     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

        services_dynamic_html = ""
        if row['Services']:
            for service_name, client_count in row['Services'].items():
                services_dynamic_html += f"""<div style="text-align: center; margin: 0 5px;">
                        {service_name}<br><strong>{client_count}</strong>
                    </div>"""
        else:
            services_dynamic_html = "<div>Aucun service spécifié.</div>"
        
        with columns_online[col_index]:
            st.markdown(f"""
                            <div style="
                                background-color: {BackgroundGraphicColor}; 
                                border: 1px solid #D5D8DC; 
                                border-radius: 10px; 
                                padding: 12px 16px; 
                                margin-bottom: 10px;
                                color: black;
                                min-height: 170px;
                            ">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <strong style="font-size: 16px;">{row['NomAgence']}</strong>
                                    <div style="display: flex; align-items: center;">
                                        <span class="status-led {row['Status']}"><span class="tooltiptext"></span></span> <span style="font-size: 14px;"></span>
                                    </div>
                                </div>
                                <div style="margin-top: 10px; font-size: 14px;">
                                    Clients en attente : <strong>{row['Clients en Attente']}</strong><br>
                                    Capacité Maximale : <strong>{max_cap}</strong><br>
                                    <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin-top: 10px;">
                                        {services_dynamic_html}
                            </div>
                            """, unsafe_allow_html=True)
            
    all_known_agencies = df_agencies_regions['NomAgence'].dropna().unique().tolist()
    offline_agencies = sorted([a for a in all_known_agencies if a not in agences_a_afficher])
    if offline_agencies:
        st.subheader("Agences Hors Ligne")
        for i in range(0, len(offline_agencies), num_cols):
            cols = st.columns(num_cols)
            agences_chunk = offline_agencies[i:i + num_cols]
            for j, nom_agence in enumerate(agences_chunk):
                with cols[j]:
                    st.markdown(f"""<div style="background-color: #FEF2F2; border: 1px solid #F8C6C6; border-radius: 10px; padding: 12px; margin-bottom: 10px; color: black; min-height: 120px;">
                        <strong style="font-size: 16px;">{nom_agence}</strong>
                    </div>""", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
def render_prediction_section(df_queue_filtered, conn):
    title=SECTIONS["prediction_affluence"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    is_today = (st.session_state.end_date == datetime.now().date())
    if is_today and not df_queue_filtered.empty:
        df_actual = df_queue_filtered[["Date_Reservation", "Date_Appel", "Date_Fin", "NomAgence"]]
        yesterday = st.session_state.end_date - timedelta(days=1)
        
        with st.spinner("Calcul des prédictions en cours..."):
            df_past = run_query(conn, SQLQueries().AllQueueQueries, params=(yesterday, yesterday))
            df_past = df_past[df_past['NomAgence'].isin(st.session_state.selected_agencies)]
            df_past = df_past[["Date_Reservation", "Date_Appel", "Date_Fin", "NomAgence"]]
            
            df_observed, df_predictions, current_time = run_prediction_pipeline(df_actual, df_past)

        if df_observed is not None and df_predictions is not None:
            all_agencies = df_predictions.index.get_level_values('NomAgence').unique().tolist()
            num_columns = 2
            for i in range(0, len(all_agencies), num_columns):
                cols = st.columns(num_columns)
                row_agencies = all_agencies[i : i + num_columns]
                for j, agency in enumerate(row_agencies):
                    with cols[j]:
                        st.markdown(f"<h3 style='text-align: center;'>{agency}</h3>", unsafe_allow_html=True)
                        observed_agency_data = df_observed.loc[agency]
                        predicted_agency_data = df_predictions.loc[agency]
                        
                        display_start_time = current_time - pd.Timedelta(hours=23)
                        past_data = observed_agency_data.loc[display_start_time:current_time]['nb_attente']
                        future_data = predicted_agency_data['prediction']
                        dates_list = past_data.index.strftime('%Hh').tolist() + future_data.index.strftime('%Hh').tolist()
                        past_values = np.round(past_data.values, 2).tolist()
                        future_values = np.round(future_data.values, 2).tolist()
                        
                        options = {
                            "tooltip": {"trigger": "axis"},
                            "legend": {"data": ["Affluence observée", "Affluence Prédite"], "top": 5},
                            "xAxis": {"type": "category", "data": dates_list},
                            "yAxis": {"type": "value", "name": "Moyenne"},
                            "grid": {"left": "10%", "right": "5%", "top": "15%", "bottom": "10%"},
                            "series": [
                                {"name": "Affluence observée", "type": "line", "data": past_values, "lineStyle": {"color": "#3398DB"}},
                                {"name": "Affluence Prédite", "type": "line", "data": [None] * len(past_values) + future_values, "lineStyle": {"color": "#FF5733", "type": "dashed"}}
                            ]
                        }
                        st_echarts(options=options, height="400px", key=f"pred_{agency}")
        else:
            st.error("Impossible de générer les prédictions.")
    else:
        st.info("Les prédictions ne sont disponibles que si la date de fin sélectionnée est aujourd'hui.")
    st.markdown("<hr>", unsafe_allow_html=True)

def render_end_section():
    st.markdown('<div id="fin_de_cycle"></div>', unsafe_allow_html=True)
    title=SECTIONS["fin_de_cycle"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    st.success("Le défilement va redémarrer depuis le début...")

# --- 5. INTERFACE ET LOGIQUE PRINCIPALE ---

def render_configuration_page(df_online_data):
    st.title("Configuration du Dashboard TV")
    
    _, col_logout = st.columns([0.9, 0.1])
    with col_logout:
        if st.button("🚪", help="Se déconnecter"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        st.header("Étape 1 : Filtrer les Données")
        st.session_state.start_date = st.date_input("Date de début", st.session_state.start_date)
        st.session_state.end_date = st.date_input("Date de fin", st.session_state.end_date)
        
        online_regions = sorted(df_online_data['Region'].dropna().unique())
        all_online_agencies = sorted(df_online_data['NomAgence'].dropna().unique())

        with st.popover("Filtrer par Régions et Agences", use_container_width=True):
            st.subheader("Régions")
            pop_c1, pop_c2 = st.columns(2)
            if pop_c1.button("Toutes les régions", key="select_all_regions", use_container_width=True):
                st.session_state.selected_agencies = all_online_agencies
                st.rerun()
            if pop_c2.button("Aucune région", key="deselect_all_regions", use_container_width=True):
                st.session_state.selected_agencies = []
                st.rerun()
            
            with st.container(height=200):
                for region in online_regions:
                    agencies_in_region = df_online_data[df_online_data['Region'] == region]['NomAgence'].unique()
                    is_region_selected = any(agency in st.session_state.selected_agencies for agency in agencies_in_region)
                    if st.checkbox(region, value=is_region_selected, key=f"cb_region_{region}") != is_region_selected:
                        if is_region_selected:
                            st.session_state.selected_agencies = [a for a in st.session_state.selected_agencies if a not in agencies_in_region]
                        else:
                            st.session_state.selected_agencies.extend([a for a in agencies_in_region if a not in st.session_state.selected_agencies])
                        st.rerun()
            
            st.divider()
            st.subheader("Agences")
            pop_c3, pop_c4 = st.columns(2)
            if pop_c3.button("Toutes les agences", key="select_all_agencies", use_container_width=True):
                st.session_state.selected_agencies = all_online_agencies
                st.rerun()
            if pop_c4.button("Aucune agence", key="deselect_all_agencies", use_container_width=True):
                st.session_state.selected_agencies = []
                st.rerun()
            with st.container(height=300):
                for agency in all_online_agencies:
                    is_selected = agency in st.session_state.selected_agencies
                    if st.checkbox(agency, value=is_selected, key=f"cb_agency_{agency}") != is_selected:
                        if is_selected:
                            st.session_state.selected_agencies.remove(agency)
                        else:
                            st.session_state.selected_agencies.append(agency)
                        st.rerun()

    with col2:
        st.header("Étape 2 : Configurer le Défilement")
        st.session_state.scroll_duration = st.number_input("Durée de visualisation par section (secondes)", min_value=5, value=st.session_state.get('scroll_duration', 15), step=1)
        
        st.markdown("**Sections à inclure dans le défilement :**")
        with st.container(height=400):
            # --- DÉBUT DE LA CORRECTION ---
            # On vérifie si la configuration existe OU si ses clés ne correspondent plus à nos sections
            if 'section_config' not in st.session_state or set(st.session_state.section_config.keys()) != set(SECTIONS.keys()):
                # Si c'est le cas, on la reconstruit à partir de zéro
                st.session_state.section_config = {sec_id: {'enabled': True} for sec_id in SECTIONS}
            # --- FIN DE LA CORRECTION ---

            for sec_id, details in SECTIONS.items():
                st.session_state.section_config[sec_id]['enabled'] = st.checkbox(
                    f"{details['title']}", 
                    value=st.session_state.section_config[sec_id].get('enabled', True), 
                    key=f"check_{sec_id}"
                )

    st.divider()
    if st.button("▶️ Lancer le Dashboard en Mode TV", use_container_width=True, type="primary"):
        st.session_state.view_mode = 'dashboard'
        st.session_state.scrolling_active = True
        st.session_state.current_section_index = 0
        st.rerun()

# def render_scrolling_dashboard():
#     # Afficher les contrôles en haut
#     if st.button("⏹️ Arrêter et Reconfigurer"):
#         st.session_state.view_mode = 'config'
#         st.session_state.scrolling_active = False
#         st.rerun()
        
#     # Charger les données filtrées
#     with st.spinner("Chargement des données..."):
#         df_all, df_queue = load_all_data(st.session_state.start_date, st.session_state.end_date)
#         df_all_filtered = df_all[df_all['NomAgence'].isin(st.session_state.selected_agencies)]
#         df_queue_filtered = df_queue[df_queue['NomAgence'].isin(st.session_state.selected_agencies)]
#         if df_all_filtered.empty:
#             st.warning("Aucune donnée pour les filtres. Retour à la configuration.")
#             st.session_state.view_mode = 'config'; st.session_state.scrolling_active = False
#             time.sleep(3); st.rerun()
#         _, agence_global, _, _ = AgenceTable2(df_all_filtered, df_queue_filtered)
    
#     # Dictionnaire des fonctions de rendu
#     render_functions = {
#         "kpis_et_carte": (render_kpis_and_map_section, {'agg_global': agence_global}),
#         "top_sevice": (render_top_sevice, {'df_all': df_all_filtered}),
#         "analyse_agence_performance": (render_agency_analysis_performance_section, {'df_all': df_all_filtered}),
#         "analyse_agence_frequentation": (render_agency_analysis_frequentation_section, {'df_all': df_all_filtered, 'df_queue': df_queue_filtered}),
#         "analyse_service": (render_service_analysis_section, {'df_all': df_all_filtered, 'df_queue': df_queue_filtered}),
#         "performance_agent_volume_temps": (render_agent_performance_volume_temps_section, {'df_all': df_all_filtered}),
#         "performance_agent_evolution_categorie": (render_agent_performance_evolution_categorie_section, {'df_all': df_all_filtered}),
#         "analyse_attente_hebdomadaire": (render_wait_time_analysis_section, {'df_queue': df_queue_filtered}),
#         "supervision_monitoring": (render_supervision_monitoring_section, {'df_all': df_all_filtered, 'df_queue': df_queue_filtered, 'df_agencies_regions': load_agencies_regions_info()}),
#         #"prediction_affluence": (render_prediction_section, {'df_queue_filtered': df_queue_filtered, 'conn': get_connection()}),
#         "fin_de_cycle": (render_end_section, {}),
#     }

#     enabled_anchors = [sec_id for sec_id, config in st.session_state.section_config.items() if config['enabled']]
    
#     # NE Rendre QUE les sections activées
#     for anchor in enabled_anchors:
#         if anchor in render_functions:
#             func, kwargs = render_functions[anchor]
#             func(**kwargs)

#     # Logique de défilement
#     if not enabled_anchors:
#         st.warning("Aucune section n'est activée. Retour à la configuration."); time.sleep(3)
#         st.session_state.view_mode = 'config'; st.session_state.scrolling_active = False; st.rerun()
    
#     current_anchor_id = enabled_anchors[st.session_state.current_section_index]
#     scroll_to_anchor(current_anchor_id)
#     time.sleep(st.session_state.get('scroll_duration', 15))
#     st.session_state.current_section_index = (st.session_state.current_section_index + 1) % len(enabled_anchors)
#     st.rerun()
def render_scrolling_dashboard():
     # Cette ligne est la clé : le CSS plein écran n'est injecté que dans ce mode.
    inject_scrolling_css()
    # Afficher le bouton d'arrêt en haut de la page (placé de manière fixe)
    st.markdown("""
        <div style="position: fixed; top: 1rem; right: 1rem; z-index: 999;">
    """, unsafe_allow_html=True)
    if st.button("⏹️ Arrêter et Reconfigurer"):
        st.session_state.view_mode = 'config'
        st.session_state.scrolling_active = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
        
    # Charger les données filtrées
    with st.spinner("Chargement des données..."):
        df_all, df_queue = load_all_data(st.session_state.start_date, st.session_state.end_date)
        df_all_filtered = df_all[df_all['NomAgence'].isin(st.session_state.selected_agencies)]
        df_queue_filtered = df_queue[df_queue['NomAgence'].isin(st.session_state.selected_agencies)]
        if df_all_filtered.empty:
            st.warning("Aucune donnée pour les filtres. Retour à la configuration.")
            st.session_state.view_mode = 'config'; st.session_state.scrolling_active = False
            time.sleep(3); st.rerun()
        _, agence_global, _, _ = AgenceTable2(df_all_filtered, df_queue_filtered)
    
    # Dictionnaire des fonctions de rendu (inchangé)
    render_functions = {
        "kpis_et_carte": (render_kpis_and_map_section, {'agg_global': agence_global}),
        "top_sevice": (render_top_sevice, {'df_all': df_all_filtered}),
        "analyse_agence_performance": (render_agency_analysis_performance_section, {'df_all': df_all_filtered}),
        "analyse_agence_frequentation": (render_agency_analysis_frequentation_section, {'df_all': df_all_filtered, 'df_queue': df_queue_filtered}),
        "analyse_service": (render_service_analysis_section, {'df_all': df_all_filtered, 'df_queue': df_queue_filtered}),
        "performance_agent_volume_temps": (render_agent_performance_volume_temps_section, {'df_all': df_all_filtered}),
        "performance_agent_evolution_categorie": (render_agent_performance_evolution_categorie_section, {'df_all': df_all_filtered}),
        "analyse_attente_hebdomadaire": (render_wait_time_analysis_section, {'df_queue': df_queue_filtered}),
        "supervision_monitoring": (render_supervision_monitoring_section, {'df_all': df_all_filtered, 'df_queue': df_queue_filtered, 'df_agencies_regions': load_agencies_regions_info()}),
        "fin_de_cycle": (render_end_section, {}),
    }

    enabled_anchors = [sec_id for sec_id, config in st.session_state.section_config.items() if config['enabled']]
    
    # --- NOUVELLE LOGIQUE DE RENDU SIMPLIFIÉE ---
    # On boucle et on appelle simplement les fonctions. Le CSS fait le reste.
    for anchor in enabled_anchors:
        if anchor in render_functions:
            func, kwargs = render_functions[anchor]
            # Chaque appel de fonction crée un nouveau bloc vertical que notre CSS va cibler
            func(**kwargs)
            
    # --- LOGIQUE DE DÉFILEMENT INCHANGÉE ---
    if not enabled_anchors:
        st.warning("Aucune section n'est activée. Retour à la configuration."); time.sleep(3)
        st.session_state.view_mode = 'config'; st.session_state.scrolling_active = False; st.rerun()
    
    current_anchor_id = enabled_anchors[st.session_state.current_section_index]
    scroll_to_anchor(current_anchor_id) # Le JS déclenche le défilement
    
    time.sleep(st.session_state.get('scroll_duration', 15))
    
    st.session_state.current_section_index = (st.session_state.current_section_index + 1) % len(enabled_anchors)
    st.rerun()
# --- 6. ROUTEUR PRINCIPAL DE L'APPLICATION ---

# def show_login_page():
#     st.title("Connexion au Dashboard Marlodj")
#     conn = get_connection()
#     df_users = run_query(conn, SQLQueries().ProfilQueries)
#     users_dict = dict(zip(df_users['UserName'], df_users['MotDePasse']))
    
#     with st.form("login_form"):
#         username = st.text_input("Nom d'utilisateur")
#         password = st.text_input("Mot de passe", type="password")
#         if st.form_submit_button("Se connecter"):
#             if users_dict.get(username) == password:
#                 st.session_state.logged_in = True
#                 st.rerun()
#             else:
#                 st.error("Nom d'utilisateur ou mot de passe incorrect.")
def show_login_page():
    # --- NOUVEAU : Créer des colonnes pour centrer le contenu ---
    # Nous créons 3 colonnes, la colonne du milieu sera plus large
    # Les colonnes latérales vides serviront de marges.
    col1, col2, col3 = st.columns([1, 1.5, 1])

    # Tout le contenu de la page de connexion ira dans la colonne du milieu
    with col2:
        # Optionnel : Affichez un logo au-dessus du formulaire
        try:
            # Assurez-vous d'avoir un fichier 'logo.png' dans votre dossier
            st.image("logo.png", width=200) 
        except Exception:
            # Si le logo n'est pas trouvé, on ne fait rien
            pass

        # Appliquer un style CSS pour créer un effet de "carte"
        st.markdown("""
            <style>
                .login-card {
                    padding: 1rem;
                    border-radius: 10px;
                    background-color: #FFFFFF;
                    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Envelopper le tout dans un conteneur avec la classe CSS
        with st.container():
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            
            st.title("Connexion au Dashboard Marlodj")
            
            # La logique de connexion reste la même
            conn = get_connection()
            df_users = run_query(conn, SQLQueries().ProfilQueries)
            users_dict = dict(zip(df_users['UserName'], df_users['MotDePasse']))
            
            with st.form("login_form"):
                st.text_input("Nom d'utilisateur", key="username_input")
                st.text_input("Mot de passe", type="password", key="password_input")
                
                # --- NOUVEAU : Améliorer le bouton ---
                submitted = st.form_submit_button(
                    "Se connecter", 
                    use_container_width=True, # Le bouton prend toute la largeur du formulaire
                    type="primary" # Style plus visible
                )
                
                if submitted:
                    username = st.session_state.username_input
                    password = st.session_state.password_input
                    
                    if users_dict.get(username) == password:
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("Nom d'utilisateur ou mot de passe incorrect.")
            
            st.markdown('</div>', unsafe_allow_html=True)
def show_initial_date_selection_page():
    st.title("Bienvenue sur le Dashboard TV")
    st.header("Veuillez sélectionner une plage de dates initiale pour commencer")
    today = datetime.now().date()
    c1, c2 = st.columns(2)
    start_date = c1.date_input("Date de début", today)
    end_date = c2.date_input("Date de fin", today)
    
    if start_date > end_date:
        st.error("La date de début ne peut pas être après la date de fin.")
    elif st.button("Charger le Dashboard", use_container_width=True, type="primary"):
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date
        st.session_state.initial_date_selected = True
        st.session_state.scrolling_active = False
        st.rerun()

# Charger les CSS de base une seule fois au début
load_base_css()
if not st.session_state.logged_in:
    show_login_page()
elif not st.session_state.initial_date_selected:
    show_initial_date_selection_page()
elif st.session_state.view_mode == 'config':
    # On a besoin des données pour initialiser les filtres, même en mode config
    with st.spinner("Chargement des données initiales..."):
        df_all, _ = load_all_data(st.session_state.get('start_date', datetime.now().date()), st.session_state.get('end_date', datetime.now().date()))
        if not st.session_state.selected_agencies: # Initialiser si la liste est vide
             st.session_state.selected_agencies = df_all['NomAgence'].unique().tolist()
    render_configuration_page(df_all)
else: # view_mode == 'dashboard'
    render_scrolling_dashboard()