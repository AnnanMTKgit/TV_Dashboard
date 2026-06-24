# pages/8_Analyse_d'activite.py
import streamlit as st
from shared_code import *

# Mettre le minuteur en place dès le début de la page
setup_auto_refresh(interval_minutes=10)

st.markdown("<h1 style='text-align: center;font-size:1.5em;'>Vue d'analyse : Tendance Hebdomadaire Moyenne</h1>", unsafe_allow_html=True)
st.markdown(""" <style>iframe[title="streamlit_echarts.st_echarts"]{ height: 500px !important } """, unsafe_allow_html=True)
load_and_display_css()

if not st.session_state.get('logged_in'):
    st.error("Veuillez vous connecter pour accéder à cette page.")
    st.stop()

create_sidebar_filters()
conn = get_connection()
df = run_query(conn, SQLQueries().AllQueueQueries, params=(st.session_state.start_date, st.session_state.end_date))
df_all = df[df['UserName'].notna()].reset_index(drop=True)
df_queue=df.copy()


df_all_filtered = df_all[df_all['NomAgence'].isin(st.session_state.selected_agencies)]
df_queue_filtered = df_queue[df_queue['NomAgence'].isin(st.session_state.selected_agencies)]

if df_all_filtered.empty: 
    st.error("Aucune donnée disponible pour la sélection.")
    st.stop()



