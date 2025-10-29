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

def load_all_css():
    try:
        with open("styles.css") as f: st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        with open("led.css") as f: st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        st.markdown("""<style>iframe[title="streamlit_echarts.st_echarts"]{ min-height: 500px !important }</style>""", unsafe_allow_html=True)
    except FileNotFoundError as e:
        st.error(f"Erreur de chargement CSS: Le fichier {e.filename} est introuvable.")

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
    "tableau_global": {"title": "Tableau Global par Agence"},
    "analyse_agence_performance": {"title": "Analyse Agence : Performance & Lenteur"},
    "analyse_agence_frequentation": {"title": "Analyse Agence : Fréquentation"},
    "analyse_service": {"title": "Analyse Détaillée par Service"}, # Exception à 3 graphiques
    "performance_agent_volume_temps": {"title": "Perf. Agent : Volume & Temps Moyen"},
    "performance_agent_evolution_categorie": {"title": "Perf. Agent : Évolution & Catégorie"},
    "analyse_attente_hebdomadaire": {"title": "Analyse Attente : Tendance Hebdo"},
    "supervision_monitoring": {"title": "Supervision : Monitoring Temps Réel"},
    "prediction_affluence": {"title": "Prédiction de l'Affluence Future"},
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
    st.markdown(f'<div id="kpis_et_carte"></div>', unsafe_allow_html=True)
    st.header(SECTIONS["kpis_et_carte"]['title'])
    TMO = agg_global["Temps Moyen d'Operation (MIN)"].mean() if not agg_global.empty else 0
    TMA = agg_global["Temps Moyen d'Attente (MIN)"].mean() if not agg_global.empty else 0
    NMC = agg_global['Total Tickets'].sum() if not agg_global.empty else 0
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Temps Moyen d'Opération (MIN)", f"{TMO:.0f}")
    kpi2.metric("Temps Moyen d'Attente (MIN)", f"{TMA:.0f}")
    kpi3.metric("Nombre Total de Clients", f"{NMC:.0f}")
    st.divider()
    agg_map = agg_global.rename(columns={"Nom d'Agence": 'NomAgence', 'Capacité': 'Capacites', "Temps Moyen d'Attente (MIN)": 'Temps_Moyen_Attente', 'Nbs de Clients en Attente': 'AttenteActuel'})
    map_html = create_folium_map(agg_map)
    with st.container(): html(map_html, height=450)
    st.markdown("<hr>", unsafe_allow_html=True)

def render_global_table_section(agence_global):
    st.markdown(f'<div id="tableau_global"></div>', unsafe_allow_html=True)
    st.header(SECTIONS["tableau_global"]['title'])
    if not agence_global.empty:
        st.dataframe(agence_global.drop(columns=['Longitude', 'Latitude'], errors='ignore'), use_container_width=True, height=500)
    st.markdown("<hr>", unsafe_allow_html=True)

# --- NOUVELLES FONCTIONS DE RENDU POUR L'ANALYSE PAR AGENCE ---

def render_agency_analysis_performance_section(df_all):
    st.markdown(f'<div id="analyse_agence_performance"></div>', unsafe_allow_html=True)
    st.header(SECTIONS["analyse_agence_performance"]['title'])
    c1, c2 = st.columns(2)
    with c1:
        st_echarts(options=stacked_chart2(df_all, 'TempsAttenteReel', 'NomAgence', "Catégorisation du Temps d'Attente"), height="500px")
    with c2:
        st_echarts(options=area_graph2(df_all, concern='NomAgence', time='TempOperation', date_to_bin='Date_Fin', seuil=5, title="Top 5 - Temps d'Opération"), height="500px")
    st.markdown("<hr>", unsafe_allow_html=True)

