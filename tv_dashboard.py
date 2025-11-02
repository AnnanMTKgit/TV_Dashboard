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
                margin-top: -80px;
                
                height: calc(100vh + 70px);
                /*height: 100vh;; */
                overflow-y: scroll;
                scroll-snap-type: y mandatory;
                scroll-behavior: smooth;
                
}
                
            
            }
            
            .main [data-testid="stVerticalBlock"] {
                scroll-snap-align: start;
                height: 100vh;;
                display: flex;
                flex-direction: column;
                justify-content:  center;
                
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
if 'display_state' not in st.session_state: st.session_state.display_state = 'show_content'
# --- 2. DÉFINITION DES SECTIONS ET MÉCANISME DE DÉFILEMENT ---
SECTIONS = {
    "kpis_et_carte": {"title": "Vue d'Ensemble : KPIs "},
    "analyse_agence_performance": {"title": "Analyse Agence : Performance & Lenteur"},
    "analyse_agence_frequentation": {"title": "Analyse Agence : Fréquentation"},
    "analyse_service": {"title": "Analyse Détaillée par Service"}, # Exception à 3 graphiques
    "top_sevice": {"title": "Type d'activité par Service"},
    "performance_agent_volume_temps": {"title": "Performance Agent : Volume & Temps Moyen"},
    "performance_agent_evolution_categorie": {"title": "Performance Agent : Évolution & Catégorie"},
    "analyse_attente_hebdomadaire": {"title": "Analyse Attente : Tendance Journalière"},
    "supervision_monitoring": {"title": "Supervision : Monitoring Temps Réel"},
   # "prediction_affluence": {"title": "Prédiction de l'Affluence Future"},
   "supervision_offline": {"title": "Supervision : Agences Hors Ligne"}, # <-- NOUVELLE LIGNE
    # "fin_de_cycle": {"title": "Fin du Cycle"},
}


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
# --- NOUVELLE FONCTION CIRCLE AMÉLIORÉE ---
def kpi_circle_chart(label, value, max_value, color_scheme):
    """
    Crée un graphique circulaire de type KPI avec Altair.
    
    Args:
        label (str): Le libellé du KPI.
        value (float): La valeur actuelle à afficher.
        max_value (float): La valeur maximale de l'échelle pour le pourcentage.
        color_scheme (list): Une liste de deux couleurs [couleur_principale, couleur_fond].
    """
    if max_value == 0:  # Éviter la division par zéro
        percent_value = 0
    else:
        percent_value = min((value / max_value) * 100, 100) # Assure que la valeur ne dépasse pas 100%

    source = pd.DataFrame({
        "category": [label, ''],
        "value": [percent_value, 100 - percent_value]
    })

    base = alt.Chart(source).encode(
        theta=alt.Theta("value:Q", stack=True),
        color=alt.Color("category:N",
                      scale=alt.Scale(domain=[label, ''], range=color_scheme),
                      legend=None)
    ).properties(
        width=180,
        height=180
    )
    
    # Le cercle de progression
    arc = base.mark_arc(innerRadius=90, cornerRadius=10)

    # Le texte de la valeur au centre
    text_value = alt.Chart(pd.DataFrame({'value': [f"{value:,.0f}"]})).mark_text(
        align='center',
        baseline='middle',
        fontSize=40,
        fontWeight='bold',
        color=color_scheme[0]
    ).encode(text='value:N')

    # Le texte du libellé en dessous
    text_label = alt.Chart(pd.DataFrame({'label': [label]})).mark_text(
        align='center',
        baseline='middle',
        fontSize=14,
        dy=40, # Décalage vertical pour placer le texte en dessous
        color='#666'
    ).encode(text='label:N')

    # Superposer les graphiques
    return (arc + text_value + text_label)

def render_kpis_and_map_section(agg_global, df_all_filtered):
    st.markdown('<div id="kpis_et_carte"></div>', unsafe_allow_html=True) 
    title=SECTIONS["kpis_et_carte"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    # --- 1. Calcul des KPIs ---
    TMO = agg_global["Temps Moyen d'Operation (MIN)"].mean() if not agg_global.empty else 0
    TMA = agg_global["Temps Moyen d'Attente (MIN)"].mean() if not agg_global.empty else 0
    NMC = agg_global['Total Tickets'].sum() if not agg_global.empty else 0
    
    kpi_rh = df_all_filtered.groupby("NomService")["UserName"].nunique().reset_index().rename(columns={"UserName": "Nombre_Agents"})
   
    kpi_cols = st.columns(6)
    
    with kpi_cols[0]:
        chart = kpi_circle_chart("Tps Moyen Opération", TMO, max_value=30, color_scheme=['#3498DB', '#EAECEE'])
        st.altair_chart(chart, use_container_width=True)

    with kpi_cols[1]:
        chart = kpi_circle_chart("Tps Moyen Attente", TMA, max_value=60, color_scheme=['#F39C12', '#EAECEE'])
        st.altair_chart(chart, use_container_width=True)
        
    with kpi_cols[2]:
        # Pour le nombre de clients, on peut utiliser une échelle dynamique
        max_clients = (math.ceil(NMC / 1000) + 1) * 1000 if NMC > 0 else 1000
        chart = kpi_circle_chart("Total Clients", NMC, max_value=max_clients, color_scheme=['#2ECC71', '#EAECEE'])
        st.altair_chart(chart, use_container_width=True)

    
    if not kpi_rh.empty:
        num_services = len(kpi_rh)
        rh_cols = st.columns(num_services)
        
        # Définir des couleurs pour chaque service
        service_colors = {
            "Caissier": ['#E74C3C', '#EAECEE'],
            "Clientele": ['#8E44AD', '#EAECEE'],
            "Default": ['#7F8C8D', '#EAECEE']
        }

        for i, row in kpi_rh.iterrows():
            service_name = row["NomService"]
            agent_count = row["Nombre_Agents"]
            colors = service_colors.get(service_name, service_colors["Default"])
            
            with kpi_cols[i+2]:
                # On peut définir une échelle max pour les agents, par exemple 10
                chart = kpi_circle_chart(f"Agents {service_name}", agent_count, max_value=10, color_scheme=colors)
                st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Aucune donnée sur les ressources par service disponible.")

    #st.markdown("<hr>", unsafe_allow_html=True)
# def render_kpis_and_map_section(agg_global,df_all_filtered):
    
#     st.markdown('<div id="kpis_et_carte"></div>', unsafe_allow_html=True)
#     title=SECTIONS["kpis_et_carte"]['title']
#     st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
#     # --- 1. Style CSS pour les cartes (basé sur votre exemple) ---
#     st.markdown("""
#     <style>
#         .custom-card {
#             background-color: #FFFFFF; 
#             border: 1px solid #D5D8DC; 
#             border-radius: 10px; 
#             padding: 0!important;
#             margin: 0;
#             color: black;
#             height: 100px; /* Hauteur fixe pour un alignement parfait */
#             display: flex;
#             flex-direction: column;
#             justify-content: space-around;
#         }
#         .card-title {
#             font-size: 0.9rem;
#             color: #555;
#             font-weight: bold;
#         }
#         .card-value {
#             font-size: 2.5rem;
#             font-weight: bold;
#             color: #013447;
#             text-align: center;
#         }
#     </style>
#     """, unsafe_allow_html=True)
    
#     # --- 2. Calcul de tous les KPIs ---
#     TMO = agg_global["Temps Moyen d'Operation (MIN)"].mean() if not agg_global.empty else 0
#     TMA = agg_global["Temps Moyen d'Attente (MIN)"].mean() if not agg_global.empty else 0
#     NMC = agg_global['Total Tickets'].sum() if not agg_global.empty else 0
    
#     kpi_rh = df_all_filtered.groupby("NomService")["UserName"].nunique().reset_index().rename(columns={"UserName": "Nombre_Agents"})

#     # --- 3. Affichage de TOUS les KPIs dans une seule grille ---
    
#     # Créer une liste de tous les KPIs à afficher
#     kpi_list = [
#         {"label": "Temps Moyen d'Opération (MIN)", "value": f"{TMO:.0f}"},
#         {"label": "Temps Moyen d'Attente (MIN)", "value": f"{TMA:.0f}"},
#         {"label": "Nombre Total de Clients", "value": f"{NMC:,.0f}"},
#     ]

#     # Ajouter dynamiquement les KPIs par service
#     for _, row in kpi_rh.iterrows():
#         kpi_list.append({
#             "label": f"Agents \"{row['NomService']}\"",
#             "value": row['Nombre_Agents']
#         })

#     # Définir le nombre de colonnes pour la grille
#     num_cols = 3 # Vous pouvez changer ceci (ex: 4)
    
#     # Créer les colonnes et remplir les cartes
#     cols = st.columns(num_cols)
#     for i, kpi in enumerate(kpi_list):
#         col_index = i % num_cols
#         with cols[col_index]:
#             st.markdown(f"""
#                 <div class="custom-card">
#                     <div class="card-title">{kpi['label']}</div>
#                     <div class="card-value">{kpi['value']}</div>
#                 </div>
#             """, unsafe_allow_html=True)

#     #st.markdown("<hr>", unsafe_allow_html=True)
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

    #st.markdown("<hr>", unsafe_allow_html=True)
      



# --- NOUVELLES FONCTIONS DE RENDU POUR L'ANALYSE PAR AGENCE ---

def render_agency_analysis_performance_section(df_all):
    
    st.markdown('<div id="analyse_agence_performance"></div>', unsafe_allow_html=True)
    title=SECTIONS["analyse_agence_performance"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st_echarts(options=stacked_chart2(df_all, 'TempsAttenteReel', 'NomAgence', "Catégorisation du Temps d'Attente"), height="600px")
    with c2:
        st_echarts(options=stacked_chart2(df_all, 'TempOperation', 'NomAgence', "Catégorisation du Temps des Opérations"), height="600px")
    #st.markdown("<hr>", unsafe_allow_html=True)

# Dans votre fichier principal tv_dashboard.py

def render_agency_analysis_frequentation_section(df_all, df_queue):
    st.markdown('<div id="analyse_agence_frequentation"></div>', unsafe_allow_html=True)
    title = SECTIONS["analyse_agence_frequentation"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    
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
        
    #st.markdown("<hr>", unsafe_allow_html=True)

def render_service_analysis_section(df_all, df_queue):
    st.markdown('<div id="analyse_service"></div>', unsafe_allow_html=True)
    title=SECTIONS["analyse_service"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    col1, col2= st.columns(2)
    with col1:
        st_echarts(options=GraphsGlob2(df_all, "Temps Moyen par Service"), height="600px")
    with col2:
        st_echarts(options=Top10_Type(df_queue, title="Top 10 Opérations"), height="600px")
    
    #st.markdown("<hr>", unsafe_allow_html=True)

# --- NOUVELLES FONCTIONS DE RENDU POUR LA PERFORMANCE DES AGENTS ---

def render_agent_performance_volume_temps_section(df_all):
    st.markdown('<div id="performance_agent_volume_temps"></div>', unsafe_allow_html=True)
    title=SECTIONS["performance_agent_volume_temps"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st_echarts(options=create_pie_chart2(df_all, title='Traitée'), height="600px", key='pie_agent')
    with c2:
        st_echarts(options=create_bar_chart2(df_all, status='Traitée'), height="600px", key="bar_agent")
    #st.markdown("<hr>", unsafe_allow_html=True)

def render_agent_performance_evolution_categorie_section(df_all):
    st.markdown('<div id="performance_agent_evolution_categorie"></div>', unsafe_allow_html=True)
    title=SECTIONS["performance_agent_evolution_categorie"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_line_chart(df_all), use_container_width=True)
    with c2:
        st_echarts(options=stacked_chart2(df_all, 'TempOperation', 'UserName', titre="Opérations par Catégorie"), height="600px")
    #st.markdown("<hr>", unsafe_allow_html=True)

def render_wait_time_analysis_section(df_queue, **kwargs):
    st.markdown('<div id="analyse_attente_hebdomadaire"></div>', unsafe_allow_html=True)
    title=SECTIONS["analyse_attente_hebdomadaire"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)

    # --- 1. Préparation des données ---
    # --- Préparation des données (inchangée) ---
    rapport_pd = run_analysis_pipeline(df_queue, filtrer_semaine=False)
    
    if rapport_pd.empty:
        st.warning("Aucune donnée d'attente disponible pour aujourd'hui.")
        #st.markdown("<hr>", unsafe_allow_html=True)
        return
        
    rapport_pd = rapport_pd[rapport_pd['Heure'] <= pd.Timestamp.now()].copy()

   
    
    rapport_pd['heure_creneau'] = rapport_pd['Heure'].dt.strftime('%H:00')
    heatmap_data_agg = rapport_pd.groupby(['NomAgence', 'heure_creneau'])['nb_attente'].mean().reset_index()
    heatmap_pivot = heatmap_data_agg.pivot(index='NomAgence', columns='heure_creneau', values='nb_attente')
    all_hours = [f"{h:02d}:00" for h in range(7, 19)]
    heatmap_pivot = heatmap_pivot.reindex(columns=all_hours, fill_value=0)
    
    heatmap_echarts_data = []
    agences_list = heatmap_pivot.index.tolist()
    heures_list = heatmap_pivot.columns.tolist()
    
    for y, agence in enumerate(agences_list):
        for x, heure in enumerate(heures_list):
            valeur = float(heatmap_pivot.loc[agence, heure])
            heatmap_echarts_data.append([x, y, round(valeur, 1)])
    
    max_val = float(heatmap_data_agg['nb_attente'].max()) if not heatmap_data_agg.empty else 10.0
    
    # --- Configuration ECharts ---
    options_heatmap = {'title': {"text": "Heatmap de l'Attente Moyenne par Agence et Heure", "left": "center"},"backgroundColor": BackgroundGraphicColor,
        "tooltip": {"position": "top"},
        "grid": {"height": "80%", "top": "5%", "left": "15%", "right": "10%"}, # Ajuster les marges pour laisser de la place
        
        "xAxis": {
            "type": "category",
            "data": heures_list,
            "splitArea": {"show": True},
            "axisLabel": {
            "fontWeight": "bold",  # Met les étiquettes de l'axe X en gras
            "color": 'black'
        }
            
        },
        
        "yAxis": {
            "type": "category",
            "data": agences_list,
            "splitLine": {
                "show": True,
                "lineStyle": {"color": '#ccc', "width": 1, "type": 'solid'}
            },
            "axisLabel": {
            "fontWeight": "bold" ,
              "color": 'black'# Met les étiquettes de l'axe X en gras
        }
        },
        
        # --- DÉBUT DE LA CORRECTION ---
        "visualMap": {
            "min": 0, 
            "max": max_val, 
            "calculable": True,
            "orient": "vertical",  # Changer l'orientation en vertical
            "left": "right",        # Placer à gauche
            "top": "center",       # Centrer verticalement
            "inRange": {"color": ['#FFFFFF', '#E0F3F8', '#ABD9E9', '#74ADD1', '#4575B4', '#FEE090', '#FDAE61', '#F46D43', '#D73027', '#A50026']}
        },
        # --- FIN DE LA CORRECTION ---
        
        "series": [{
            "name": "Attente Moyenne", "type": "heatmap", "data": heatmap_echarts_data,
            "label": {"show": True, "formatter": '{@[2]}', "color": "#000"},
            "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0, 0, 0, 0.5)"}}
        }]
    }
    st_echarts(options=options_heatmap, height="700px") # Augmenté la hauteur pour une meilleure visibilité

    #st.markdown("<hr>", unsafe_allow_html=True)


def render_supervision_offline_section(df_queue, df_agencies_regions, **kwargs):
    """
    Affiche les agences HORS LIGNE sous forme de cartes paginées,
    en imitant la logique et le format de la section de monitoring.
    
    Retourne le nombre total de pages pour cette section.
    """
    # Ancre HTML pour le défilement
    st.markdown('<div id="supervision_offline"></div>', unsafe_allow_html=True)

    # --- 1. GESTION DE LA PAGE ACTUELLE (avec sa propre clé de session) ---
    if 'offline_page_index' not in st.session_state:
        st.session_state.offline_page_index = 0
    page_index = st.session_state.offline_page_index

    # --- 2. PARAMÈTRES DE LA PAGINATION (identiques au monitoring) ---
    ITEMS_PER_PAGE = 12
    NUM_COLS = 4

    # --- 3. IDENTIFICATION DES AGENCES HORS LIGNE (Logique Robuste) ---
    online_agencies_in_period = set(df_queue['NomAgence'].unique())
    # On récupère la liste maîtresse de toutes les agences connues
    all_known_agencies = set(df_agencies_regions['NomAgence'].dropna().unique())

    # Les agences hors ligne sont celles de la liste maîtresse qui ne sont pas dans la liste en ligne
    offline_agency_names = sorted(list(all_known_agencies - online_agencies_in_period))
    
    # On filtre le dataframe pour ne garder que les informations des agences hors ligne
    offline_agencies_df = df_agencies_regions[df_agencies_regions['NomAgence'].isin(offline_agency_names)].copy()
    offline_agencies_df = offline_agencies_df.sort_values(by=["Region", "NomAgence"])
    
    total_offline_agencies = len(offline_agencies_df)

    # Calculer le nombre total de pages
    num_pages = math.ceil(total_offline_agencies / ITEMS_PER_PAGE) if total_offline_agencies > 0 else 1

    # --- 4. AFFICHAGE DU TITRE DYNAMIQUE ---
    title = SECTIONS["supervision_offline"]['title']
    t=f"{title} (Page {page_index + 1}/{num_pages})"
    st.markdown(f"<h1 style='text-align: center;'>{t}</h1>", unsafe_allow_html=True)

    if offline_agencies_df.empty:
        st.success("Toutes les agences connues ont rapporté des données sur cette période.")
        st.markdown("<hr>", unsafe_allow_html=True)
        return 1 # Il y a une seule page "vide"

    # --- 5. SÉLECTION DES AGENCES POUR LA PAGE ACTUELLE ---
    agencies_to_display = offline_agencies_df.iloc[page_index * ITEMS_PER_PAGE : (page_index + 1) * ITEMS_PER_PAGE]

    # --- 6. INJECTION DU CSS (on réutilise les classes du monitoring) ---
    try:
        with open("led.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Le fichier 'led.css' est manquant.")
        
    st.markdown("""
        <style>
            .metric-card {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 1rem;
                text-align: center;
                height: 100%;
            }
            .metric-label {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                font-size: 1.1em;
                font-weight: bold;
                margin-bottom: 0.5rem;
            }
            .metric-value {
                font-size: 2.8em;
                font-weight: bold;
                color: #013447;
                line-height: 1.2;
            }
            .metric-delta {
                font-size: 0.9em;
                color: #555;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)
    # --- 7. AFFICHAGE DE LA GRILLE DE CARTES HORS LIGNE ---
    for i in range(0, len(agencies_to_display), NUM_COLS):
        cols = st.columns(NUM_COLS, gap="large")
        # On prend une "tranche" du DataFrame pour la ligne actuelle.
        row_agencies_df = agencies_to_display.iloc[i : i + NUM_COLS]
        
        # --- LA CORRECTION EST ICI ---
        # On utilise enumerate pour avoir un index local 'j' (0, 1, 2, 3, 4) pour les colonnes.
        for j, (index, agence_data) in enumerate(row_agencies_df.iterrows()):
            
            # On assigne la carte à la bonne colonne en utilisant l'index local 'j'.
            with cols[j]:
                nom_agence = agence_data['NomAgence']
                region = agence_data.get('Region', 'N/A')
                
                # Le code Markdown pour la carte reste identique.
                st.markdown(f"""
                    <div class="metric-card" style="background-color: #FEF2F2; border: 1px solid #F87171;">
                        <div class="metric-label">
                            <span class="status-led red"></span>
                            <span>{nom_agence}</span>
                        </div>
                        <div class="metric-value" style="font-size: 1.8em; color: #DC2626; line-height: 1.2;">
                            Hors Ligne
                        </div>
                        <div class="metric-delta" style="margin-top: 0.5rem;">
                            Région: {region}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # --- 8. RETOUR DE L'INFORMATION CRUCIALE ---
    # On retourne le nombre total de pages au "cerveau" de défilement.
    return num_pages


def render_supervision_monitoring_section(df_all, df_queue, df_agencies_regions, **kwargs):
    """
    Affiche la grille de supervision avec une pagination interne gérée par session_state.
    
    Cette fonction est conçue pour être "pilotée" par une boucle de défilement externe :
    - Elle affiche la page de cartes correspondant à l'index stocké dans st.session_state.
    - Elle retourne le nombre total de pages calculé pour que le pilote sache quoi faire.
    """
    # Ancre HTML pour que le défilement principal puisse cibler cette section
    st.markdown('<div id="supervision_monitoring"></div>', unsafe_allow_html=True)

    # --- 1. GESTION DE LA PAGE ACTUELLE ---
    # On utilise st.session_state pour mémoriser la page affichée entre chaque rafraîchissement
    if 'monitoring_page_index' not in st.session_state:
        st.session_state.monitoring_page_index = 0
    page_index = st.session_state.monitoring_page_index

    # --- 2. PARAMÈTRES DE LA PAGINATION ---
    # Affiche 3 lignes de 5 agences, soit 15 par "diapositive"
    ITEMS_PER_PAGE = 12 
    NUM_COLS = 4

    # --- 3. PRÉPARATION DES DONNÉES ---
    _, agg_global = AgenceTable(df_all, df_queue)
    agg_global_filtered = agg_global[agg_global["Nom d'Agence"].isin(st.session_state.selected_agencies)]
    agg_global_sorted = agg_global_filtered.sort_values(by='Nbs de Clients en Attente', ascending=False)
    
    online_agencies = agg_global_sorted["Nom d'Agence"].unique().tolist()
    total_online_agencies = len(online_agencies)
    
    # Calculer le nombre total de pages nécessaires pour afficher toutes les agences
    num_pages = math.ceil(total_online_agencies / ITEMS_PER_PAGE) if total_online_agencies > 0 else 1

    # --- 4. AFFICHAGE DU TITRE DYNAMIQUE ---
    title = SECTIONS["supervision_monitoring"]['title']
    t=f"{title} (Page {page_index + 1}/{num_pages})"
    st.markdown(f"<h1 style='text-align: center;'>{t}</h1>", unsafe_allow_html=True)
    # st.header(f"{title} (Page {page_index + 1}/{num_pages})")

    # Cas où il n'y a aucune agence à afficher
    if not online_agencies:
        st.info("Aucune agence en ligne à afficher pour les filtres sélectionnés.")
        #st.markdown("<hr>", unsafe_allow_html=True)
        # On retourne 1 car il y a techniquement une page (vide) à afficher
        return 1

    # --- 5. SÉLECTION DES AGENCES POUR LA PAGE ACTUELLE ---
    # C'est ici que la pagination a lieu : on ne prend qu'un "morceau" de la liste
    start_index = page_index * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    agencies_to_display = online_agencies[start_index:end_index]

    # --- 6. INJECTION DU CSS POUR LES CARTES ET LES LEDS ---
    try:
        with open("led.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Le fichier 'led.css' est manquant.")
        
    st.markdown("""
        <style>
            .metric-card {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 1rem;
                text-align: center;
                height: 100%;
            }
            .metric-label {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                font-size: 1.1em;
                font-weight: bold;
                margin-bottom: 0.5rem;
            }
            .metric-value {
                font-size: 2.8em;
                font-weight: bold;
                color: #013447;
                line-height: 1.2;
            }
            .metric-delta {
                font-size: 0.9em;
                color: #555;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- 7. AFFICHAGE DE LA GRILLE POUR LA PAGE SÉLECTIONNÉE ---
    for i in range(0, len(agencies_to_display), NUM_COLS):
        cols = st.columns(NUM_COLS, gap="large")
        # On itère sur le sous-ensemble `agencies_to_display`, pas sur la liste complète
        row_agencies = agencies_to_display[i:i + NUM_COLS]
        
        for j, nom_agence in enumerate(row_agencies):
            with cols[j]:
                agence_data = agg_global_sorted[agg_global_sorted["Nom d'Agence"] == nom_agence]
                
                if not agence_data.empty:
                    max_cap = int(agence_data['Capacité'].values[0])
                    queue_now = agence_data['Nbs de Clients en Attente'].values[0]
                    status_class = get_status_info(queue_now, capacite=max_cap)
                    
                    services_html = " | ".join([
                        f"{s}: {current_attente(df_queue[(df_queue['NomAgence'] == nom_agence) & (df_queue['NomService'] == s)], nom_agence)}" 
                        for s in df_queue[df_queue['NomAgence'] == nom_agence]['NomService'].unique()
                    ])
                if not agence_data.empty:
                    max_cap = int(agence_data['Capacité'].values[0])
                    queue_now = agence_data['Nbs de Clients en Attente'].values[0]
                    # La fonction get_status_info est supposée exister dans votre code
                    status_class = get_status_info(queue_now, capacite=max_cap)
                    
                    # Construction de la carte-métrique
                    st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">
                                    <span class="status-led {status_class}"></span>
                                    <span>{nom_agence}</span>
                                </div>
                                <div class="metric-value">{queue_now}</div>
                                <div class="metric-delta">Capacité: {max_cap}</div>
                                <div class="metric-delta">{services_html or "Aucun service actif"}</div>
                            </div>
                        """, unsafe_allow_html=True)

    #st.markdown("<hr>", unsafe_allow_html=True)

    # --- 8. RETOUR DE L'INFORMATION CRUCIALE ---
    # On retourne le nombre total de pages au "cerveau" (render_scrolling_dashboard)
    return num_pages

    
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
    #st.markdown("<hr>", unsafe_allow_html=True)

def render_end_section():
    st.markdown('<div id="fin_de_cycle"></div>', unsafe_allow_html=True)
    title=SECTIONS["fin_de_cycle"]['title']
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
    st.success("Le défilement va redémarrer depuis le début...")

# --- 5. INTERFACE ET LOGIQUE PRINCIPALE ---

def render_configuration_page():
    st.title("Configuration du Défilement TV")
    
    _, col_logout = st.columns([0.9, 0.1])
    with col_logout:
        if st.button("🔴Déconnection", help="Se déconnecter"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    st.info(f"Le tableau de bord affichera automatiquement les données pour aujourd'hui : **{datetime.now().strftime('%d %B %Y')}**.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.header("Durée du Défilement")
        st.session_state.scroll_duration = st.number_input(
            "Temps de visualisation par section (secondes)", 
            min_value=5, 
            value=st.session_state.get('scroll_duration', 15), 
            step=1,
            label_visibility="collapsed"
        )

    with col2:
        st.header("Sections à Inclure")
        with st.container(height=400):
            if not st.session_state.section_config:
                st.session_state.section_config = {sec_id: {'enabled': True} for sec_id in SECTIONS}
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
        st.session_state.display_state = 'show_content' # Important de réinitialiser
        st.rerun()
        
    st.markdown("</div>", unsafe_allow_html=True)
        
    # Charger les données UNIQUEMENT pour la journée en cours
    debut =datetime.strptime('2025-10-31', '%Y-%m-%d')
    today = datetime.now().date()
    with st.spinner(f"Chargement des données ..."):
        df_all, df_queue = load_all_data(debut, today)
        
        # Si aucune donnée n'est trouvée pour aujourd'hui, on arrête
        if df_all.empty:
            st.error(f"Aucune donnée disponible pour aujourd'hui ({today.strftime('%d/%m/%Y')}). Le tableau de bord ne peut pas démarrer.")
            st.stop()
            
        # Le filtrage n'est plus nécessaire, on utilise toutes les données chargées
        df_all_filtered = df_all
        df_queue_filtered = df_queue
        
        # Mettre à jour la liste des agences pour les autres fonctions si besoin
        st.session_state.selected_agencies = df_queue_filtered['NomAgence'].unique().tolist()
        
        _, agence_global, _, _ = AgenceTable2(df_all_filtered, df_queue_filtered)
    

    # --- CRÉATION DU CONTENEUR TAMPON ---
    # On crée UN SEUL espace réservé au début.
    placeholder = st.empty()
    # Dictionnaire des fonctions de rendu (inchangé)
    render_functions = {
        "kpis_et_carte": (render_kpis_and_map_section,  {'agg_global': agence_global, 'df_all_filtered': df_all_filtered}),
        "top_sevice": (render_top_sevice, {'df_all': df_all_filtered}),
        "analyse_agence_performance": (render_agency_analysis_performance_section, {'df_all': df_all_filtered}),
        "analyse_agence_frequentation": (render_agency_analysis_frequentation_section, {'df_all': df_all_filtered, 'df_queue': df_queue_filtered}),
        "analyse_service": (render_service_analysis_section, {'df_all': df_all_filtered, 'df_queue': df_queue_filtered}),
        "performance_agent_volume_temps": (render_agent_performance_volume_temps_section, {'df_all': df_all_filtered}),
        "performance_agent_evolution_categorie": (render_agent_performance_evolution_categorie_section, {'df_all': df_all_filtered}),
        "analyse_attente_hebdomadaire": (render_wait_time_analysis_section, {'df_queue': df_queue_filtered}),
        "supervision_monitoring": (render_supervision_monitoring_section, {'df_all': df_all_filtered, 'df_queue': df_queue_filtered, 'df_agencies_regions': load_agencies_regions_info()}),
        "supervision_offline": (render_supervision_offline_section, {'df_queue': df_queue_filtered, 'df_agencies_regions': load_agencies_regions_info()}),
        # "fin_de_cycle": (render_end_section, {}),
    }

    enabled_anchors = [sec_id for sec_id, config in st.session_state.section_config.items() if config['enabled']]
    
    # 1. On détermine quelle est la SEULE section à afficher
    # 1. Déterminer quelle section afficher
    current_anchor_id = enabled_anchors[st.session_state.current_section_index]
    
    # 2. Utiliser le conteneur pour afficher la section
    # À chaque rerun, le placeholder est d'abord vidé avant d'être rempli.
    if st.session_state.display_state == 'show_content':
        
        # 1. On affiche la section actuelle dans le placeholder
        with placeholder.container():
            current_anchor_id = enabled_anchors[st.session_state.current_section_index]
            func, kwargs = render_functions[current_anchor_id]
            
            # La logique de rendu et de pagination du monitoring reste la même
            total_pages_monitoring = 1
            if current_anchor_id == "supervision_monitoring":
                total_pages_monitoring = func(**kwargs)
            else:
                func(**kwargs)

        # 2. On attend la durée de visualisation
        time.sleep(st.session_state.get('scroll_duration', 15))

        # 3. ON PRÉPARE LE PASSAGE À LA SECTION SUIVANTE (logique inchangée)
        current_anchor_id = enabled_anchors[st.session_state.current_section_index]
        if current_anchor_id == "supervision_monitoring":
            is_last_page = (st.session_state.monitoring_page_index >= total_pages_monitoring - 1)
            if is_last_page:
                st.session_state.current_section_index = (st.session_state.current_section_index + 1) % len(enabled_anchors)
                st.session_state.monitoring_page_index = 0
            else:
                st.session_state.monitoring_page_index += 1
        else:
            st.session_state.current_section_index = (st.session_state.current_section_index + 1) % len(enabled_anchors)

        # 4. On bascule vers l'état "Nettoyage" pour le prochain rafraîchissement
        st.session_state.display_state = 'clearing'
        st.rerun()

    # --- ÉTAPE B : Si on est en phase de nettoyage ---
    elif st.session_state.display_state == 'clearing':
        
        # 1. On vide explicitement le placeholder. C'est l'étape de "l'ardoise propre".
        placeholder.empty()

        # 2. On attend une fraction de seconde, juste assez pour que le navigateur traite le vidage.
        time.sleep(0.1) # 100 millisecondes

        # 3. On re-bascule vers l'état "Affichage" pour le prochain rafraîchissement
        st.session_state.display_state = 'show_content'
        st.rerun()
# --- 6. ROUTEUR PRINCIPAL DE L'APPLICATION ---


def show_login_page():
    # --- NOUVEAU : Créer des colonnes pour centrer le contenu ---
    # Nous créons 3 colonnes, la colonne du milieu sera plus large
    # Les colonnes latérales vides serviront de marges.
    col1, col2, col3 = st.columns([1, 1.5, 1])

    # Tout le contenu de la page de connexion ira dans la colonne du milieu
    with col2:
    
        
    
        
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


# Charger les CSS de base une seule fois au début
load_base_css()

if not st.session_state.logged_in:
    show_login_page()

elif st.session_state.view_mode == 'config':
    # Le mode config est une page standard
    render_configuration_page()

else: # view_mode == 'dashboard'
    # Le mode dashboard active le CSS plein écran et le défilement
    
    render_scrolling_dashboard()