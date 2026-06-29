# pages/2_📍_Congestion_et_Carte.py
import streamlit as st
from shared_code import *

# Mettre le minuteur en place dès le début de la page
setup_auto_refresh(interval_minutes=1)

st.markdown("<h1 style='text-align: center;'>Congestion et Localisation des Agences</h1>", unsafe_allow_html=True)

load_and_display_css()

if not st.session_state.get('logged_in'):
    st.error("Veuillez vous connecter pour accéder à cette page.")
    st.stop()

# --- Dessine la sidebar et charge les données (via API) ---
create_sidebar_filters()
df       = st.session_state.df_main.copy()
df_all   = df[df['UserName'].notna()].reset_index(drop=True)
df_queue = df.copy()

# --- Filtrage basé sur st.session_state ---
df_all_filtered = df_all[df_all['NomAgence'].isin(st.session_state.selected_agencies)]
df_queue_filtered = df_queue[df_queue['NomAgence'].isin(st.session_state.selected_agencies)]

if df_all_filtered.empty:
    st.warning("Aucune donnée disponible pour la période et les agences sélectionnées.")
    st.stop()

# --- KPIs ---
_, agg_global = AgenceTable(df_all_filtered, df_queue_filtered)
agg_global = agg_global[agg_global["Nom d'Agence"].isin(st.session_state.selected_agencies)]

Temps_Moyen_Operation=df_all_filtered[['TempOperation']].apply(lambda x: np.mean(x) / 60).values[0]

Temps_Moyen_Attente=df_queue_filtered[['TempsAttenteReel']].apply(lambda x: np.mean(x) / 60).values[0]

#Temps_Moyen_Attente=('TempsAttenteReel', lambda x: np.mean(x) / 60),

TMO = round(Temps_Moyen_Operation) #agg_global["Temps Moyen d'Operation (MIN)"].sum()/len(agg_global)
TMA = round(Temps_Moyen_Attente) #agg_global["Temps Moyen d'Attente (MIN)"].sum()/len(agg_global)

NMC = agg_global['Total Tickets'].sum()

c1, c2, c3 = st.columns(3)
c1.metric("Temps Moyen d'Opération (MIN)", f"{TMO:.0f}")
c2.metric("Temps Moyen d'Attente (MIN)", f"{TMA:.0f}")
c3.metric("Nombre Total de Clients", f"{NMC:.0f}")

st.divider()

# --- Section Congestion ---
c1, c2 = st.columns([1, 2])

agg_map = agg_global.rename(columns={
    "Nom d'Agence":'NomAgence', 'Capacité':'Capacites', 
    "Temps Moyen d'Operation (MIN)":'Temps_Moyen_Operation',
    "Temps Moyen d'Attente (MIN)":'Temps_Moyen_Attente',
    'Total Traités':'NombreTraites', 'Total Tickets':'NombreTickets',
    'Nbs de Clients en Attente':'AttenteActuel'
})

with c1:
    
    st.markdown("""
<p style="font-size: 14px; text-align: center; color: black;">
    CONGESTION PAR AGENCE
</p>
""", unsafe_allow_html=True)
    agence_options = agg_map['NomAgence'].unique()
    if len(agence_options) > 0:
        selected_agence_gauge = st.selectbox(
            "Choisir une agence",
            options=agence_options,
            label_visibility="collapsed"
        )
        
        agence_data = agg_map[agg_map['NomAgence'] == selected_agence_gauge]
        if not agence_data.empty:
            # Privilégier les données temps réel (Firebase) pour la jauge
            _rt = st.session_state.get('agencies_realtime', pd.DataFrame())
            _rt_row = _rt[_rt['NomAgence'] == selected_agence_gauge] if not _rt.empty else pd.DataFrame()
            if not _rt_row.empty:
                queue_length = int(_rt_row['ClientsEnAttente'].values[0])
                max_length   = int(_rt_row['Capacites'].values[0])
            else:
                queue_length = agence_data['AttenteActuel'].values[0]
                max_length   = agence_data['Capacites'].values[0]
            echarts_satisfaction_gauge(queue_length, max_length=max_length, title="Clients en Attente")

            # Répartition par service — source : attenteParService du realtime (temps réel)
            # Fallback sur current_attente() si le champ est absent
            attente_par_service = {}
            if not _rt_row.empty and "AttenteParService" in _rt_row.columns:
                raw = _rt_row["AttenteParService"].values[0]
                if isinstance(raw, list) and len(raw) > 0:
                    attente_par_service = {s["nomService"]: s["clientsEnAttente"] for s in raw}

            if not attente_par_service:
                # Fallback : calcul depuis df_main (cache 30 min)
                HeureFermeture = df_queue['HeureFermeture'].iloc[0]
                nomService = list(df_queue_filtered['NomService'].unique())
                attente_par_service = {
                    s: current_attente(df_queue[df_queue['NomService'] == s], selected_agence_gauge, HeureFermeture)
                    for s in nomService
                }

            if attente_par_service:
                c = c1.columns(len(attente_par_service))
                for i, (nom, val) in enumerate(attente_par_service.items()):
                    c[i].metric(label=nom, value=int(val))
with c2:
    st.markdown("""
<p style="font-size: 14px; text-align: center; color: black;">
    CARTE DES AGENCES
</p>
""", unsafe_allow_html=True)
    
    folium_map=create_folium_map(agg_map)
    # folium_map.save('map.html')
    # #@st.cache_data()
    # def get_golden_map():
    #     HtmlFile = open("map.html", 'r', encoding='utf-8')
    #     bcn_map_html = HtmlFile.read()
    #     return bcn_map_html
    # bcn_map_html = get_golden_map()
    with st.container():
        html(folium_map, height=450)