def render_agency_analysis_frequentation_section(df_all, df_queue):
    st.markdown(f'<div id="analyse_agence_frequentation"></div>', unsafe_allow_html=True)
    st.header(SECTIONS["analyse_agence_frequentation"]['title'])
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(top_agence_freq(df_all, df_queue, title=['Total Tickets', 'Total Traités']), use_container_width=True)
    with c2:
        st.plotly_chart(top_agence_freq(df_all, df_queue, title=['Total Tickets', 'Total Rejetées'], color=[green_color, blue_color]), use_container_width=True)
    st.markdown("<hr>", unsafe_allow_html=True)

def render_service_analysis_section(df_all, df_queue):
    st.markdown(f'<div id="analyse_service"></div>', unsafe_allow_html=True)
    st.header(SECTIONS["analyse_service"]['title'])
    col1, col2, col3 = st.columns(3)
    with col1:
        st_echarts(options=GraphsGlob2(df_all, "Temps Moyen par Service"), height="600px")
    with col2:
        st_echarts(options=Top10_Type(df_queue, title="Top 10 Opérations"), height="600px")
    with col3:
        figures_activity = analyse_activity(df_all, type='Type_Operation', concern='NomService')
        if figures_activity:
            st_echarts(options=figures_activity[0], height="600px", key="service_activity_chart")
        else:
            st.info("Pas de données pour l'analyse d'activité détaillée.")
    st.markdown("<hr>", unsafe_allow_html=True)

# --- NOUVELLES FONCTIONS DE RENDU POUR LA PERFORMANCE DES AGENTS ---

def render_agent_performance_volume_temps_section(df_all):
    st.markdown(f'<div id="performance_agent_volume_temps"></div>', unsafe_allow_html=True)
    st.header(SECTIONS["performance_agent_volume_temps"]['title'])
    c1, c2 = st.columns(2)
    with c1:
        st_echarts(options=create_pie_chart2(df_all, title='Opérations Traitées'), height="500px", key='pie_agent')
    with c2:
        st_echarts(options=create_bar_chart2(df_all, status='Traitée'), height="500px", key="bar_agent")
    st.markdown("<hr>", unsafe_allow_html=True)

def render_agent_performance_evolution_categorie_section(df_all):
    st.markdown(f'<div id="performance_agent_evolution_categorie"></div>', unsafe_allow_html=True)
    st.header(SECTIONS["performance_agent_evolution_categorie"]['title'])
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_line_chart(df_all), use_container_width=True)
    with c2:
        st_echarts(options=stacked_chart2(df_all, 'TempOperation', 'UserName', titre="Opérations par Catégorie"), height="600px")
    st.markdown("<hr>", unsafe_allow_html=True)

def render_wait_time_analysis_section(df_queue):
    st.markdown(f'<div id="analyse_attente_hebdomadaire"></div>', unsafe_allow_html=True)
    st.header(SECTIONS["analyse_attente_hebdomadaire"]['title'])
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
    st.markdown(f'<div id="supervision_monitoring"></div>', unsafe_allow_html=True)
    st.header(SECTIONS["supervision_monitoring"]['title'])
    online_agencies = df_queue['NomAgence'].unique().tolist()
    all_known_agencies = df_agencies_regions['NomAgence'].dropna().unique().tolist()
    offline_agencies = sorted([a for a in all_known_agencies if a not in online_agencies])
    _, agg_global = AgenceTable(df_all, df_queue)
    agg_global = agg_global.sort_values(by='Nbs de Clients en Attente', ascending=False)
    
    st.subheader("Agences en Ligne")
    num_cols = 4
    for i in range(0, len(online_agencies), num_cols):
        cols = st.columns(num_cols)
        agences_chunk = online_agencies[i:i + num_cols]
        for j, nom_agence in enumerate(agences_chunk):
            with cols[j]:
                agence_data = agg_global[agg_global["Nom d'Agence"] == nom_agence]
                if not agence_data.empty:
                    queue_now = agence_data['Nbs de Clients en Attente'].values[0]
                    max_cap = agence_data['Capacité'].values[0]
                    status_class = get_status_info(queue_now, max_cap)
                    st.markdown(f"""<div style="background-color: #F8F9F9; border: 1px solid #D5D8DC; border-radius: 10px; padding: 12px; margin-bottom: 10px; color: black; min-height: 120px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong style="font-size: 16px;">{nom_agence}</strong>
                            <span class="status-led {status_class}"><span class="tooltiptext"></span></span>
                        </div>
                        <div style="margin-top: 10px; font-size: 14px;">Clients en attente : <strong>{queue_now} / {max_cap}</strong></div>
                    </div>""", unsafe_allow_html=True)

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
    st.markdown(f'<div id="prediction_affluence"></div>', unsafe_allow_html=True)
    st.header(SECTIONS["prediction_affluence"]['title'])
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
    st.markdown(f'<div id="fin_de_cycle"></div>', unsafe_allow_html=True)
    st.header(SECTIONS["fin_de_cycle"]['title'])
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