# --- FONCTION PRINCIPALE DE LA PAGE ---
def render_activity_page():
    
    
    rapport_pd = run_analysis_pipeline(df_queue_filtered,filtrer_semaine=False)
    if rapport_pd.empty: return
    rapport_pd = rapport_pd[rapport_pd['Heure'] <= pd.Timestamp.now()].copy()
    
    # --- NOUVEAU: Pré-calcul du nombre de jours d'activité ---
    # On normalise pour ne compter que les jours, pas les heures
    jours_activite_par_agence = rapport_pd.groupby('NomAgence')['Heure'].apply(lambda x: x.dt.normalize().nunique())
   
    agences_dispo = sorted(rapport_pd['NomAgence'].unique())
    agence_selectionnee = st.selectbox(
        "**1. Choisissez une agence**",
        options=agences_dispo
    )
    
    if not agence_selectionnee:
        st.info("Veuillez choisir une agence pour commencer l'analyse.")
        return

    df_agence = rapport_pd[rapport_pd['NomAgence'] == agence_selectionnee]

    min_date = df_agence['Heure'].min().normalize()
    max_date = df_agence['Heure'].max().normalize()
    diff_jours = (max_date - min_date).days
    nb_jours_activite = jours_activite_par_agence.get(agence_selectionnee, 0)
    
   

    # --- SECTION DES KPIs ---
    if diff_jours > 0:
        # KPIs pour la vue hebdomadaire
        rapport_moyen = calculer_moyenne_hebdomadaire(df_agence)
        
        # KPIs sur les moyennes (inchangés)
        # Calculs pour les KPIs
        pic_moyen = rapport_moyen['nb_attente_moyen'].max()
        moyenne_globale = df_agence['nb_attente'].mean()
        
        creneau_charge_info = rapport_moyen.loc[rapport_moyen['nb_attente_moyen'].idxmax()]
        jour_charge = creneau_charge_info['Jour_semaine']
        heure_charge = creneau_charge_info['Heure_jour']
        creneau_charge_str = f"{jour_charge[:3].capitalize()} {heure_charge}h"

        # peak_info = df_agence.loc[df_agence['nb_attente'].idxmax()]
        # peak_value = peak_info['nb_attente']
        # peak_timestamp = peak_info['Heure']
        # # Utilisation d'un format plus court pour la date du pic absolu
        # peak_str = peak_timestamp.strftime("%a %d %b à %Hh")

        # NOUVEAU: Disposition à 4 colonnes
        kpi1, kpi2, kpi3= st.columns(3)
        kpi1.metric(
            label="Pic d'Attente Moyen", 
            value=f"{pic_moyen:.0f}",
            help="Le pic le plus élevé de la MOYENNE d'attente pour un créneau (jour de la semaine + heure)."
        )
        kpi2.metric(
            label="Attente Moyenne Globale", 
            value=f"{moyenne_globale:.0f}",
            help="Moyenne de l'attente sur toutes les heures enregistrées dans la période analysée."
        )
        kpi3.metric(
            label="Créneau le Plus Chargé",
            value=creneau_charge_str,
            help="Le créneau (jour + heure) qui a, en moyenne, la plus haute attente."
        )
          
        # kpi4.metric(
        #     label="Pic d'Attente Absolu",
        #     value=f"{int(peak_value)}",
        #     help=f"Le pic le plus élevé jamais atteint, survenu le : {peak_str.capitalize()}"
        # )
    else:
        # KPIs pour la vue journalière (inchangés)
        if not df_agence.empty:
            pic_jour = df_agence['nb_attente'].max()
            moyenne_jour = df_agence['nb_attente'].mean()
            heure_pointe_info = df_agence.loc[df_agence['nb_attente'].idxmax()]
            heure_pointe_str = heure_pointe_info['Heure'].strftime('%H:%M')

            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric(
                label="Attente Maximale", 
                value=int(pic_jour),
                help="Le nombre maximum de personnes en attente atteint à un moment donné de la journée."
            )
            kpi2.metric(
                label="Attente Moyenne", 
                value=f"{moyenne_jour:.0f}",
                help="Moyenne de l'attente calculée sur toutes les heures d'ouverture de la journée."
            )
            kpi3.metric(
                label="Heure de Pointe", 
                value=heure_pointe_str,
                help="L'heure exacte à laquelle le pic d'attente maximal a été enregistré."
            )

    

    # --- SECTION DES VISUALISATIONS (inchangée) ---
    if diff_jours > 0:
        
        #st.markdown(f"<h1 style='text-align: center;font-size:1em;'>Les données s'étalent sur {nb_jours_activite} jour(s) d'activité pendant cette période pour {agence_selectionnee.upper()}</h1>", unsafe_allow_html=True)
       
        
        
        # --- SECTION DES KPIs ---
        # Récupérer la valeur pré-calculée
        
        rapport_moyen = calculer_moyenne_hebdomadaire(df_agence)
        
        tab1, tab2 = st.tabs(["📊 Vue d'Ensemble", "📈 Analyse Horaire Détaillée"])
        with tab1:
            
            
            


            col1, col2 = st.columns(2)
            with col1:
                # --- NOUVEAU: GRAPHIQUE À BARRES DE LA CHARGE JOURNALIÈRE ---
                charge_journaliere_df = calculer_charge_journaliere_moyenne(rapport_moyen)
                
                max_charge = charge_journaliere_df['Charge_Journaliere'].max()
                
                # Préparation des données pour la série, en stylisant la barre max
                bar_data = []
                for _, row in charge_journaliere_df.iterrows():
                    charge_val = row['Charge_Journaliere']
                    item = {"value": round(charge_val, 2)}
                    if charge_val == max_charge:
                        item["itemStyle"] = {"color": "#546E7A"} # Couleur foncée pour le max
                    bar_data.append(item)
                    
                options_bar = {
                    "title": {"text": "Charge Moyenne Totale par Jour de la Semaine", "left": "center"},
                    "backgroundColor":BackgroundGraphicColor,
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "xAxis": {
                        "type": "category",
                        "data": charge_journaliere_df['Jour_semaine'].tolist()
                    },
                    "yAxis": {"type": "value"},
                    "series": [{
                        "name": "Charge Journalière",
                        "type": "bar",
                        "data": bar_data,
                        "itemStyle": {"color": "#6c8dff"} # Couleur par défaut pour les autres barres
                    }]
                }
                st_echarts(options=options_bar, height="400px", key=f"bar_chart_{agence_selectionnee}")


            with col2:
                rapport_moyen = calculer_moyenne_hebdomadaire(df_agence) # S'assurer que les données sont fraîches
                heures_int = [int(h) for h in sorted(rapport_moyen['Heure_jour'].unique())]
                heures_str = [f"{h:02d}h" for h in heures_int]

                jours_ordre_complet = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
                jours_disponibles = rapport_moyen['Jour_semaine'].unique().tolist()
                jours_a_afficher_chrono = [jour for jour in jours_ordre_complet if jour in jours_disponibles]

                # Inversion de l'ordre pour l'affichage sur l'axe Y
                jours_a_afficher_inverse = jours_a_afficher_chrono[::-1]

                # On utilise la liste inversée pour l'index du pivot et l'axe Y du graphique
                heatmap_pivot = rapport_moyen.pivot_table(
                    index='Jour_semaine', columns='Heure_jour', values='nb_attente_moyen'
                ).reindex(index=jours_a_afficher_inverse)

                heatmap_data = []
                for y, jour in enumerate(jours_a_afficher_inverse):
                    for x, heure in enumerate(heures_int):
                        valeur = rapport_moyen[(rapport_moyen['Jour_semaine'] == jour) & (rapport_moyen['Heure_jour'] == heure)]['nb_attente_moyen'].values
                        if len(valeur) > 0:
                            heatmap_data.append([x, y, round(float(valeur[0]), 2)])

                options_heatmap = {
                    "title": {"text": "Heatmap de la Charge Moyenne par Jour et par heure", "left": "center"},
                    "backgroundColor":BackgroundGraphicColor,
                    "tooltip": {"position": "top"},
                    "grid": {"height": "50%", "top": "20%"},
                    "xAxis": {"type": "category", "data": heures_str, "splitArea": {"show": True}},
                    "yAxis": {"type": "category", "data": jours_a_afficher_inverse, "splitArea": {"show": True}},
                    "visualMap": {
                        "min": float(rapport_moyen['nb_attente_moyen'].min()),
                        "max": float(rapport_moyen['nb_attente_moyen'].max()),
                        "calculable": True, "orient": "horizontal", "left": "center", "bottom": "15%",
                        "inRange": {"color": ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']}
                    },
                    "series": [{"name": "Attente Moyenne", "type": "heatmap", "data": heatmap_data, "label": {"show": True}, "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0, 0, 0, 0.5)"}}}],
                }
                st_echarts(options=options_heatmap, height="400px", key=f"heatmap_{agence_selectionnee}")

       
        with tab2:
            series_line = []
            jours_disponibles = rapport_moyen['Jour_semaine'].unique().tolist()
            
            for jour in jours_disponibles:
                data_jour = rapport_moyen[rapport_moyen['Jour_semaine'] == jour]
                data_map = data_jour.set_index('Heure_jour')['nb_attente_moyen']
                # Utiliser heures_int pour la récupération des données
                series_data = [float(data_map.get(h)) if data_map.get(h) is not None else None for h in heures_int]
                series_line.append({"name": jour, "type": "line", "smooth": True, "data": series_data})

            options_line = {
                "title": {
                    "text": "Tendance Moyenne par Jour de la Semaine",
                    "left": "center"
                },"backgroundColor":BackgroundGraphicColor,
                "tooltip": {"trigger": "axis"},
                "legend": {"data": jours_disponibles,"right":'right'},
                # Utiliser heures_str pour l'affichage de l'axe X
                "xAxis": {"type": "category", "data": heures_str},
                "yAxis": {"type": "value"},
                "series": series_line,
            }
            st_echarts(options=options_line, height="400px", key=f"line_chart_{agence_selectionnee}")

        
        
        


    else:
        # Vue journalière (inchangée)
        #st.markdown(f"<h1 style='text-align: center;font-size:1em;'>Les données s'étalent sur {nb_jours_activite} jour(s) d'activité ( Journée du {min_date.strftime('%Y-%m-%d')}) pendant cette période pour {agence_selectionnee.upper()}</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        
       
        with col1:
            # Préparation des données pour ECharts
            x_axis_data = df_agence['Heure'].dt.strftime('%H:%M').tolist()
            y_axis_data = df_agence['nb_attente'].tolist()

            options_daily = {
                "title": {"text": "Évolution horaire du nombre de Client en attente", "left": "center"},
                "backgroundColor":BackgroundGraphicColor,
                "tooltip": {"trigger": "axis"},
                "toolbox": {"show": True, "feature": {"saveAsImage": {"show": True, "title": "Sauvegarder"}}},
                "xAxis": {"type": "category", "data": x_axis_data},
                "yAxis": {"type": "value"},
                "series": [{
                    "name": "Attente",
                    "type": "line",
                    "smooth": True,
                    "data": y_axis_data
                }]
            }
            st_echarts(options=options_daily, height="400px", key=f"daily_chart_{agence_selectionnee}")
        

        with col2:
        
            
            # Préparation des données pour la heatmap journalière
            df_jour = df_agence.copy()
            df_jour['Heure_jour'] = df_jour['Heure'].dt.hour
            
            heures_int = sorted(df_jour['Heure_jour'].unique())
            heures_str = [f"{h:02d}h" for h in heures_int]
            
            # MODIFICATION 1: Obtenir le nom du jour au lieu de la date
            jours_traduction = {
    'Monday': 'Lundi', 'Tuesday': 'Mardi', 'Wednesday': 'Mercredi',
    'Thursday': 'Jeudi', 'Friday': 'Vendredi', 'Saturday': 'Samedi', 'Sunday': 'Dimanche'
}
            jour_en = min_date.day_name()
            jour_fr = jours_traduction.get(jour_en, jour_en)
            jour_nom = [jour_fr.capitalize()]
            

            heatmap_data = []
            for x, heure in enumerate(heures_int):
                valeur = df_jour[df_jour['Heure_jour'] == heure]['nb_attente'].values
                if len(valeur) > 0:
                    heatmap_data.append([x, 0, int(valeur[0])])
            
            options_heatmap_jour = {
                "title": {"text": "Heatmap de la Journée", "left": "center"},
                "backgroundColor":BackgroundGraphicColor,
                "tooltip": {"position": "top"},
                # MODIFICATION 3: Ajuster la grille pour l'axe Y visible
                "grid": {"height": "25%", "top": "25%", "left": "15%"}, 
                "xAxis": {"type": "category", "data": heures_str},
                # MODIFICATION 2: Afficher l'axe Y avec le nom du jour
                "yAxis": {"type": "category", "data": jour_nom, "show": True},
                "visualMap": {
                    "min": int(df_jour['nb_attente'].min()),
                    "max": int(df_jour['nb_attente'].max()),
                    "calculable": True, "orient": "horizontal", "left": "center", "bottom": "10%",
                },
                "series": [{
                    "name": "Attente", "type": "heatmap", "data": heatmap_data,
                    "label": {"show": True},
                    "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0, 0, 0, 0.5)"}}
                }]
            }
            st_echarts(options=options_heatmap_jour, height="400px", key=f"heatmap_jour_{agence_selectionnee}")

if __name__ == "__main__":
    render_activity_page()