def render_scrolling_dashboard():
    # Afficher les contrôles en haut
    if st.button("⏹️ Arrêter et Reconfigurer"):
        st.session_state.view_mode = 'config'
        st.session_state.scrolling_active = False
        st.rerun()
        
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
    
    # Dictionnaire des fonctions de rendu
    render_functions = {
        "kpis_et_carte": (render_kpis_and_map_section, {'agg_global': agence_global}),
        "tableau_global": (render_global_table_section, {'agence_global': agence_global}),
        "analyse_agence_performance": (render_agency_analysis_performance_section, {'df_all': df_all_filtered}),
        "analyse_agence_frequentation": (render_agency_analysis_frequentation_section, {'df_all': df_all_filtered, 'df_queue': df_queue_filtered}),
        "analyse_service": (render_service_analysis_section, {'df_all': df_all_filtered, 'df_queue': df_queue_filtered}),
        "performance_agent_volume_temps": (render_agent_performance_volume_temps_section, {'df_all': df_all_filtered}),
        "performance_agent_evolution_categorie": (render_agent_performance_evolution_categorie_section, {'df_all': df_all_filtered}),
        "analyse_attente_hebdomadaire": (render_wait_time_analysis_section, {'df_queue': df_queue_filtered}),
        "supervision_monitoring": (render_supervision_monitoring_section, {'df_all': df_all_filtered, 'df_queue': df_queue_filtered, 'df_agencies_regions': load_agencies_regions_info()}),
        "prediction_affluence": (render_prediction_section, {'df_queue_filtered': df_queue_filtered, 'conn': get_connection()}),
        "fin_de_cycle": (render_end_section, {}),
    }

    enabled_anchors = [sec_id for sec_id, config in st.session_state.section_config.items() if config['enabled']]
    
    # NE Rendre QUE les sections activées
    for anchor in enabled_anchors:
        if anchor in render_functions:
            func, kwargs = render_functions[anchor]
            func(**kwargs)

    # Logique de défilement
    if not enabled_anchors:
        st.warning("Aucune section n'est activée. Retour à la configuration."); time.sleep(3)
        st.session_state.view_mode = 'config'; st.session_state.scrolling_active = False; st.rerun()
    
    current_anchor_id = enabled_anchors[st.session_state.current_section_index]
    scroll_to_anchor(current_anchor_id)
    time.sleep(st.session_state.get('scroll_duration', 15))
    st.session_state.current_section_index = (st.session_state.current_section_index + 1) % len(enabled_anchors)
    st.rerun()

# --- 6. ROUTEUR PRINCIPAL DE L'APPLICATION ---

def show_login_page():
    st.title("Connexion au Dashboard Marlodj")
    conn = get_connection()
    df_users = run_query(conn, SQLQueries().ProfilQueries)
    users_dict = dict(zip(df_users['UserName'], df_users['MotDePasse']))
    
    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        if st.form_submit_button("Se connecter"):
            if users_dict.get(username) == password:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")

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

load_all_css()
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