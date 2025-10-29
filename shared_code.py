# shared_code.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import warnings
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
warnings.filterwarnings('ignore')
from streamlit_folium import st_folium 
from streamlit_option_menu import option_menu
from streamlit.components.v1 import html
from streamlit_echarts import st_echarts,JsCode
from streamlit_autorefresh import st_autorefresh
import time
import plotly.graph_objects as go
import pydeck as pdk
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import plotly.io as pio
import copy
import pyodbc
import altair as alt
import seaborn as sns
import plotly.figure_factory as ff
import plotly.subplots as sp
import io 
import folium
from itertools import product
from datetime import datetime, timedelta
from openpyxl.utils import get_column_letter ##
from openpyxl.worksheet.table import Table, TableStyleInfo ##
import base64
import math

# import pyspark
# from pyspark.sql import SparkSession, Window, DataFrame
# from pyspark.sql.functions import col, lit, sum, countDistinct, monotonically_increasing_id
# from pyspark.sql.types import TimestampType
# Variable de couleurs


# --- Configuration Globale du Thème des Graphiques ---
BackgroundGraphicColor = "white"
GraphicPlotColor = "#FFFFFF"
GraphicTitleColor = 'black'
OutsideBarColor = 'black'
InsideBarColor = 'white'

#### COLOR SPECIFIQUE A  ECOBANK###
blue_color="#022737"
green_color="#BBD600"
blue_clair_color= "#1B698D"

# colors=[blue_color,blue_clair_color,green_color,"#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#33FFF0","#FF8333", "#33FF83", "#8C33FF", "#FF3385", "#3385FF",
#     "#FFBD33", "#33FFBD", "#8CFF33", "#FF33B8", "#33FFCC","#B833FF", "#FF336D", "#3385FF", "#FF8333", "#33A1FF","#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#33FFF0",
#     "#FF8333", "#33FF83", "#8C33FF", "#FF3385", "#3385FF","#FFD433", "#33FFD4", "#BD33FF", "#FF33BD", "#33FF99","#FF33B8", "#33A1FF", "#FFBD33", "#33D4FF", "#FF33D4",
#     "#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#33FFF0","#FF8333", "#33FF83", "#8C33FF", "#FF3385", "#3385FF"
# ]

# palette non panacher
palette_colors= ["#022737", "#083A53", "#104D6F", "#17608B", "#1B698D", "#2E86AB", "#4F9DBA", "#70B4C9", "#90CDD8", "#B0E4E7", "#D0FBFB", "#E6FCFC", "#6E7C00", "#879A00", "#A1B800", "#BBD600", "#C7DD2A", "#D3E455", "#E0EC80", "#EDF3AA", "#F6F9D5", "#2F3E46", "#4A5A63", "#65767F", "#80919C", "#9AABB8", "#B5C5D3", "#D0E0EE", "#EBF5FF", "#4C3A5A", "#6D557C", "#8E709E", "#A17FAB", "#B48ECC", "#C29AD4", "#D0A7DC", "#DDA4E3", "#00796B", "#00897B", "#26A69A", "#4DB6AC", "#80CBC4", "#B2DFDB", "#E0F2F1", "#B75D28", "#D18A00", "#E5A000", "#F7B42C", "#FFC954", "#FFDDA1", "#FFECC2", "#D4C5A3", "#E3D5B8", "#F2E5CC", "#C7007D", "#E0409A", "#F97FBA", "#FFAFD8", "#FFD6E9"]
Simple_pallette=[blue_color,blue_clair_color,green_color]
# Palette panacher 
# palette_colors=['#022737', '#BBD600', '#4C3A5A', '#083A53', '#A1B800', '#6D557C', '#104D6F', '#879A00', '#8E709E', '#17608B', '#6E7C00', '#A17FAB', '#1B698D', '#C7DD2A', '#B48ECC', '#2E86AB', '#D3E455', '#C29AD4', '#4F9DBA', '#E0EC80', '#D0A7DC', '#70B4C9', '#EDF3AA', '#DDA4E3', '#90CDD8', '#F6F9D5', '#D0FBFB', '#B0E4E7', '#D18A00', '#EBF5FF', '#2F3E46', '#E5A000', '#D4C5A3', '#4A5A63', '#F7B42C', '#E3D5B8', '#65767F', '#FFC954', '#F2E5CC', '#80919C', '#FFDDA1', '#FFECC2', '#9AABB8', '#C7007D', '#80CBC4', '#B5C5D3', '#E0409A', '#B2DFDB', '#00796B', '#F97FBA', '#E0F2F1', '#00897B', '#FFAFD8', '#90CDD8', '#26A69A', '#FFD6E9', '#B0E4E7', '#4DB6AC', '#B75D28', '#D0FBFB']
data_visualization_colors = [
    "#3498DB",  # Bleu Azur
    "#48C9B0",  # Vert Menthe
    "#013447",  # Corail Doux
    blue_color,  # Orange Safran
    "#8E7CC3",  # Lavande
    "#2A9D8F",  # Vert Marin
    "#F7C181",  # Pêche Claire
    "#5DADE2",  # Bleu Ciel
    blue_clair_color,  # Vieux Rose
    "#AF7AC5",  # Mauve
    green_color,  # Jaune Tournesol
    "#586F7C",  # Gris Ardoise
]


##### Minuteur pour rafraîchir chaque page #####



def setup_auto_refresh(interval_minutes=10):
    
    # L'intervalle est en millisecondes, donc on convertit
    interval_ms = interval_minutes * 60 * 1000
    
    # Exécute le composant d'actualisation automatique
    # La clé (key) est importante pour que Streamlit gère correctement le composant
    st_autorefresh(interval=interval_ms, limit=None, key="auto_refresher")
    #st.toast(f"Page actualisée", icon='🔄')




# --- Classes et Fonctions de Connexion BDD (depuis query.py et sql.py) ---

class SQLQueries:
    def __init__(self):
        # ... (copiez votre classe SQLQueries ici)
        self.AllQueueQueries = f""" SELECT u.FirstName,u.LastName,u.UserName,q.Date_Reservation,q.Date_Appel,q.TempAttenteMoyen,DATEDIFF(second, q.Date_Reservation, q.Date_Appel) as TempsAttenteReel,
    q.Date_Fin,DATEDIFF(second, q.Date_Appel, q.Date_Fin) as TempOperation,q.IsMobile,e.Nom ,s.NomService,t.Label as Type_Operation,r.ReservationParHeure,
    r.AgenceId,a.NomAgence,a.Capacites,a.Longitude,a.Latitude ,a.HeureFermeture, rg.Label Region FROM reservation r LEFT JOIN TypeOperation t ON t.Id=r.TypeOperationId LEFT JOIN queue q ON r.id = q.reservationId
    LEFT JOIN Service s ON r.ServiceId = s.Id LEFT JOIN [User] u ON u.Id = q.userId LEFT JOIN Etat e ON e.Id = q.EtatId LEFT JOIN Agence a ON a.Id = r.AgenceId LEFT JOIN Region rg ON rg.Id=a.RegionId
    WHERE Date_Reservation is not NULL and CAST(q.Date_Reservation AS DATE) BETWEEN CAST(? AS datetime) AND CAST(? AS datetime) 
    ORDER BY q.Date_Reservation DESC; """

        self.ProfilQueries = f"""SELECT
      U.[FirstName]
      ,U.[LastName]
      ,U.[PhoneNumber]
      ,U.[UserName]
      ,U.[Token] as MotDePasse
      ,R.Label as Profil
      ,a.NomAgence
  FROM [User] U  LEFT JOIN [Role] R ON U.[RoleId]= R.Id LEFT JOIN Agence a ON a.Id = U.AgenceId"""
       
        self.RendezVousQueries = f"""SELECT RPH.Id
      ,[HeureReservation]
      ,[NumeroHeureReservation]
      ,[HeureAppel]
      ,[Date_Fin]
      ,[Date_Appel]
      ,[ReservationID]
      ,[userId]
      ,[TempAttenteMoyen]
      ,e.Nom
      ,[IsMobile]
      
  FROM [dbo].[ReservationParHeure] RPH LEFT JOIN Etat e ON e.Id = RPH.EtatId
  WHERE HeureReservation is not NULL and CAST(HeureReservation AS DATE) BETWEEN CAST(? AS datetime) AND CAST(? AS datetime) 
  """ 
        self.AllReseau=f"""SELECT [Id]
      [Label] as Reseau
  FROM [dbo].[Region]"""
        

        self.All_Region_Agences = f"""SELECT
      R.[Label] as Region
      ,A.[NomAgence]
      ,A.[Adresse]
      ,A.[codeAgence]
      ,A.[Pays]
      ,A.[Longitude]
      ,A.[Latitude]
      ,A.[StructureID]
      ,A.[NbClientByDay]
      ,A.[Status]
      ,A.[Capacites]
      ,A.[Telephone]
      ,A.[HeureDemarrage]
      ,A.[HeureFermeture]
      ,A.[SuspensionActivite]
      ,A.[ActivationReservation]
      ,A.[nombreLimitReservation]
  FROM [dbo].[Region] R LEFT JOIN Agence A ON R.Id=A.RegionId"""

def create_excel_buffer(df, sheet_name="Sheet1"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        # Écrire le DataFrame dans Excel
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        worksheet = writer.sheets[sheet_name]

        # Ajuster la largeur des colonnes
        for col_num, column_title in enumerate(df.columns, start=1):
            max_length = max(
                df[column_title].astype(str).map(len).max(),  # Longueur max des données
                len(column_title)  # Longueur du titre de la colonne
            )
            adjusted_width = max_length + 2  # Ajout de marge pour lisibilité
            worksheet.column_dimensions[get_column_letter(col_num)].width = adjusted_width
            
        # Ajouter un style de table
        table = Table(
            displayName="Tableau1",
            ref=worksheet.dimensions  # Dimensions automatiques basées sur les données
        )
        style = TableStyleInfo(
            name="TableStyleMedium9",  # Style prédéfini
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,  # Bandes alternées
            showColumnStripes=False
        )
        table.tableStyleInfo = style
        worksheet.add_table(table)

    # Réinitialiser le pointeur du buffer
    buffer.seek(0)
    return buffer


# Dans shared_code.py


def get_connection():
    """Crée et met en cache la connexion à la base de données."""
    try:
        server = st.secrets['db_server']
        database = st.secrets['db_database']
        username = st.secrets['db_username']
        password = st.secrets['db_password']
        driver_name = st.secrets['db_driver'] # ex: 'ODBC Driver 17 for SQL Server'

        # FORCER le format correct pour le pilote
        # La chaîne de connexion doit avoir DRIVER={Nom du Pilote}
        # et non DRIVER='{Nom du Pilote};...'
        connection_string = (
            f"DRIVER={driver_name};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f'PORT=1433;'
            f"UID={username};"
            f"PWD={password};"
        )
        
        return pyodbc.connect(connection_string)
    
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        st.info("Veuillez vérifier les points suivants :")
        st.markdown("""
            - Le pilote ODBC pour SQL Server est-il bien installé ? (voir `brew install msodbcsql17`)
            - Les informations dans votre fichier `secrets.toml` sont-elles correctes ?
            - Votre Mac est-il connecté à un réseau qui autorise l'accès au serveur de base de données (vérifiez le pare-feu) ?
        """)
        st.stop()

@st.cache_data(hash_funcs={pyodbc.Connection: id}, ttl=3600, show_spinner=False)  # Cache 1h
def run_query_cached(_connection, sql, params):
    """Cache intelligent pour les requêtes lourdes avec TTL de 1h"""
    try:
        # Exécuter la requête et retourner le résultat
        df = pd.read_sql_query(sql, _connection, params=params)
        return df
    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête : {e}")
        return pd.DataFrame() # Retourner un DataFrame vide en cas d'erreur

    

def run_query(_connection, sql, params=None):
    """
    Exécute une requête SQL avec cache intelligent pour optimiser les performances.
    Cache automatiquement les requêtes lourdes (>1 jour de données).
    """
    current_date = datetime.now().date()
    current_hour = datetime.now().hour
    
    # Déterminer si on doit utiliser le cache
    use_cache = False
    if params and len(params) >= 2:
        try:
            start_date = pd.to_datetime(params[0]).date()
            end_date = pd.to_datetime(params[1]).date()
            date_range_days = (end_date - start_date).days
            
            # Utiliser le cache pour les requêtes sur plus d'1 jour OU en dehors des heures de bureau
            use_cache = (date_range_days > 1) or (current_hour < 7 or current_hour >= 18)
        except:
            use_cache = False
    
    if use_cache:
        return run_query_cached(_connection, sql, params)
    else:
        try:
            df = pd.read_sql_query(sql, _connection, params=params)
            return df
        except Exception as e:
            st.error(f"Erreur lors de l'exécution de la requête : {e}")
            return pd.DataFrame()
# --- Fonctions de Traitement de Données (depuis functions.py) ---


def _format_and_finalize_df(df, sort_by, periode_str=None, is_reseau_view=False):
    """Fonction helper pour formater les DataFrames de sortie."""
    if df.empty:
        return pd.DataFrame()

    # 1. Remplacer les NaN par 0
    cols_to_fill = [
        'Temps_Moyen_Operation', 'Temps_Moyen_Attente', 'NombreTraites', 
        'NombreRejetee', 'NombrePassee', 'NombreTickets', 'TotalMobile', 'AttenteActuel',
        'Capacites'
    ]
    for col in cols_to_fill:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # 2. Calculer le temps de passage
    df["Temps Moyen de Passage(MIN)"] = df['Temps_Moyen_Attente'] + df['Temps_Moyen_Operation']
    
    # 3. Définir la période
    if periode_str:
        df["Période"] = periode_str
    else: # Pour les vues mensuelles
        df = df.rename(columns={'Mois': 'Période'})

    # 4. Conversion en entiers
    cols_to_int = [
        'Temps_Moyen_Operation', 'Temps_Moyen_Attente', 'Temps Moyen de Passage(MIN)',
        'NombreTraites', 'NombreRejetee', 'NombrePassee', 'NombreTickets', 'TotalMobile', 
        'AttenteActuel', 'Capacites'
    ]
    for col in cols_to_int:
        if col in df.columns:
            df[col] = np.round(df[col]).astype(int)

    # 5. Renommage des colonnes
    new_name = {
        'NomAgence': "Nom d'Agence",
        'Capacites': 'Capacité',
        'Temps_Moyen_Operation': "Temps Moyen d'Operation (MIN)",
        'Temps_Moyen_Attente': "Temps Moyen d'Attente (MIN)",
        'NombreTraites': 'Total Traités',
        'NombreRejetee': 'Total Rejetées',
        'NombrePassee': 'Total Passées',
        'NombreTickets': 'Total Tickets',
        'AttenteActuel': 'Nbs de Clients en Attente',
        'TotalMobile': 'TotalMobile'
    }
    df = df.rename(columns=new_name)

    # 6. Ordre des colonnes
    base_order = [
        'Période', "Nom d'Agence", 'Region', "Temps Moyen d'Operation (MIN)", 
        "Temps Moyen d'Attente (MIN)", "Temps Moyen de Passage(MIN)", 
        'Capacité', 'Total Tickets', 'Total Traités', 'Total Rejetées', 
        'Total Passées', 'TotalMobile', 'Nbs de Clients en Attente', 
        'Longitude', 'Latitude'
    ]
    if is_reseau_view:
        cols_to_remove = ["Nom d'Agence", 'Longitude', 'Latitude']
        final_order = [col for col in base_order if col not in cols_to_remove]
    else:
        final_order = base_order

    ordered_cols = [col for col in final_order if col in df.columns]
    df = df[ordered_cols]
    
    # 7. Trier les résultats
    df = df.sort_values(by=sort_by).reset_index(drop=True)
    
    return df


def AgenceTable2(df_all, df_queue):
    """
    Calcule 4 tables de performance avec la logique de capacité réseau corrigée.
    """
    try:
        if df_all.empty or df_queue.empty:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        df1 = df_all.copy()
        df2 = df_queue.copy()

        df1['Date_Reservation'] = pd.to_datetime(df1['Date_Reservation'])
        df2['Date_Reservation'] = pd.to_datetime(df2['Date_Reservation'])
        df1['Mois'] = df1['Date_Reservation'].dt.to_period('M').astype(str)
        df2['Mois'] = df2['Date_Reservation'].dt.to_period('M').astype(str)

        # Concaténer les deux dataframes pour avoir une liste complète des agences et de leurs capacités
        df_combined = pd.concat([
            df1[['NomAgence', 'Region', 'Capacites', 'Mois']],
            df2[['NomAgence', 'Region', 'Capacites', 'Mois']]
        ]).drop_duplicates().reset_index(drop=True)

        # ==================== DÉFINITION DES AGRÉGATIONS ====================
        agg_perf = {
            'Temps_Moyen_Operation': ('TempOperation', lambda x: np.mean(x) / 60),
            'Temps_Moyen_Attente': ('TempsAttenteReel', lambda x: np.mean(x) / 60),
            'NombreTraites': ('Nom', lambda x: (x == 'Traitée').sum()),
            'NombreRejetee': ('Nom', lambda x: (x == 'Rejetée').sum()),
            'NombrePassee': ('Nom', lambda x: (x == 'Passée').sum())
        }
        
        agg_queue_agence = {
            'NombreTickets': ('Date_Reservation', 'count'),
            'TotalMobile': ('IsMobile', 'sum')
        }
        
        # Pour le réseau, on ne calcule plus la capacité ici.
        agg_queue_reseau = {
            'NombreTickets': ('Date_Reservation', 'count'),
            'TotalMobile': ('IsMobile', 'sum')
        }

        # ==================== 1. VUE PAR AGENCE (inchangée) ====================
        agg1_mensuel = df1.groupby(['Mois', 'NomAgence', "Region", 'Capacites']).agg(**agg_perf).reset_index()
        agg2_mensuel = df2.groupby(['Mois', 'NomAgence', "Region", 'Capacites', 'Longitude', 'Latitude']).agg(**agg_queue_agence).reset_index()
        agg1_global = df1.groupby(['NomAgence', "Region", 'Capacites']).agg(**agg_perf).reset_index()
        agg2_global = df2.groupby(['NomAgence', "Region", 'Capacites', 'Longitude', 'Latitude']).agg(**agg_queue_agence).reset_index()

        attente_actuelle = [] # ... (logique d'attente actuelle inchangée)
        if attente_actuelle:
            agg2_global = pd.merge(agg2_global, pd.DataFrame(attente_actuelle), on='NomAgence', how='left')
        else:
            agg2_global['AttenteActuel'] = 0

        agence_mensuel = pd.merge(agg2_mensuel, agg1_mensuel, on=['Mois', 'NomAgence', "Region", 'Capacites'], how='outer')
        agence_global = pd.merge(agg2_global, agg1_global, on=['NomAgence', "Region", 'Capacites'], how='outer')

        # ==================== 2. VUE POUR LE RÉSEAU (logique corrigée) ====================
        # Agrégations pour le réseau (tickets, mobiles, temps, statuts...)
        agg1_reseau_mensuel = df1.groupby(['Mois', 'Region']).agg(**agg_perf).reset_index()
        agg2_reseau_mensuel = df2.groupby(['Mois', 'Region']).agg(**agg_queue_reseau).reset_index()
        agg1_reseau_global = df1.groupby(['Region']).agg(**agg_perf).reset_index()
        agg2_reseau_global = df2.groupby(['Region']).agg(**agg_queue_reseau).reset_index()

        # === NOUVELLE LOGIQUE POUR LA CAPACITÉ RÉSEAU ===
        # 1. Obtenir la capacité unique pour chaque agence
        capacites_uniques_par_agence = df_combined[['NomAgence', 'Region', 'Capacites']].drop_duplicates()
        
        # 2. Calculer la capacité totale du réseau (global) par région
        capacite_reseau_global = capacites_uniques_par_agence.groupby('Region')['Capacites'].sum().reset_index()
        
        # 3. Calculer la capacité totale du réseau (mensuel) par mois et par région
        # On ne garde qu'une ligne par mois/agence pour éviter les doublons avant de sommer
        capacites_uniques_par_mois = df_combined[['Mois', 'NomAgence', 'Region', 'Capacites']].drop_duplicates()
        capacite_reseau_mensuel = capacites_uniques_par_mois.groupby(['Mois', 'Region'])['Capacites'].sum().reset_index()

        # Fusion des données de performance et de file d'attente
        reseau_mensuel = pd.merge(agg2_reseau_mensuel, agg1_reseau_mensuel, on=['Mois', 'Region'], how='outer')
        reseau_global = pd.merge(agg2_reseau_global, agg1_reseau_global, on=['Region'], how='outer')

        # Fusion AVEC LA CAPACITÉ CORRECTEMENT CALCULÉE
        reseau_mensuel = pd.merge(reseau_mensuel, capacite_reseau_mensuel, on=['Mois', 'Region'], how='left')
        reseau_global = pd.merge(reseau_global, capacite_reseau_global, on=['Region'], how='left')
        
        # ==================== 3. FORMATAGE FINAL (inchangé) ====================
        all_dates = pd.concat([df1['Date_Reservation'], df2['Date_Reservation']]).dropna()
        periode_globale = f"{all_dates.min().strftime('%Y-%m-%d')} - {all_dates.max().strftime('%Y-%m-%d')}"
        
        agence_mensuel_f = _format_and_finalize_df(agence_mensuel, sort_by=['Période', "Nom d'Agence"])
        agence_global_f = _format_and_finalize_df(agence_global, sort_by=["Nom d'Agence"], periode_str=periode_globale)
        reseau_mensuel_f = _format_and_finalize_df(reseau_mensuel, sort_by=['Période', 'Region'], is_reseau_view=True)
        reseau_global_f = _format_and_finalize_df(reseau_global, sort_by=['Region'], periode_str=periode_globale, is_reseau_view=True)
        
        return agence_mensuel_f, agence_global_f, reseau_mensuel_f, reseau_global_f

    except Exception as e:
        # st.error(f"Erreur dans AgenceTable: {e}")
        print(f"Erreur dans AgenceTable: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()





















def AgenceTable(df_all, df_queue):
    """Version optimisée de AgenceTable pour de gros volumes de données"""
    
    try:
        # Créer des copies pour ne pas modifier les dataframes originaux
        df1 = df_all.copy()
        df2 = df_queue.copy()

        # Vérification des données d'entrée
        if df1.empty and df2.empty:
            return pd.DataFrame(), pd.DataFrame()

        # S'assurer que les colonnes de date sont bien au format datetime
        df1['Date_Reservation'] = pd.to_datetime(df1['Date_Reservation'])
        df2['Date_Reservation'] = pd.to_datetime(df2['Date_Reservation'])
        
        # Pour de gros volumes, on travaille directement sur l'agrégation globale
        # sans passer par l'agrégation journalière qui peut être très lourde
        
        ##### Agrégation Globale Directe ############
        # Agrégation des données de performance (df1)
        agg1_global = df1.groupby(['NomAgence', "Region", 'Capacites']).agg(
            Temps_Moyen_Operation=('TempOperation', lambda x: np.mean(x) / 60),
            Temps_Moyen_Attente=('TempsAttenteReel', lambda x: np.mean(x) / 60),
            NombreTraites=('Nom', lambda x: (x == 'Traitée').sum()),
            NombreRejetee=('Nom', lambda x: (x == 'Rejetée').sum()),
            NombrePassee=('Nom', lambda x: (x == 'Passée').sum())
        ).reset_index()

        # Agrégation des données de queue (df2)
        agg2_global = df2.groupby(['NomAgence', "Region", 'Capacites', 'Longitude', 'Latitude']).agg(
            NombreTickets=('Date_Reservation', 'count'),
            TotalMobile=('IsMobile', 'sum')
        ).reset_index()
        
        # Calculer l'attente actuelle pour chaque agence
        attente_actuelle = []
        for agence in df2['NomAgence'].unique():
            df_agence = df2[df2['NomAgence'] == agence]
            if not df_agence.empty:
                heure_fermeture = df_agence['HeureFermeture'].iloc[0]
                attente = current_attente(df2, agence, heure_fermeture)
                attente_actuelle.append({'NomAgence': agence, 'AttenteActuel': attente})
        
        attente_df = pd.DataFrame(attente_actuelle)
        
        # Fusionner les données d'attente
        if not attente_df.empty:
            agg2_global = pd.merge(agg2_global, attente_df, on='NomAgence', how='left')
        else:
            agg2_global['AttenteActuel'] = 0
        
        # Fusion finale
        globale = pd.merge(agg2_global, agg1_global, on=['NomAgence', "Region", 'Capacites'], how='outer')
        
        # Remplacer les NaN par 0
        cols_to_fill = [
            'Temps_Moyen_Operation', 'Temps_Moyen_Attente', 'NombreTraites', 
            'NombreRejetee', 'NombrePassee', 'NombreTickets', 'TotalMobile', 'AttenteActuel'
        ]
        for col in cols_to_fill:
            if col in globale.columns:
                globale[col] = globale[col].fillna(0)

        # Calculer le temps de passage
        globale["Temps Moyen de Passage(MIN)"] = globale['Temps_Moyen_Attente'] + globale['Temps_Moyen_Operation']
        
        # Définir la période
        if not df_queue.empty:
            globale["Période"] = f"{df_queue['Date_Reservation'].min().strftime('%Y-%m-%d')} - {df_queue['Date_Reservation'].max().strftime('%Y-%m-%d')}"
        else:
            globale["Période"] = "N/A"

        # Conversion en entiers
        cols_to_int = [
            'Temps_Moyen_Operation', 'Temps_Moyen_Attente', 'Temps Moyen de Passage(MIN)',
            'NombreTraites', 'NombreRejetee', 'NombrePassee', 'NombreTickets', 'TotalMobile', 'AttenteActuel'
        ]

        for col in cols_to_int:
            if col in globale.columns:
                globale[col] = np.round(globale[col]).astype(int)

        # Renommage des colonnes
        new_name = {
            'NomAgence': "Nom d'Agence",
            'Capacites': 'Capacité',
            'Temps_Moyen_Operation': "Temps Moyen d'Operation (MIN)",
            'Temps_Moyen_Attente': "Temps Moyen d'Attente (MIN)",
            'NombreTraites': 'Total Traités',
            'NombreRejetee': 'Total Rejetées',
            'NombrePassee': 'Total Passées',
            'NombreTickets': 'Total Tickets',
            'AttenteActuel': 'Nbs de Clients en Attente',
            'TotalMobile': 'TotalMobile'
        }

        globale = globale.rename(columns=new_name)

        # Ordre des colonnes
        order = [
            'Période', "Nom d'Agence", 'Region', "Temps Moyen d'Operation (MIN)", 
            "Temps Moyen d'Attente (MIN)", "Temps Moyen de Passage(MIN)", 
            'Capacité', 'Total Tickets', 'Total Traités', 'Total Rejetées', 
            'Total Passées', 'TotalMobile', 'Nbs de Clients en Attente', 
            'Longitude', 'Latitude'
        ]
        
        globale_order = [col for col in order if col in globale.columns]
        globale = globale[globale_order]
       
        # Pour les gros volumes, on retourne seulement la vue globale
        return pd.DataFrame(), globale
        
    except Exception as e:
        st.error(f"Erreur dans AgenceTable: {e}")
        return pd.DataFrame(), pd.DataFrame()









# def AgenceTable(df_all,df_queue):

#     ########## Journalier ##################
    
#     df1=df_all.copy()
    
    
#     df1['Période'] = df1['Date_Reservation'].dt.date
#     agg1 = df1.groupby(['Période','NomAgence',"Region", 'Capacites']).agg(
#     Temps_Moyen_Operation=('TempOperation', lambda x: np.round(np.mean(x)/60).astype(int)),
#     Temps_Moyen_Attente=('TempsAttenteReel', lambda x: np.round(np.mean(x)/60).astype(int)),NombreTraites=('Nom',lambda x: (x == 'Traitée').sum()),NombreRejetee=('Nom',lambda x: (x == 'Rejetée').sum()),NombrePassee=('Nom',lambda x: (x == 'Passée').sum())
# ).reset_index()
#     agg1["Temps Moyen de Passage(MIN)"]=agg1['Temps_Moyen_Attente']+agg1['Temps_Moyen_Operation']
#     df2=df_queue.copy()
#     df2['Période'] = df2['Date_Reservation'].dt.date
#     agg2=df2.groupby(['Période','NomAgence',"Region", 'Capacites','Longitude','Latitude']).agg(NombreTickets=('Date_Reservation', np.count_nonzero),AttenteActuel=("NomAgence",lambda x: current_attente(df2,agence=x.iloc[0],HeureFermeture=df2[df2['NomAgence']==x.iloc[0]]['HeureFermeture'].values[0])),TotalMobile=('IsMobile',lambda x: int(sum(x)))).reset_index()
    
#     detail=pd.merge(agg2,agg1,on=['Période','NomAgence',"Region", 'Capacites'],how='outer')
    
#     ##### Global ############
#     globale=detail.groupby(['NomAgence',"Region", 'Capacites','Longitude','Latitude']).agg(
#     Temps_Moyen_Operation=('Temps_Moyen_Operation', lambda x: np.round(np.mean(x)).astype(int)),
#     Temps_Moyen_Attente=('Temps_Moyen_Attente', lambda x: np.round(np.mean(x)).astype(int)),NombreTraites=('NombreTraites',lambda x: x.sum()),NombreRejetee=('NombreRejetee',lambda x: x.sum()),NombrePassee=('NombrePassee',lambda x: x.sum()),
#     TMP=("Temps Moyen de Passage(MIN)", lambda x: np.round(np.mean(x)).astype(int)),
# NombreTickets=('NombreTickets', lambda x: np.sum(x)),AttenteActuel=("AttenteActuel",lambda x: x.sum()),TotalMobile=('TotalMobile',lambda x: int(sum(x)))).reset_index()
#     globale["Période"]=f"{df_queue['Date_Reservation'].min().strftime('%Y-%m-%d')} - {df_queue['Date_Reservation'].max().strftime('%Y-%m-%d')}"
#     globale["Temps Moyen de Passage(MIN)"]=globale['Temps_Moyen_Attente']+globale['Temps_Moyen_Operation']
#     ###########
    
#     new_name={'NomAgence':"Nom d'Agence",'Capacites':'Capacité','Temps_Moyen_Operation':"Temps Moyen d'Operation (MIN)",'Temps_Moyen_Attente':"Temps Moyen d'Attente (MIN)",'NombreTraites':'Total Traités','NombreRejetee':'Total Rejetées','NombrePassee':'Total Passées','NombreTickets':'Total Tickets','AttenteActuel':'Nbs de Clients en Attente'}


#     detail=detail.rename(columns=new_name)
#     globale=globale.rename(columns=new_name)
    

#     # order=['Période',"Nom d'Agence", "Temps Moyen d'Operation (MIN)", "Temps Moyen d'Attente (MIN)","Temps Moyen de Passage(MIN)",'Capacité','Total Tickets','Total Traités','Total Rejetées','Total Passées','TotalMobile','Nbs de Clients en Attente','Longitude','Latitude']
#     # detail=detail[order]
#     # globale=globale[order]
  
#     # globale=globale.replace(-9223372036854775808, 0)
#     # detail=detail.replace(-9223372036854775808, 0)
    
   
#     return detail,globale
def current_attente(df_queue,agence,HeureFermeture=None):
    current_date = datetime.now().date()
    current_datetime = datetime.now()
   
# Set the time to 6:00 PM on the same day
    if HeureFermeture==None:
        six_pm_datetime = current_datetime.replace(hour=18, minute=0, second=0, microsecond=0)
    else:
        # List of formats to try, from most to least specific
        formats_to_try = [
            '%Hh%M',    
            '%H:%M',    
            '%H.%M',    
            '%H %M',    
            '%H'       
        ]

        for fmt in formats_to_try:
            try:
                # Try to parse the string with the current format
                time_obj = datetime.strptime(HeureFermeture, fmt).time()
                break
            except ValueError:
                # If it fails, just continue to the next format
                continue
        #time_obj =datetime.strptime(HeureFermeture, "%H:%M").time()

        six_pm_datetime=datetime.combine(current_date, time_obj)

    if current_datetime > six_pm_datetime:
    
        return 0
    else:
        var='En attente'
        
        df = df_queue.query(
        f"(Nom == @var) & (Date_Reservation.dt.strftime('%Y-%m-%d') == '{current_date}') & (NomAgence == @agence)"
    )
        number=len(df)
        return number


# --- Composants UI Partagés ---

def load_and_display_css():
    """Charge le fichier CSS consolidé."""
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Dans shared_code.py

def date_range_selection():
    # Ces widgets vont lire et écrire dans st.session_state grâce à l'argument 'key'
    st.sidebar.date_input(
        "Date Début", 
        key="start_date"  # La valeur sera st.session_state.start_date
    )
    st.sidebar.date_input(
        "Date Fin", 
        key="end_date"    # La valeur sera st.session_state.end_date
    )

    if st.session_state.start_date > st.session_state.end_date:
        st.sidebar.error("La date de début ne peut pas être après la date de fin.")
        st.stop()


def filtering(df, UserName, NomService):
              
    return df.query('UserName in @UserName & NomService in @NomService')



def filter1(df_all):
    
    # Appliquer un style CSS pour restreindre la hauteur
    
    with st.sidebar:
        with st.popover("Nom des Services",use_container_width=True):

            show_multiselect = True
            if show_multiselect:
                
                NomService = st.multiselect(
        'Services',
        options=df_all['NomService'].unique(),
        default=df_all['NomService'].unique()
    )
    
        #st.write(f"✅ {len(NomService)} disponible(s)")
    
    # Filter df_all based on the selected NomService
    df = df_all[df_all['NomService'].isin(NomService)]

    # UserName selection

    with st.sidebar:
        with st.popover("Nom des Agents",use_container_width=True):

            show_multiselect = True
            if show_multiselect:
                
                UserName = st.multiselect(
        'Agents',
        options=df['UserName'].unique(),
        default=df['UserName'].unique()
    )
       
        #st.write(f"✅ {len(UserName)} Agent(s) en ligne")
    

    
    
    df_selection = filtering(df, UserName, NomService)
    return df_selection




def filter2(df_agence_Region):
    """
    Génère des filtres hiérarchiques liés mais indépendants en affichage.
    - 'selected_agencies' est la seule source de vérité pour la sélection.
    - L'état des régions est dérivé de la sélection des agences.
    - Le filtre agence montre toujours toutes les agences connectées disponibles.
    """
    # Initialisation et nettoyage de la source de vérité
    if 'selected_agencies' not in st.session_state:
        # Par défaut, tout est sélectionné au premier lancement
        st.session_state.selected_agencies = st.session_state.df_main['NomAgence'].unique().tolist()
    st.session_state.selected_agencies = [a for a in st.session_state.get('selected_agencies', []) if pd.notna(a)]

    # --- Préparation des données ---
    df_main = st.session_state.df_main
    online_regions = sorted(df_main['Region'].unique().tolist())
    all_online_agencies = sorted(df_main['NomAgence'].unique().tolist())
    
    all_regions_total = df_agence_Region['Region'].unique().tolist()
    offline_regions = sorted([r for r in all_regions_total if r not in online_regions])
    
    agency_display_map = {row['NomAgence']: f"{row['NomAgence']} ({row['Region']})" for _, row in df_agence_Region.iterrows()}

    # --- FILTRE RÉGION ---
    with st.sidebar:
        with st.popover("Régions", use_container_width=True):
            with st.container(height=300):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Tout cocher", key="select_all_regions", use_container_width=True):
                        st.session_state.selected_agencies = all_online_agencies
                        st.rerun()
                with col2:
                    if st.button("Tout décocher", key="deselect_all_regions", use_container_width=True):
                        st.session_state.selected_agencies = []
                        st.rerun()

                st.write("**Régions en lignes**")
                
                for region in online_regions:
                    agencies_in_region = df_main[df_main['Region'] == region]['NomAgence'].unique()
                    is_region_selected = any(agency in st.session_state.selected_agencies for agency in agencies_in_region)

                    if st.checkbox(region, value=is_region_selected, key=f"cb_region_{region}") != is_region_selected:
                        if is_region_selected: # Si on décoche, on retire toutes ses agences
                            st.session_state.selected_agencies = [a for a in st.session_state.selected_agencies if a not in agencies_in_region]
                        else: # Si on coche, on ajoute toutes ses agences
                            st.session_state.selected_agencies.extend([a for a in agencies_in_region if a not in st.session_state.selected_agencies])
                        st.rerun()
                
                st.divider()
                st.write("**Régions hors lignes**")
                if offline_regions:
                    for region in offline_regions:
                        st.markdown(f"• _{region}_")
                else:
                    st.markdown("_Aucune région hors ligne._")

        # L'état des régions sélectionnées est toujours DÉRIVÉ des agences
        selected_regions = df_main[df_main['NomAgence'].isin(st.session_state.selected_agencies)]['Region'].unique().tolist()
        st.write(f"✅ {len(selected_regions)}/{len(online_regions)} Région(s) sélectionnée(s)")
    
    if not st.session_state.selected_agencies:
        st.sidebar.warning("Vous devez sélectionner au moins une agence.")
        st.stop()

    # --- FILTRE AGENCE ---
    st.sidebar.write(' ')
    with st.sidebar:
        with st.popover("Agences", use_container_width=True):
            with st.container(height=300):
                col3, col4 = st.columns(2)
                with col3:
                    if st.button("Tout cocher", key="select_all_agences", use_container_width=True):
                        st.session_state.selected_agencies = all_online_agencies
                        st.rerun()
                with col4:
                    if st.button("Tout décocher", key="deselect_all_agencies", use_container_width=True):
                        st.session_state.selected_agencies = []
                        st.rerun()
                
                # --- SECTION 1: AGENCES CONNECTÉES (INTERACTIF) ---
                st.write("**Agences en lignes**")
                # On itère sur TOUTES les agences en ligne, sans filtre de région
                for agence in all_online_agencies:
                    is_selected = agence in st.session_state.selected_agencies
                    display_label = agency_display_map.get(agence, agence)
                    
                    if st.checkbox(display_label, value=is_selected, key=f"cb_agence_{agence}") != is_selected:
                        if is_selected:
                            st.session_state.selected_agencies.remove(agence)
                        else:
                            st.session_state.selected_agencies.append(agence)
                        st.rerun()
                
                st.divider()

                # --- SECTION 2: AGENCES HORS LIGNE (LECTURE SEULE) ---
                # Affiche les agences hors ligne des régions actuellement sélectionnées
                st.write("**Agences hors lignes**")
                online_agencies_in_scope = df_main[df_main['Region'].isin(selected_regions)]['NomAgence'].unique().tolist()
                all_agencies_in_scope = df_agence_Region[df_agence_Region['Region'].isin(all_regions_total)]['NomAgence'].unique().tolist()
                offline_agencies_in_scope = [a for a in all_agencies_in_scope if a not in online_agencies_in_scope and pd.notna(a)]
                st.session_state.offline_agencies_in_scope = offline_agencies_in_scope  # Pour tests éventuels
                if offline_agencies_in_scope:
                    for agence in offline_agencies_in_scope:
                        display_label = agency_display_map.get(agence, agence)
                        st.markdown(f"• _{display_label}_")
                else:
                    st.markdown("_Aucune agence hors ligne dans les régions sélectionnées._")
        
        st.write(f"✅ {len(st.session_state.selected_agencies)}/{len(all_online_agencies)} Agence(s) sélectionnée(s)") 
        
@st.cache_data(ttl=1800, show_spinner=False)  # Cache 30min pour les données principales
def load_main_data(start_date, end_date):
    """Charge les données principales une seule fois et les met en cache"""
    conn = get_connection()
    df = run_query(conn, SQLQueries().AllQueueQueries, params=(start_date, end_date))
    return df

def create_sidebar_filters():
    
    


    # Rendu des date_input avec valeur actuelle
    start_date = st.sidebar.date_input("Date Début", value=st.session_state.start_date, key="start_date_input")
    end_date = st.sidebar.date_input("Date Fin", value=st.session_state.end_date, key="end_date_input")

    # Mise à jour manuelle du session_state
    st.session_state.start_date = start_date
    st.session_state.end_date = end_date



    if st.session_state.start_date > st.session_state.end_date:
        st.error("La date de début ne peut pas être après la date de fin.")
        st.stop()

    # Charger les données principales une seule fois
    if "df_main" not in st.session_state or st.session_state.get("last_date_range") != (start_date, end_date):
        
        with st.spinner("Chargement des données..."):
            st.session_state.df_main = load_main_data(start_date, end_date)
            st.session_state.last_date_range = (start_date, end_date)
            st.session_state.selected_Region =st.session_state.df_main['Region'].unique().tolist()
            st.session_state.selected_agencies = st.session_state.df_main['NomAgence'].unique().tolist()
    # Initialiser dans st.session_state si la clé n'existe pas
    if "all_agence_Region" not in st.session_state :
        
        conn = get_connection()
        df_Agence_Regionx = run_query(conn, SQLQueries().All_Region_Agences,params=None)
        st.session_state.all_agence_Region=df_Agence_Regionx
        AllRegion = df_Agence_Regionx['Region'].unique().tolist()
        st.session_state.all_Region = AllRegion
       
        ### AJOUTS ICI POUR CORRIGER L'ERREUR ###
        # On initialise aussi la liste de toutes les agences et les agences sélectionnées par défaut
        AllAgences = df_Agence_Regionx['NomAgence'].unique().tolist()
        st.session_state.all_agencies = AllAgences
    
    filter2(st.session_state.all_agence_Region)
    # Initialiser dans st.session_state si la clé n'existe pas
    # if "selected_agencies" not in st.session_state:
    #     conn = get_connection()
    #     df_agences = run_query(conn, SQLQueries().AllAgences,params=None)
    #     available_agencies = df_agences['NomAgence'].unique()
    #     st.session_state.all_agencies = available_agencies
    #     st.session_state.selected_agencies = available_agencies  # valeur par défaut
    

#     st.sidebar.markdown("""
#     <style>
#     .stMultiSelect > div {
#         max-height: 120px;
#         overflow-y: auto;
#     }
#     </style>
# """, unsafe_allow_html=True)
    
    
    
    
    

    #st.sidebar.markdown("<div style='position: fixed; bottom: 0; left: 0; width: 17rem; padding: 10px; text-align: center;'>Copyright Obertys 2025</div>", unsafe_allow_html=True)
# --- Fonctions de Visualisation Partagées ---




def create_folium_map(agg):
    legend_html = ''  # Variable pour stocker la légende HTML
    
    df=agg.copy()
    
    df['Temps_Moyen_Attente']=df['Temps_Moyen_Attente'].fillna(' ')
    # Définition des couleurs uniques par NomAgence
    agences = list(df["NomAgence"].unique())
    couleurs = [
        'blue', 'green', 'purple', 'orange', 'darkred', 'red',
        'cadetblue', 'darkpurple', 'pink', 'lightblue', 'lightgreen', 
        'gray', 'black', 'darkblue'
    ]

    agence_couleur = {
        agence: couleurs[i % len(couleurs)] 
        for i, agence in enumerate(agences)
    }
    # 4. Déterminer la vue initiale de la carte
    if df.empty or df["Latitude"].isnull().all() or df["Longitude"].isnull().all():
        map_location = [14.4974, -14.4524] # Centre du Sénégal
        map_zoom = 6
    else:
        map_location = [df["Latitude"].mean(), df["Longitude"].mean()]
        map_zoom = 7

    # 5. Créer l'objet carte en utilisant la position sauvegardée si elle existe
    m = folium.Map(
        location= map_location,
        zoom_start= map_zoom,
        control_scale=True,
        prefer_canvas=True,
        width="100%",
        height="100%"
    )
    # Générer des polygones et marqueurs par ville
    for ville, group in df.groupby("Region"):
        min_lat, max_lat = group["Latitude"].min(), group["Latitude"].max()
        min_lon, max_lon = group["Longitude"].min(), group["Longitude"].max()

        # Définition du polygone (bounding box)
        polygon_coords = [
            [min_lat, min_lon], [max_lat, min_lon],
            [max_lat, max_lon], [min_lat, max_lon],
            [min_lat, min_lon]
        ]
        folium.Polygon(
            locations=polygon_coords,
            color="black",
            fill=True,
            fill_color="gray",
            fill_opacity=0.2,
            popup=f"Région: {ville}"
        ).add_to(m)

        # Ajouter les marqueurs avec popups
        for _, row in group.iterrows():
            popup_text = (
                f"<b>Région:</b> {row['Region']}<br>"
                f"<b>Nom Agence:</b> {row['NomAgence']}<br>"
                f"<b>Client en Attente:</b> {row['AttenteActuel']} <br>"
                f"<b>Temps Moyen d'Attente:</b> {row['Temps_Moyen_Attente']} min"
            )

            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                tooltip=popup_text,  # Affichage au survol
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=agence_couleur[row["NomAgence"]], icon="info-sign")
            ).add_to(m)

    return m._repr_html_()  


def echarts_satisfaction_gauge(queue_length, title="Client(s) en Attente",max_length=100,key="1"):
    value = int(queue_length)
    max_value = int(max_length)
    
    max_gauge=100
    min_gauge=0
    
    
   
    
    # --- Determine Pointer Color based on Gauge Progress ---
    current_percentage = value / max_value
    
    pointer_color = '#FF0000' if value >= max_value else ('black' if current_percentage ==0 else
        green_color if current_percentage < 0.5 else blue_clair_color if current_percentage < 0.8 else blue_color
    )
    
    status={"black":'Vide',green_color:"Modérement occupée",blue_clair_color:"Fortement occupée",blue_color:"Très fortement occupée ",'#FF0000':'Congestionnée'}
    
    
    
    seuil_pourcentage = max_value / 100
    # Crée une petite zone rouge autour du seuil (ex: de 29% à 31% si le seuil est 30)
    debut_rouge = max(0, seuil_pourcentage - 0.01)
    fin_rouge = min(1, seuil_pourcentage + 0.01)
    

    options = {"backgroundColor":BackgroundGraphicColor,
               "title": {"text": status[pointer_color],"left": 'center',"top":'2%',
        "textStyle": {
                "color": blue_color
            }},
    "series": [
        {   
            "type": "gauge",
            "startAngle": 200,
            "endAngle": -20,
            "min": 0,
            "max": 100,
            "splitNumber": max_gauge,
            # --- La barre de progression qui montre la valeur actuelle ---
            "progress": {
                "show": True,
                "width": 20,
                "itemStyle": {
                    "color": "transparent"
                } 
            },
            "axisLine": {
                "lineStyle": {
                    "width": 20,
                    "color": [[value/100,"#013447"],[debut_rouge, "lightblue"],[fin_rouge, "red"],[1,"lightblue"]] if (value/100)<debut_rouge else
                        
                        [[value/100, "#013447"],[fin_rouge, "red"],[1,"lightblue"]] if (value/100)<fin_rouge and (value/100)>=debut_rouge else 

                        [[debut_rouge, "#013447"],[fin_rouge, "red"],[1,"lightblue"]] if (value/100)==fin_rouge else 

                        [[debut_rouge, "#013447"],[fin_rouge, "red"],[value/100,"#013447"],[1,"lightblue"]]
                        
                }
            },
            "pointer": {
                "show": True,
                "length": "65%",
                "width": 6,
                "itemStyle": {
                    "color": "#013447"
                }
            },
        
            # --- MODIFICATION 1 : Masquer les petits traits ---
            "axisTick": {
                "show": False# On cache les petits traits de graduation internes
            },
            "splitLine": {
                "show": False
            },
            # --- MODIFICATION 2 : N'afficher que le label "30" ---
            "axisLabel": {
                "show": True, # L'axe des labels doit rester visible
                "distance": 5, # Distance du label par rapport à la jauge
                "color": blue_color, #"#333",
                "fontSize": 16,
                "interval": 0,
                # Astuce JS pour n'afficher que le label "0,100 ou max_value"
                "formatter": JsCode(f"function(value){{if(value==={min_gauge}||value==={max_gauge}||value==={max_value}){{return value;}}return '';}}").js_code
            },
            "detail": {
                "valueAnimation": True,
                "formatter": f"{value}",
                "fontSize": 60,
                "fontWeight": "bold",
                "color": blue_color,
                "offsetCenter": [0, "100%"]
            },
            "title": {
                "show": True,
                "offsetCenter": [0, "60%"],
                "fontSize": 22,
                "color": "#333"
            },
            "data": [
                {
                    "value": value,
                    "name": "Clients en Attente"
                }
            ],
          
            
        }
    ]
}
    # Ensure st_echarts is imported
    # from streamlit_echarts import st_echarts
    st_echarts(options=options, height="280px", key='4')

################ Nouveau ###########
def stacked_chart2(data,type:str,concern:str,titre):
    """
    Default values of type:
    'TempsAttenteReel' and 'TempOperation'
    """
    df=data.copy()
    df = df.dropna(subset=[type])

    if df.empty:
        return {"title": {"text": f"(Pas de données)", "left": 'center'}}



    top_categories=['0-5min','5-10min','>10min']
    # color_scale = alt.Scale(
    #     domain=top_categories,  # The top categories you want to color specifically
    #     range=[blue_color,blue_clair_color,green_color]   # Replace with the colors you want to assign to each category
    # ) 
      
  
    if  concern=='NomAgence':
        
        df['Categorie'] = df[type].apply(lambda x: 
        '0-5min' if 0 <= np.round(x/60).astype(int) <= 5 else 
        '5-10min' if 5 < np.round(x/60).astype(int) <= 10 else 
        '>10min'
    )
        df=df.groupby([f'{concern}', 'Categorie']).size().reset_index(name='Count')
        
        df_pivoted = df.pivot_table(
        index=concern,
        columns="Categorie",
        values="Count",
        fill_value=0
    )
        options = {
            "backgroundColor":BackgroundGraphicColor,
            "title": {"text": titre,"left": 'center',
        "textStyle": {
                "color": GraphicTitleColor
            }},
            "color":Simple_pallette
            ,
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        # Get legend data from the pivoted DataFrame's columns
        "legend": {"data": df_pivoted.columns.tolist(),"left":'right'},
        "grid": {
            "left": "3%",
            "right": "6%",
            "bottom": "15%", # Increase bottom margin for rotated labels
            "containLabel": True
        },
        # X-axis uses categories from the pivoted DataFrame's index
        "xAxis": {
            "type": "category",
            "data": df_pivoted.index.tolist(),
            "axisLabel": {
                "rotate": 30,  # Rotate labels to prevent overlap
                "interval": 0  # Ensure all labels are shown
            },
            "name":"Agences"
        },
        # Y-axis is the value axis
        "yAxis": {"type": "value","name":"Valeur totale"},
        # Create a series for each column in the pivoted DataFrame
        "series": [
            {
                "name": category,
                "type": "bar",
                "stack": "total", # This key is what creates the stacking
                "label": {"show": True, "position": "inside"},
                "emphasis": {"focus": "series"},
                "data": df_pivoted[category].tolist(),
            }
            for category in df_pivoted.columns
        ],
    }
    else:
       
        df['Type_Operation'] = df['Type_Operation'].fillna('Inconnu')
        # Ensure Categorie is correctly assigned based on TempOperation (in minutes)
        df[type] = df[type].apply(lambda x: np.round(x / 60).astype(int))

        df['Categorie'] = df[type].apply(
            lambda x: 
            '0-5min' if 0 <= x <= 5 else 
            '5-10min' if 5 < x <= 10 else 
            '>10min'
        )
  
        


        # Group by UserName and Categorie, count the occurrences
        df_count = df.groupby([f'{concern}', 'Categorie']).size().reset_index(name='Count')

        top_operations = df.groupby([concern, 'Categorie', 'Type_Operation', type]).size().reset_index(name='OperationCount')
        top_operations = top_operations.sort_values(['UserName', 'Categorie', type], ascending=[True, True, False])
        top_operations = top_operations.groupby([f'{concern}', 'Categorie']).head(5)
        
        
        
        
        # Combine the TypeOperation, TempOperation, and OperationCount into a single string for tooltips
        top_operations['TopOperations'] = top_operations.apply(
    lambda row: f"{row['Type_Operation']} ({row[type]} min, {row['OperationCount']} fois)", axis=1
)
        top_operations = top_operations.groupby([f'{concern}', 'Categorie'])['TopOperations'].apply(lambda x: ', '.join(x)).reset_index()
        
        df = pd.merge(df_count, top_operations, on=[f'{concern}', 'Categorie'], how='left')
        # 2. Construct the ECharts options dictionary from the DataFrame
        
        

        # Use pivot_table to structure data for ECharts series
        df_pivot_count = df.pivot_table(index='UserName', columns='Categorie', values='Count', aggfunc='sum').fillna(0)
        df_pivot_ops = df.pivot_table(index='UserName', columns='Categorie', values='TopOperations', aggfunc='first').fillna('')

        # Define the explicit order for categories and get users
        categories_order = ['0-5min', '5-10min', '>10min']
        users = df_pivot_count.index.tolist()

        # Reorder the columns in the pivot tables to match our desired stacking order
        df_pivot_count = df_pivot_count.reindex(columns=categories_order, fill_value=0)
        df_pivot_ops = df_pivot_ops.reindex(columns=categories_order, fill_value='')


        # --- STEP 2: BUILD THE ENTIRE TOOLTIP HTML IN THE LIST COMPREHENSION ---
        # All formatting logic is now in Python, which is safer and easier to debug.
        
        
        
        tooltip_formatter_js = JsCode("function (params) {return `<b>Agent(s):</b> ${params.name}<br/><b>Queue:</b> ${params.seriesName}<br/><b>Nombre:</b> ${params.value}<br/><b>5 premières opérations:</b><br/>${params.data.operations}`;}").js_code


        series_list = [
    {
        "name": category,
        "type": "bar",
        "stack": "total",
        "emphasis": {"focus": "series"},
        "data": [
            {
                "value": int(df_pivot_count.loc[user, category]),
                # This custom property will be accessible in the tooltip formatter via @{operations}
                "operations": (df_pivot_ops.loc[user, category].replace(', ', '<br/>') or 'N/A')
            }
            for user in users
        ]
    }
    for category in categories_order
]



        # Define the full ECharts options dictionary
        options = {
            "title": {
                "text": titre,
                "left": "center"
            },
            "tooltip": {
        "trigger": "item",
        "formatter": tooltip_formatter_js, # Use the template string
        "axisPointer": {"type": "shadow"},
    },
            "legend": {
                "data": categories_order,
                "top": "bottom"
            },
            "grid": {
                "left": "3%",
                "right": "6%",
                "bottom": "10%",
                "containLabel": True,
            },
            "xAxis": [
                {
                    "type": "category",
                    "data": users,
                    "axisLabel": {
                        "rotate": 45,
                        "interval": 0
                    },
                    "name":"Agents"
                }
            ],
            "yAxis": [{"type": "value", "name": "Valeur totale"}],
            "series": series_list,
        }


        
    
    return options


def stacked_chart(data,type:str,concern:str,titre,w=1000,h=400):
    """
    Default values of type:
    'TempsAttenteReel' and 'TempOperation'
    """
    df=data.copy()
    df=df.sample(n=min(5000, len(data)),replace=False)
    df = df.dropna(subset=[type])

    top_categories=['0-5min','5-10min','>10min']
    color_scale = alt.Scale(
        domain=top_categories,  # The top categories you want to color specifically
        range=[blue_color,blue_clair_color,green_color]   # Replace with the colors you want to assign to each category
    ) 
      
    if concern=='UserName':
        x='Agent(s)'
    else:
        x='Agence(s)'
    if type=='TempsAttenteReel' or concern=='NomAgence':
        
        df['Categorie'] = df[type].apply(lambda x: 
        '0-5min' if 0 <= np.round(x/60).astype(int) <= 5 else 
        '5-10min' if 5 < np.round(x/60).astype(int) <= 10 else 
        '>10min'
    )
        df=df.groupby([f'{concern}', 'Categorie']).size().reset_index(name='Count')
        
       
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(f'{concern}:O', title=f'{x}'),
            y=alt.Y('Count:Q', title='Nombre'),
            color=alt.Color('Categorie:N', title='Queue',sort=top_categories,scale=color_scale),
            order=alt.Order('Categorie:N',title='Queue')  # Ensures the stacking order
        ).properties(
            width=1000,
            height=400,
            title={
        "text": f"{titre} par {x}",
        "anchor": "middle",
        "fontSize": 16,
        "font": "Helvetica",
       'color': GraphicTitleColor
    }
       
            
        ).configure(
    background=BackgroundGraphicColor   # Set the background color for the entire figure
)
    else:
        
        df['Type_Operation'] = df['Type_Operation'].fillna('Inconnu')
        # Ensure Categorie is correctly assigned based on TempOperation (in minutes)
        df[type] = df[type].apply(lambda x: np.round(x / 60).astype(int))

        df['Categorie'] = df[type].apply(
            lambda x: 
            '0-5min' if 0 <= x <= 5 else 
            '5-10min' if 5 < x <= 10 else 
            '>10min'
        )
  
        


        # Group by UserName and Categorie, count the occurrences
        df_count = df.groupby([f'{concern}', 'Categorie']).size().reset_index(name='Count')

        # Calculate the top 2 TypeOperation and corresponding TempOperation (now in minutes) per UserName and Categorie
        # top_operations = df.groupby([f'{concern}', 'Categorie', 'Type_Operation'])[type].agg(
        #     lambda x: np.round(x.mean()).astype(int)
        # ).reset_index(name=type)
        #top_operations = top_operations.sort_values([f'{concern}', 'Categorie', type], ascending=[True, True, False])
        
        top_operations = df.groupby(['UserName', 'Categorie', 'Type_Operation', type]).size().reset_index(name='OperationCount')
    
        top_operations = top_operations.sort_values(['UserName', 'Categorie', type], ascending=[True, True, False])
        top_operations = top_operations.groupby([f'{concern}', 'Categorie']).head(5)
        st.write(top_operations)
        if len(top_operations)==0:
            chart = alt.Chart(top_operations).mark_bar().encode(
            x=alt.X(f'{concern}:O', title=f'{x}'),
            y=alt.Y('Count:Q', title='Nombre par Categorie'),
            color=alt.Color('Categorie:N', title='Queue',sort=top_categories,scale=color_scale),
            order=alt.Order('Categorie:N',title='Queue'),  # Ensures the stacking order
            tooltip=[
                alt.Tooltip('UserName:O', title=f'{x}'),
                alt.Tooltip('Count:Q', title='Nombre'),
                alt.Tooltip('Categorie:N', title='Queue'),
                alt.Tooltip('TopOperations:N', title='5 premières opérations')
            ]
        ).properties(
            width=1000,
            height=400,
         title={
        "text": f"{titre} par {x}",
        "anchor": "middle",
        "fontSize": 16,
        "font": "Helvetica",
       'color': GraphicTitleColor
    }
        ).configure(
    background=BackgroundGraphicColor   # Set the background color for the entire figure
) 
            return chart

        # Combine the TypeOperation, TempOperation, and OperationCount into a single string for tooltips
        top_operations['TopOperations'] = top_operations.apply(
    lambda row: f"{row['Type_Operation']} ({row[type]} min, {row['OperationCount']} fois)", axis=1
)
        top_operations = top_operations.groupby([f'{concern}', 'Categorie'])['TopOperations'].apply(lambda x: ', '.join(x)).reset_index()
        #top_operations = top_operations.groupby([f'{concern}', 'Categorie'])['TopOperations'].apply(lambda x: '\n'.join(x)).reset_index()
        #top_operations = top_operations.groupby([f'{concern}', 'Categorie'])['TopOperations'].apply(lambda x: '\n'.join([f"({op}, {count} fois)" for op, count in x.value_counts().items()])).reset_index()

        #st.table(top_operations)
        
        # Merge the top operations back with the count dataframe
        df_final = pd.merge(df_count, top_operations, on=[f'{concern}', 'Categorie'], how='left')
        #st.dataframe(df_final)
        # Create the Altair chart with tooltips
        st.write(df_final)
        chart = alt.Chart(df_final).mark_bar().encode(
            x=alt.X(f'{concern}:O', title=f'{x}'),
            y=alt.Y('Count:Q', title='Nombre par Categorie'),
            color=alt.Color('Categorie:N', title='Queue',sort=top_categories,scale=color_scale),
            order=alt.Order('Categorie:N',title='Queue'),  # Ensures the stacking order
            tooltip=[
                alt.Tooltip('UserName:O', title=f'{x}'),
                alt.Tooltip('Count:Q', title='Nombre'),
                alt.Tooltip('Categorie:N', title='Queue'),
                alt.Tooltip('TopOperations:N', title='5 premières opérations')
            ]
        ).properties(
            width=w,
            height=h,
         title={
        "text": f"{titre}",
        "anchor": "middle",
        "fontSize": 16,
        "font": "Helvetica",
       'color': GraphicTitleColor
    }
        ).configure(
    background=BackgroundGraphicColor   # Set the background color for the entire figure
)
    return chart

def TempsPassage(data):
    """
    Default values of type:
    'TempsAttenteReel' and 'TempOperation'
    """
    df=data.copy()
    df=df.sample(n=min(5000, len(data)),replace=False)
    df['TempsAttenteReel'] = df['TempsAttenteReel'].dropna()
    df['TempOperation'] = df['TempOperation'].dropna()
    df['TempsPassage']=df['TempsAttenteReel']+df['TempOperation']
    
    
    df['Categorie'] = df['TempsPassage'].apply(lambda x: 
    '0-30min' if 0 <= np.round(x/60).astype(int) <= 30 else 
    '30min-1h' if 30 < np.round(x/60).astype(int) <= 60 else 
    '>1h'
)
    df=df.groupby(['NomAgence', 'Categorie']).size().reset_index(name='Count')
    top_categories=['0-30min','30min-1h','>1h']
    color_scale = alt.Scale(
        domain=top_categories,  # The top categories you want to color specifically
        range=[blue_color,blue_clair_color,green_color]  # Replace with the colors you want to assign to each category
    )
        
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(f'NomAgence:O', title=f'Agence(s)'),
        y=alt.Y('Count:Q', title='Nombre par Categorie'),
        color=alt.Color('Categorie:N',title='Queue',sort=top_categories,scale=color_scale),
        order=alt.Order('Categorie:N',title='Queue')  # Ensures the stacking order
    ).properties(
        width=1000,
        height=400,
        title={
    "text": f"Répartition en trois du Temps de Passage par Agence",
    "anchor": "middle",
    "fontSize": 16,
    "font": "Helvetica",
   'color': GraphicTitleColor
}
        
        ).configure(
    background=BackgroundGraphicColor   # Set the background color for the entire figure
)
    return chart


def assign_to_bin(date,bins):
    date = pd.Timestamp(date).normalize()  # Convert string date to Timestamp and normalize (ignore time)
    for start, end in bins:
        start_date = pd.Timestamp(start).normalize()
        end_date = pd.Timestamp(end).normalize()
        if start_date <= date <= end_date:
            return f"{start_date.date()} to {end_date.date()}"
    return None   
def get_time_bins(min_date, max_date, bin_type):
    start_date = min_date
    time_bins = []

    if bin_type == 'Mois':
        offset = pd.DateOffset(months=1)
    elif bin_type == 'Semaine':
        offset = pd.DateOffset(weeks=1)
    elif bin_type == 'Annee':
        offset = pd.DateOffset(years=1)
    else:
        raise ValueError("bin_type must be 'month', 'week', or 'year'")

    while start_date <= max_date:
        if bin_type == 'Semaine':
            end_date = start_date + pd.DateOffset(days=6)
        else:
            end_date = (start_date + offset) - pd.DateOffset(days=1)

        # Ensure the end date does not exceed the max_date
        if end_date > max_date:
            end_date = max_date

        time_bins.append((start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

        # Move to the next bin
        start_date = end_date + pd.DateOffset(days=1)

    return time_bins

################## NEW ######################




def area_graph2(data,concern='UserName',time='TempOperation',date_to_bin='Date_Fin',seuil=5,title='Courbe'):
    df=data.copy()
    df=df.dropna(subset=[date_to_bin])

    # Convert columns to datetime
    df['Date_Reservation'] = pd.to_datetime(df['Date_Reservation'])
    df[date_to_bin] = pd.to_datetime(df[date_to_bin])


    # Calculate the difference between the min and max dates
    min_date = df['Date_Reservation'].min()
    max_date = df['Date_Reservation'].max()
    date_diff = (max_date - min_date).days

    # Define the Time_Bin intervals based on the date difference
    if date_diff == 0:
        time_bin_labels = ['7-8h', '8-9h', '9-10h', '10-11h', '11-12h', 
                           '12-13h', '13-14h', '14-15h', '15-16h', '16-17h', '17-18h']
        unit, df['Time_Bin'] = 'Heure', pd.cut(df[date_to_bin].dt.hour, bins=range(7, 19), labels=time_bin_labels, right=False)
        df['Time_Bin'] = pd.Categorical(df['Time_Bin'], categories=time_bin_labels, ordered=True)
    elif 1 <= date_diff <=7:
        unit, df['Time_Bin'], complete_dates = 'Jour', df[date_to_bin].dt.day, range(min_date.day, max_date.day + 1)
    else:
        unit = ['Semaine', 'Mois', 'Annee'][int(date_diff > 84) + int(date_diff > 365)]
        bins = get_time_bins(min_date, max_date, unit)
        df['Time_Bin'] = df[date_to_bin].apply(lambda x: assign_to_bin(x, bins))


    # Group by Nom_Agence and Time_Bin, and calculate the average TempAttente
    #grouped_data = df.groupby([concern, 'Time_Bin'])[[time]].agg(( lambda x: np.round(np.mean(x)/60).astype(int))).reset_index()

    grouped_data = df.groupby([concern, 'Time_Bin'])[[time]].agg(lambda x: np.round(np.nanmean(x) / 60).astype(int)).reset_index()
    
#     seuil = st.number_input(
#     "Définir la valeur du seuil",
#     min_value=0,
#     max_value=100,
#     value=seuil, # Valeur par défaut
#     step=1
# )
    
        
    if grouped_data.empty:
        return {"title": {"text": f"(Pas de données)", "left": 'center'}}

    # Select the top 5 agencies with the largest area under the curve
    if len(df['NomAgence'].unique())==1 and concern=='UserName':
        top_agences=grouped_data[concern].unique()
    else:
        top_agences =grouped_data.groupby(concern)[time].sum().nlargest(5).index.tolist()
    


    # Create a DataFrame with all combinations of agencies and time bins
    if unit=="Jour":
        all_combinations = pd.MultiIndex.from_product([top_agences, sorted(complete_dates)], names=[concern, 'Time_Bin']).to_frame(index=False)
    else:
        
        all_combinations = pd.MultiIndex.from_product([top_agences, sorted(df['Time_Bin'].dropna().unique())], names=[concern, 'Time_Bin']).to_frame(index=False)

    all_combinations = pd.merge(all_combinations, grouped_data, on=[concern, 'Time_Bin'], how='left').fillna(0)
    
    
    if unit=='Heure':
        all_combinations['Time_Bin'] = pd.Categorical(
            all_combinations['Time_Bin'],
            categories=time_bin_labels,
            ordered=True
        )

    df_pivoted = all_combinations.pivot_table(
        index='Time_Bin',    # This will become the x-axis
        columns=concern,     # These will become the different series (lines)
        values=time          # These are the y-axis values
    ).reset_index() # .reset_index() makes 'Time_Bin' a column again

        # --- 3. BUILD ECHARTS OPTIONS ---
    # Let's also add some colors, similar to your `couleur` variable
    colors = ['#5470C6', '#91CC75', '#EE6666', '#73C0DE', '#3BA272']

    options = {"backgroundColor": GraphicPlotColor,
    "title": {"text": title,"left": 'center',
    "textStyle": {
            "color": GraphicTitleColor
        }},
    "tooltip": {"trigger": "axis"},
    "legend": {"data": top_agences,'orient':'vertical',"left": 'right'}, # Use the list of agencies for the legend
    "grid": {"left": '5%', "right": '5%', "bottom": '5%',"top":"5%", "containLabel": True},
    "toolbox": {"left": "5%", "feature": {"saveAsImage": {},"magicType": {
                "show": True,
                "type": ['line', 'bar', 'stack'], # Types de graphiques interchangeables
                "title": {
                    "line": "Passer en lignes",
                    "bar": "Passer en barres",
                    "stack": "Empiler"
                }
            }}},
    "xAxis": {
        "type": "category",
        "boundaryGap": False,
        "data": df_pivoted['Time_Bin'].tolist(), # X-axis from the pivoted table
    },
    "yAxis": {"type": "value"},
    
    "series": [
        {
            "name": agence,
            "type": "line",
            "areaStyle": {},  # This is equivalent to Plotly's fill='tozeroy'
            "emphasis": {"focus": "series"},
            "data": df_pivoted[agence].tolist(), # Get data for each agency from its column
            "lineStyle": {"color": colors[i % len(colors)]}, # Assign a color
            "itemStyle": {"color": colors[i % len(colors)]}, # Color for markers
            "markLine":{
            "silent": True,               # La ligne n'est pas cliquable/interactive
            "symbol": "none",             # Cache les flèches aux extrémités de la ligne
            "lineStyle": {
                "type": "dashed",         # 'dashed' pour des tirets, 'dotted' pour des points
                "color": "#333",          # Couleur de la ligne (gris foncé)
                "width": 2                # Épaisseur de la ligne
            },
            "data": [
                {
                    "yAxis": seuil, # Positionne la ligne sur l'axe Y à la valeur du seuil
                    "name": "Seuil",      # Nom utilisé pour l'étiquette
                    "label": {
                        "show": True,
                        "position": "end",  # Affiche l'étiquette à la fin de la ligne
                        "formatter": "{b}: {c}", # Format: 'Nom: Valeur' (ex: "Seuil: 25")
                        "color": "#333",
                        "fontSize": 14
                    }
                }
            ]
        }
        }
        for i, agence in enumerate(top_agences) # Loop through agencies to build the series list
    ],
}
    return options
    









#################################################

def top_agence_freq(df_all,df_queue,title,color=[green_color,blue_clair_color]): 
    _,agg=AgenceTable(df_all,df_queue)
    agg=agg[["Nom d'Agence",title[0],title[1]]]
    

    top_counts0=agg[["Nom d'Agence",title[0]]]
    top_counts0=top_counts0.sort_values(by=title[0], ascending=False)
    top_counts0=top_counts0.head(5)
    top_counts0=top_counts0.rename(columns={title[0]:'Total'})
    top_counts0['Statut']=title[0].split(' ')[1]
    

    top_counts1=agg[["Nom d'Agence",title[1]]]
    top_counts1=top_counts1.sort_values(by=title[1], ascending=False)
    top_counts1=top_counts1.head(5)
    top_counts1=top_counts1.rename(columns={title[1]:'Total'})
    top_counts1['Statut']=title[1].split(' ')[1]
    
    
    top_counts = pd.concat([top_counts0, top_counts1], axis=0)
    
    fig = px.funnel(top_counts, x='Total', y="Nom d'Agence",color='Statut',color_discrete_sequence=color)
    fig.update_layout(title={
        'text': f'{title[0]} vs {title[1]}',
        'x': 0.5,  # Center the title
        'xanchor': 'center' # Set your desired color
        
        },plot_bgcolor=GraphicPlotColor,paper_bgcolor=BackgroundGraphicColor,
                  xaxis=dict(title='tt',tickfont=dict(size=10)),
                  yaxis=dict(title="Nom d'Agence"))
    return fig

def GraphsGlob2(df_all,titre="",color=blue_color):
    

    df=df_all.copy()
    df['TempOperation']=df['TempOperation'].fillna(0)
    df = df.groupby(by=['NomService']).agg(
    TempOperation=('TempOperation', lambda x: np.round(np.mean(x)/60).astype(int))).reset_index()

 
    df = df.rename(columns={'TempOperation': "value", 'NomService': "name"})
   
    chart_data = df.to_dict(orient='records')
    

    # --- CORRECTED ECHARTS OPTIONS ---
    options = {
        "backgroundColor": GraphicPlotColor,
        "title": {
            "text": f"{titre}", # Made title more descriptive
            "left": 'center',
            "textStyle": {
                "color": GraphicTitleColor
            }
        },
        "color":color,
        "tooltip": {
            "trigger": 'axis',  # 'axis' trigger is better for bar charts
            "axisPointer": {
                "type": 'shadow' 
            },
            # CORRECTED: Removed '{d}%' which is for pie charts
            "formatter": '{b}: {c} min' 
        },
        # Toolbox désactivée car problématique dans Streamlit
        "toolbox": {"show": False},
        # ADDED: Bar charts require an xAxis and yAxis
        "xAxis": {
            "type": 'value', # The axis with numbers
            "boundaryGap": [0, 0.01],
            "axisLabel": {
                "color": GraphicTitleColor,
                "formatter": '{value} min' # Add units to the axis
            }
        },
        "yAxis": {
            "type": 'category', # The axis with names/labels
            # Data for the category axis is automatically taken 
            # from the 'name' field in the series data
            "data": [item['name'] for item in chart_data],
            "axisLabel": {
                "color": GraphicTitleColor
            }
        },
        "series": [
            {
                "name": 'Temps moyen', # A more descriptive series name
                "type": 'bar',
                # REMOVED: 'radius' is not a bar chart property
                "data": chart_data,
                "emphasis": {
                    "focus": 'series',
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ],
        # Optional: Add a grid to control padding
        "grid": {
            "left": '0%',
            "right": '0%',
            "bottom": '3%',
            "containLabel": True
        }
    } 
    return options

def stacked_service(data,type:str,concern:str,titre="Nombre de type d'opération par Service"):
    """
    Default values of type:
    'TempsAttenteReel' and 'TempOperation'
    """
    df=data.copy()
    df=df.sample(n=min(5000, len(data)),replace=False)
    df[concern] = df[concern].apply(lambda x: 'Inconnu' if pd.isnull(x) else x)
    
    df=df.groupby([f'{type}', f'{concern}']).size().reset_index(name='Count')
    
    n=len(df[concern].unique()) 

    top_categories=df.groupby([f'{concern}'])['Count'].sum().nlargest(53).reset_index()[f'{concern}'].to_list()
    
    
    color_scale = alt.Scale(
        domain=top_categories,  # The top categories you want to color specifically
        range=palette_colors   # Replace with the colors you want to assign to each category
    )


    


    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(f'{type}:O', title='Service'),
        y=alt.Y('Count:Q', title='Nombre par Categorie'),
        color=alt.Color(f'{concern}:N', title="Type d'Opération" ,sort=top_categories,scale=color_scale   # Apply specific colors to the top three categories
        ),
        order=alt.Order('Count:N', title="Type d'Opération",sort='descending')  # Ensures the stacking order
    ).properties(
        width=600,height=400,
         title={
        "text": f"{titre}",
        "anchor": "middle",
        "fontSize": 16,
        "font": "Helvetica",
       'color': GraphicTitleColor
    }
    
    ).configure(
    background=BackgroundGraphicColor   # Set the background color for the entire figure
)
    return chart


def stacked_agent2(data,type:str,concern:str,titre="Nombre de type d'opération par Agent"):
    """
    Default values of type:
    'TempsAttenteReel' and 'TempOperation'
    """
    df=data.copy()
    df[type] = df[type].apply(lambda x: 'Inconnu' if pd.isnull(x) else x)
    
    df=df.groupby([f'{concern}',f'{type}']).size().reset_index(name='Count')
    
    top_categories=df[type].unique()
    
    # Apply this filter to the dataframe. This is the key step that was missing.
    df_filtered = df[df[type].isin(top_categories)]
    
    
    # If filtering removed all data, handle it gracefully
    if df_filtered.empty:
        return {"title": {"text": f"(Pas de données)", "left": 'center'}}

        
    # Pivot the *filtered* data for charting
    df_pivoted = df_filtered.pivot_table(
        index=concern,
        columns=type,
        values="Count",
        fill_value=0
    )
    tooltip_formatter_js = JsCode("function(params){var agentName=params[0].name;var html=`<b>${agentName}</b><br/>`;let nonZeroSeries=params.filter(p=>p.value>0);nonZeroSeries.sort((a,b)=>b.value-a.value);let top10Series=nonZeroSeries.slice(0,10);if(top10Series.length===0){html+='Aucune valeur non-nulle';return html;}top10Series.forEach(p=>{html+=`${p.marker} ${p.seriesName}: <b>${p.value}</b><br/>`;});if(nonZeroSeries.length>10){html+=`... et ${nonZeroSeries.length-10} autre(s)`;}return html;}").js_code
    
    
    options = {
        "backgroundColor":BackgroundGraphicColor,
        "title": {"text": titre,"left": 'center',
    "textStyle": {
            "color": GraphicTitleColor
        }},
        "color":data_visualization_colors,
    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}, "formatter": tooltip_formatter_js },
    # Get legend data from the pivoted DataFrame's columns
    #"legend": {"data": df_pivoted.columns.tolist(),"left":'right'},
    "grid": {
        "left": "3%",
        "right": "4%",
        "bottom": "6%", # Increase bottom margin for rotated labels
        "containLabel": True
    },
    # X-axis uses categories from the pivoted DataFrame's index
    "xAxis": {
        "type": "category",
        "data": df_pivoted.index.tolist(),
        "axisLabel": {
            "rotate": 30,  # Rotate labels to prevent overlap
            "interval": 0  # Ensure all labels are shown
        },
    },
    # Y-axis is the value axis
    "yAxis": {"type": "value"},
    # Create a series for each column in the pivoted DataFrame
    "series": [
        {
            "name": category,
            "type": "bar",
            "stack": "total", # This key is what creates the stacking
            #"label": {"show": True, "position": "inside"},
            "emphasis": {"focus": "series"},
            "data": df_pivoted[category].tolist(),
        }
        for category in df_pivoted.columns
    ],
}


    return options
def analyse_activity(data, type: str, concern: str, titre="Nombre de type d'opération par Agent"):
    """
    Affiche un graphique dynamique différent pour chaque catégorie de 'concern'.
    """
    df_source = data.copy()
    
    # 1. Préparation initiale des données (votre logique)
    df_source[type] = df_source[type].apply(lambda x: 'Inconnu' if pd.isnull(x) else x)
    
    # On groupe pour obtenir le compte par service (concern) et sous-catégorie (type)
    df_grouped = df_source.groupby([concern, type]).size().reset_index(name='Count')
    
    # S'il n'y a pas de données après le group by, on s'arrête
    if df_grouped.empty:
        st.info("Aucune donnée à afficher avec les filtres actuels.")
        return


    def create_rose_chart_options(df: pd.DataFrame, service_name: str, type_col: str, count_col: str):
        data = [{"value": int(row[count_col]), "name": row[type_col]} for _, row in df.iterrows()]
        return {
            "title": {"text": f"{service_name}","left":"center"},"backgroundColor":BackgroundGraphicColor,
            "tooltip": {"trigger": "item", "formatter": '{b}: {c} ({d}%)'},
            
            "series": [{"name": service_name, "type": 'pie', "radius": ['20%', '70%'],"label": {"show": True, "formatter": "{b}\n{c}"},
                        "roseType": 'area', "itemStyle": {"borderRadius": 8}, "data": data}]
        }

    def create_funnel_chart_options(df: pd.DataFrame, service_name: str, type_col: str, count_col: str):
        df_sorted = df.sort_values(count_col, ascending=False)
        data = [{"value": int(row[count_col]), "name": row[type_col]} for _, row in df_sorted.iterrows()]
        return {
            "title": {"text": f"{service_name}","left":"center"},"backgroundColor":BackgroundGraphicColor,
            "tooltip": {"trigger": "item", "formatter": "{b}: {c}"},
            
            "series": [{"name": service_name, "type": 'funnel', "sort": 'descending', "gap": 2,"label": {"show": True, "position": 'inside', "formatter": '{b}\n{c}'},
                        "label": {"show": True, "position": 'inside'}, "data": data}]
        }

    def create_treemap_chart_options(df: pd.DataFrame, service_name: str, type_col: str, count_col: str):
        data = [{"value": int(row[count_col]), "name": row[type_col]} for _, row in df.iterrows()]
        return {
            "title": {"text": f"{service_name}","left":"center"},"backgroundColor":BackgroundGraphicColor,
            "tooltip": {"formatter": '{b}: {c}'},
            "series": [{"type": 'treemap', "data": data,  "label": {"show": True, "formatter": "{b}\n{c}"},
                        "itemStyle": {"borderColor": "#fff"}}]
        }

    # 3. Logique d'affichage dynamique (simplifiée)
    
    # Obtenir la liste des services (ex: la liste des agents)
    unique_services = df_grouped[concern].unique()
    chart_functions = [create_rose_chart_options, create_funnel_chart_options, create_treemap_chart_options]
    
    generated_figures = []

    for i, service in enumerate(unique_services):
        df_service_simple = df_grouped[df_grouped[concern] == service]
        
        # Choisir la fonction de création d'options
        chart_function_to_use = chart_functions[i % len(chart_functions)]
        
        # Créer les options et les ajouter à la liste
        options = chart_function_to_use(df_service_simple, service, type_col=type, count_col='Count')
        generated_figures.append(options)
        
    return generated_figures
    

def Top10_Type(df_queue,title=""):
    df=df_queue.copy()
    if df.empty:
        return {"title": {"text": f"(Pas de données)", "left": 'center'}}
    df['Type_Operation'] = df['Type_Operation'].apply(lambda x: 'Inconnu' if pd.isnull(x) else x)

    
    top_counts = df['Type_Operation'].value_counts().reset_index()
    top_counts=top_counts.sort_values(by='Type_Operation', ascending=False)
    top_counts=top_counts.head(10)
    top_counts = top_counts.iloc[::-1]

    # Renaming is also correct for ECharts
    top_counts= top_counts.rename(columns={'Type_Operation': "value", 'index': "name"})
    
    chart_data = top_counts.to_dict(orient='records')

    # --- CORRECTED ECHARTS OPTIONS ---
    options = {
        "backgroundColor": GraphicPlotColor,
        "title": {
            "text": title, # Made title more descriptive
            "left": 'center',
            "textStyle": {
                "color": GraphicTitleColor
            }
        },
        "color":green_color,
        "tooltip": {
            "trigger": 'axis',  # 'axis' trigger is better for bar charts
            "axisPointer": {
                "type": 'shadow' 
            },
            # CORRECTED: Removed '{d}%' which is for pie charts
            "formatter": '{b}: {c} ' 
        },
        # Toolbox désactivée car problématique dans Streamlit
        "toolbox": {"show": False},
        # ADDED: Bar charts require an xAxis and yAxis
        "xAxis": {
            "type": 'value', # The axis with numbers
            "boundaryGap": [0, 0.01],
            "axisLabel": {
                "color": GraphicTitleColor,
                "formatter": '{value}' # Add units to the axis
            }
        },
        "yAxis": {
            "type": 'category', # The axis with names/labels
            # Data for the category axis is automatically taken 
            # from the 'name' field in the series data
            "data": [item['name'] for item in chart_data],
            "axisLabel": {
                "color": GraphicTitleColor
            }
        },
        "series": [
            {
                "name": "Type d'Opération", # A more descriptive series name
                "type": 'bar',
                "label": {"show": True, "position": "inside"},
                # REMOVED: 'radius' is not a bar chart property
                "data": chart_data,
                "emphasis": {
                    "focus": 'series',
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ],
        # Optional: Add a grid to control padding
        "grid": {
            "left": '0%',
            "right": '0%',
            "bottom": '3%',
            "containLabel": True
        }
    } 
    return options


# Plotting with Plotly
def find_highest_peak(df, person):
        df_person = df[df['UserName'] == person]
        max_row = df_person.loc[df_person['count'].idxmax()]
        return max_row['Date_Reservation']
def find_value_peak(df, person):
        df_person = df[df['UserName'] == person]
        return df_person['count'].max()



def plot_line_chart(df):
    if len(df['Date_Reservation'].dt.date.unique())==1:

        grouped = df.groupby('UserName').size().reset_index(name='count')
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=grouped['UserName'],
            y=grouped['count'],
            mode='lines+markers+text',
            text=grouped.apply(lambda row: f" {row['count']}", axis=1),
            textposition='top center',
            marker=dict(size=10,color=blue_color),
            name='Total Count'
            

        ))

        fig.update_layout(
            xaxis=dict(title='Agent(s)',tickfont=dict(size=10)),
            yaxis=dict(title="Nombre d'Opération"),margin=dict(l=150, r=20, t=30, b=150),
            title={
        'text': "Nombre d'Opération par Agent",
        'x': 0.5,  # Center the title
        'xanchor': 'center',
             'font': {
            'color': GraphicTitleColor  # Set your desired color
        }}
        ,plot_bgcolor=GraphicPlotColor,paper_bgcolor=BackgroundGraphicColor,
            showlegend=False,height=500
        )
        
    
    else:

        df['date'] = df['Date_Reservation'].dt.date

        filtered_df = df

        # Agréger les données par jour et par personne
        aggregated_df = filtered_df.groupby(['UserName', 'date']).size().reset_index(name='count')
        
        aggregated_df['Date_Reservation'] = aggregated_df['UserName'] + ' = ' + aggregated_df['date'].astype(str)
       
        # Récupération des dates des pics les plus élevés pour chaque personne
        peak_dates = {person: find_highest_peak(aggregated_df, person) for person in aggregated_df['UserName'].unique()}

        # Filtrage des dates d'abscisse pour n'afficher que les dates des pics
        peak_date_strings = [date for date in peak_dates.values()]
        
        agg=aggregated_df.loc[aggregated_df.groupby('UserName')['count'].idxmax()]

        # Créer le graphique
        
        fig = px.line(aggregated_df, x='Date_Reservation', y='count', color='UserName',line_group='UserName', title='Nombre d\'Opération par Agent', markers=True)
        fig.update_xaxes(
        tickmode='array',
        tickvals=[date for date in peak_dates.values()],
        ticktext=peak_date_strings
       )  
    
        fig.add_trace(go.Scatter(
            x=agg['Date_Reservation'],
            y=agg['count'],
            mode='text',
            text=agg.apply(lambda row: f" {row['count']}", axis=1),
            textposition='top center',
            marker=dict(size=10,color=blue_color),
            showlegend=False

        ))
        

        fig.update_layout(
            xaxis_title='Date de Pick de Client par Agent',
            yaxis_title='Nombre d\'Opérations',
            xaxis_tickangle=-45,plot_bgcolor=GraphicPlotColor,paper_bgcolor=BackgroundGraphicColor,
           
            height=500

        )
    return fig 


 
 ###################   NOUVEAU ###################

def create_bar_chart2(df, status,color=blue_color):
    df_filtered = df[df['Nom'] == status]
    
    if df_filtered.empty:
        return {"title": {"text": f"(Pas de données)", "left": 'center'}}

    # Your data processing is correct
    top = df_filtered.groupby(by=['UserName']).agg(
        TempOperation=('TempOperation', lambda x: np.round(np.mean(x) / 60))
    ).reset_index()
    top = top.sort_values(by='TempOperation', ascending=True)

    # Renaming is also correct for ECharts
    top = top.rename(columns={'TempOperation': "value", 'UserName': "name"})
   
    chart_data = top.to_dict(orient='records')
    

    # --- CORRECTED ECHARTS OPTIONS ---
    options = {
        "backgroundColor": GraphicPlotColor,
        "title": {
            "text": f"Temps moyen d'opération {status}", # Made title more descriptive
            "left": 'center',
            "textStyle": {
                "color": GraphicTitleColor
            }
        },
        "color":color,
        "tooltip": {
            "trigger": 'axis',  # 'axis' trigger is better for bar charts
            "axisPointer": {
                "type": 'shadow' 
            },
            # CORRECTED: Removed '{d}%' which is for pie charts
            "formatter": '{b}: {c} min' 
        },
        # Toolbox désactivée car problématique dans Streamlit
        "toolbox": {"show": False},
        # ADDED: Bar charts require an xAxis and yAxis
        "xAxis": {
            "type": 'value', # The axis with numbers
            "boundaryGap": [0, 0.01],
            "axisLabel": {
                "color": GraphicTitleColor,
                "formatter": '{value} min' # Add units to the axis
            }
        },
        "yAxis": {
            "type": 'category', # The axis with names/labels
            # Data for the category axis is automatically taken 
            # from the 'name' field in the series data
            "data": [item['name'] for item in chart_data],
            "axisLabel": {
                "color": GraphicTitleColor
            }
        },
        "series": [
            {
                "name": 'Temps moyen', # A more descriptive series name
                "type": 'bar',
                # REMOVED: 'radius' is not a bar chart property
                "data": chart_data,
                "emphasis": {
                    "focus": 'series',
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ],
        # Optional: Add a grid to control padding
        "grid": {
            "left": '0%',
            "right": '0%',
            "bottom": '3%',
            "containLabel": True
        }
    } 
    return options
    

def create_pie_chart2(df, title='Traitée'):
   
    df=df[df['Nom']==title]
    if df.empty:
        return {"title": {"text": f"(Pas de données)", "left": 'center'}}
    top = df.groupby(by=['UserName'])['Nom'].count().reset_index()
    top=top.rename(columns={'Nom':"value",'UserName':"name"})
    
    chart_data = top.to_dict(orient='records')
    options = {
    "backgroundColor": GraphicPlotColor,
    
    "title": {
        "text": title,
        "left": 'center',
        "textStyle": {
                "color": GraphicTitleColor
            }
    },
    

  # Toolbox désactivée car problématique dans Streamlit
  "toolbox": {"show": False},
  
  
  "tooltip": {"left": "10%", 
   " trigger": 'item',
   "formatter": '{a} <br/>{b}: {c} ({d}%)', # Example of a nice formatter
   
  },
  
  "series": [
    {
      "name": 'Nom et Score',
      "type": 'pie',
      "radius": '50%',
      "data": chart_data,
      "emphasis": {
        "itemStyle": {
          "shadowBlur": 10,
          "shadowOffsetX": 0,
          "shadowColor": 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
} 
    return options
    



def circle(input_text,input_response,list_2color):
    source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]
    })
        
    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            #domain=['A', 'B'],
                            domain=[input_text, ''],
                            # range=['#29b5e8', '#155F7A']),  # 31333F
                            range=list_2color),
                        legend=None)
    ).properties(width=130, height=130)
        
        
    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response}'))
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            # domain=['A', 'B'],
                            domain=[input_text, ''],
                            range=list_2color),  # 31333F
                        legend=None),
    ).properties(width=130, height=130)

    return plot_bg + plot + text 



def ServiceTable(df,status="Traitée"):
    df1=df.copy()
    df1=df1[df1["Nom"]==status]
    agg = df1.groupby(['UserName']).agg(
    TMO=('TempOperation', lambda x: np.round(np.mean(x)/60).astype(int)),NombreTickets=('Nom','size'),
TotalMobile=('IsMobile',lambda x: (x==1).sum())).reset_index()
    
    
    return agg

def plot_metrics(df,status,var):
    agg = ServiceTable(df,status)
    if agg.empty:
        
        Delta = ''
        st.metric(label=status, value=None, delta=None)
    else:

        Value = agg[var]
        Delta = ''
        st.metric(label=status, value=Value, delta=Delta)





def service_congestion(df_queue,color=[green_color, '#12783D'],title=False):
  
   
  agence=df_queue["NomAgence"].iloc[0]
  if not title:
    title=df_queue["NomService"].iloc[0]
  
  HeureFermeture=df_queue['HeureFermeture'].iloc[0]
  queue_length=current_attente(df_queue,agence,HeureFermeture)
  #max_length=df_queue['Capacites'].iloc[0]
  
#   percentage = (queue_length / max_length) * 100

#   chart_color  = ['#FF0000', '#781F16'] if queue_length >= max_length else (['#FFFFFF', '#D5D5D5']  if percentage ==0 else  
#         [green_color, '#12783D'] if percentage < 50 else [blue_clair_color, '#BF6B3D'] if percentage < 80 else [blue_color, '#B03A30']   
#     )
  #title='Vide' if chart_color==['#FFFFFF', '#D5D5D5']  else "Modérement occupée" if chart_color==[green_color, '#12783D'] else "Fortement occupée" if chart_color==[blue_clair_color, '#BF6B3D'] else "Très fortement occupée " if chart_color==[blue_color, '#B03A30'] else 'Congestionnée'
  
  input_text="Congestion"
  input_response=queue_length
  fig=circle(input_text,input_response,list_2color=color)

  st.markdown(
    f"""
    <div style="text-align: center;">
        <p style="font-size: 20px; font-weight: bold;text-decoration: underline;">{title}</p>
    </div>
    """,
    unsafe_allow_html=True
)

 
  
  
  return fig


# Dans shared_code.py

# ==============================================================================
# --- COMPOSANT "CARTE DE STATUT D'AGENCE" ---
# ==============================================================================


# --- 1. Refined get_status function to return emoji, CSS class, text, and plot color ---
def get_status_info(clients, capacite):
    
    if capacite == 0: # Handle division by zero if capacity can be zero
        return "status-led-black"
    
    ratio = clients / capacite
    
    if ratio == 0: 
        return  "status-led-white" 
    elif ratio < 0.5: 
        return  "status-led-green"
    elif ratio < 0.8: 
        return "status-led-yellow"
    elif ratio < 1: 
        return  "status-led-orange"
    else:   
        return  "status-led-red"



# ==============================================================================
# --- FIN DU COMPOSANT ---
# ==============================================================================





def option_agent(df_all_service,df_queue_service):
        df=df_all_service.copy()
        # nom=df["LastName"].iloc[0]
        # prenom=df['FirstName'].iloc[0]
        # nom_service=df["NomService"].iloc[0]
        
        # st.sidebar.markdown(f'SERVICE : :orange[ {nom_service}]')
        # #st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
        # st.sidebar.markdown(f'UTILISATEUR : :blue[  {prenom} {nom}]')
        # #st.sidebar.markdown(f"## Utilisateur :  {prenom} {nom}")
        st.sidebar.markdown("<br><br>", unsafe_allow_html=True) 
        # CSS styling
        st.markdown("""
<style>



[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

        col = st.columns((1.25, 5.25, 1), gap='medium')
        with col[0]:
            
            st.markdown(
    f"""
    <div style="text-align: center;">
        <p style="font-size: 20px; font-weight: bold;text-decoration: underline;">Totaux Opération</p>
    </div>
    """,
    unsafe_allow_html=True
)

            

            plot_metrics(df,'Traitée',"NombreTickets")
            plot_metrics(df,"Passée","NombreTickets")
            plot_metrics(df,"Rejetée","NombreTickets")

            
           

        with col[1]:
            c= st.columns((1.5, 1.5), gap='medium')
            with c[0]:
                fig=stacked_chart(df_all_service,'TempOperation','UserName',"Catégorisation du Temps d'opération")
                st.altair_chart(fig, use_container_width=True)  
            with c[1]:
                fig1=stacked_agent2(df_all_service,type='UserName',titre="Nombre de type d'opération",concern='Type_Operation')
                st.altair_chart(fig1, use_container_width=True)
            
        with col[2]:
            st.markdown(
    f"""
    <div style="text-align: center;">
        <p style="font-size: 20px; font-weight: bold;text-decoration: underline;">File d'Attente</p>
    </div>
    """,
    unsafe_allow_html=True
)

            
           
            fig=service_congestion(df_queue_service,color=['#12783D',green_color])
            st.altair_chart(fig,use_container_width=True)
            
            
        col = st.columns((1.25, 5.25, 1), gap='medium')
        
        with col[0]:
            st.markdown(
    f"""
    <div style="text-align: center;">
        <p style="font-size: 20px; font-weight: bold;text-decoration: underline;">Temps Moy Opération (MINUTES)</p>
    </div>
    """,
    unsafe_allow_html=True
)

            
            
            agg=ServiceTable(df,"Rejetée")
            
            plot_metrics(df,'Traitée',"TMO")
            plot_metrics(df,"Passée","TMO")
            plot_metrics(df,"Rejetée","TMO")
        with col[1]:
            
            fig,_,_,_=area_graph(df_all_service,concern='UserName',time='TempOperation',date_to_bin='Date_Fin',seuil=5,title="Evolution du temps moyen de traitement",couleur='#17becf')
            
            st.plotly_chart(fig, use_container_width=True)
        

        with col[2]:

            fig1=service_congestion(df_queue_filtered,color=['#B03A30',blue_color],title='Agence')
            st.altair_chart(fig1,use_container_width=True)

        st.stop()


############ Page 8 ##################


def filtrer_derniere_semaine_pandas(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    df['Date_Reservation'] = pd.to_datetime(df['Date_Reservation'])
    df['max_date_agence'] = df.groupby('NomAgence')['Date_Reservation'].transform('max')
    start_date_period = df['max_date_agence'] - pd.Timedelta(days=7)
    df_filtered = df[df['Date_Reservation'] >= start_date_period].copy()
    df_filtered.drop(columns=['max_date_agence'], inplace=True)
    return df_filtered

def calculer_metriques_agents_pandas(df_input: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule nb_attente et nb_agent en utilisant Pandas.
    """
    if df_input.empty:
        return pd.DataFrame(columns=list(df_input.columns) + ['nb_attente', 'nb_agent'])
    
    df = df_input.copy()
    # Conversion des dates et création d'un ID unique
    df['Date_Reservation'] = pd.to_datetime(df['Date_Reservation'])
    df['Date_Fin'] = pd.to_datetime(df['Date_Fin'])
    df = df.reset_index().rename(columns={'index': 'row_id'})

    # --- Calcul de 'nb_attente' (méthode événementielle) ---
    starts = df[['Date_Reservation', 'NomAgence']].copy()
    starts.rename(columns={'Date_Reservation': 'time'}, inplace=True)
    starts['change'] = 1

    ends = df[['Date_Fin', 'NomAgence']].copy()
    ends.rename(columns={'Date_Fin': 'time'}, inplace=True)
    ends['change'] = -1

    events = pd.concat([starts, ends])
    # Traiter les départs (-1) avant les arrivées (+1) en cas d'égalité de temps
    events.sort_values(by=['time', 'change'], ascending=[True, False], inplace=True)

    # Calcul de la somme cumulative par agence
    events['active_clients'] = events.groupby('NomAgence')['change'].cumsum()
    
    # On ne garde que les événements d'arrivée pour la jointure
    arrival_events = events[events['change'] == 1].copy()
    arrival_events['nb_attente'] = arrival_events['active_clients'] - 1
    # Assurer que nb_attente n'est jamais négatif
    arrival_events['nb_attente'] = arrival_events['nb_attente'].clip(lower=0)

    # Joindre les résultats au DataFrame original
    df = pd.merge(
        df,
        arrival_events[['time', 'NomAgence', 'nb_attente']],
        left_on=['Date_Reservation', 'NomAgence'],
        right_on=['time', 'NomAgence'],
        how='left'
    ).drop(columns=['time'])

    df.fillna({'nb_attente': 0}, inplace=True)
    return df

# MODIFIÉ : Version robuste de la fonction
def filtrer_derniere_semaine_pandas(df: pd.DataFrame) -> pd.DataFrame: #...
    if df.empty: return df
    df['Date_Reservation'] = pd.to_datetime(df['Date_Reservation'])
    df['max_date_agence'] = df.groupby('NomAgence')['Date_Reservation'].transform('max')
    start_date_period = df['max_date_agence'] - pd.Timedelta(days=7)
    df_filtered = df[df['Date_Reservation'] >= start_date_period].copy()
    df_filtered.drop(columns=['max_date_agence'], inplace=True)
    return df_filtered
def calculer_attente_pandas(df_input: pd.DataFrame) -> pd.DataFrame: #...
    if df_input.empty: return pd.DataFrame(columns=list(df_input.columns) + ['nb_attente'])
    df = df_input.copy(); df['Date_Reservation'] = pd.to_datetime(df['Date_Reservation']); df['Date_Fin'] = pd.to_datetime(df['Date_Fin'])
    starts = df[['Date_Reservation', 'NomAgence']].copy(); starts.rename(columns={'Date_Reservation': 'time'}, inplace=True); starts['change'] = 1
    ends = df[['Date_Fin', 'NomAgence']].copy(); ends.rename(columns={'Date_Fin': 'time'}, inplace=True); ends['change'] = -1
    events = pd.concat([starts, ends]); events.sort_values(by=['time', 'change'], ascending=[True, False], inplace=True)
    events['active_clients'] = events.groupby('NomAgence')['change'].cumsum()
    arrival_events = events[events['change'] == 1].copy(); arrival_events['nb_attente'] = (arrival_events['active_clients'] - 1).clip(lower=0)
    df_final = pd.merge(df, arrival_events[['time', 'NomAgence', 'nb_attente']], left_on=['Date_Reservation', 'NomAgence'], right_on=['time', 'NomAgence'], how='left').drop(columns=['time'])
    df_final.fillna({'nb_attente': 0}, inplace=True); return df_final


# --- 4. FONCTION PRINCIPALE DE LA PAGE (MODIFIÉE) ---
def calculer_moyenne_hebdomadaire(rapport_df: pd.DataFrame) -> pd.DataFrame:
    """Version infaillible avec traduction manuelle des jours de la semaine."""
    df = rapport_df.copy()

    # --- MODIFICATION DÉFINITIVE ---
    # 1. Obtenir les noms des jours en anglais (fonctionne toujours)
    df['Jour_semaine_en'] = df['Heure'].dt.day_name()

    # 2. Dictionnaire de traduction
    jours_traduction = {
        'Monday': 'Lundi', 'Tuesday': 'Mardi', 'Wednesday': 'Mercredi',
        'Thursday': 'Jeudi', 'Friday': 'Vendredi', 'Saturday': 'Samedi', 'Sunday': 'Dimanche'
    }

    # 3. Appliquer la traduction pour créer la colonne en français
    df['Jour_semaine'] = df['Jour_semaine_en'].map(jours_traduction)
    # --------------------------------

    df['Heure_jour'] = df['Heure'].dt.hour
    moyenne_df = df.groupby(['NomAgence', 'Jour_semaine', 'Heure_jour'])['nb_attente'].mean().reset_index()
    moyenne_df.rename(columns={'nb_attente': 'nb_attente_moyen'}, inplace=True)
    
    # L'ordre est maintenant basé sur la colonne française traduite
    jours_ordre = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    moyenne_df['Jour_semaine'] = pd.Categorical(moyenne_df['Jour_semaine'], categories=jours_ordre, ordered=True)

    return moyenne_df.sort_values(by=['NomAgence', 'Jour_semaine', 'Heure_jour'])

# --- NOUVELLE FONCTION POUR LE GRAPHIQUE À BARRES ---
def calculer_charge_journaliere_moyenne(rapport_moyen: pd.DataFrame) -> pd.DataFrame:
    """Agrège la charge horaire moyenne pour obtenir une charge journalière totale."""
    charge_jour = rapport_moyen.groupby('Jour_semaine')['nb_attente_moyen'].sum().reset_index()
    charge_jour.rename(columns={'nb_attente_moyen': 'Charge_Journaliere'}, inplace=True)
    charge_jour = charge_jour.sort_values('Jour_semaine')
    return charge_jour

# REMPLACEZ L'ANCIENNE FONCTION PAR CELLE-CI
def creer_rapport_horaire_pandas_simple(df_metriques: pd.DataFrame) -> pd.DataFrame:
    """
    Version finale :
    1. Crée un rapport horaire strict de 08h à 18h.
    2. Applique une tolérance de 1 heure pour l'activité continue.
    3. Supprime les heures futures du rapport par rapport à l'heure actuelle.
    """
    if df_metriques.empty:
        return pd.DataFrame(columns=['Heure', 'NomAgence', 'nb_attente'])
        
    df = df_metriques[['Date_Reservation', 'NomAgence', 'nb_attente']].copy()
    df.rename(columns={'Date_Reservation': 'Heure'}, inplace=True)
    df.sort_values('Heure', inplace=True)

    df['jour'] = df['Heure'].dt.normalize()
    jours_agences_uniques = df[['jour', 'NomAgence']].drop_duplicates()
    
    grille_globale = []
    for _, row in jours_agences_uniques.iterrows():
        grille_journaliere = pd.date_range(
            start=row['jour'] + pd.Timedelta(hours=8),
            end=row['jour'] + pd.Timedelta(hours=18),
            freq='H'
        )
        grille_globale.append(pd.DataFrame({'Heure': grille_journaliere, 'NomAgence': row['NomAgence']}))

    if not grille_globale:
        return pd.DataFrame(columns=['Heure', 'NomAgence', 'nb_attente'])
        
    grille_df = pd.concat(grille_globale).sort_values('Heure')

    rapport_df = pd.merge_asof(
        grille_df, df[['Heure', 'NomAgence', 'nb_attente']],
        on='Heure', by='NomAgence', direction='backward', tolerance=pd.Timedelta('1 hour')
    )
    
    rapport_df['nb_attente'].fillna(0, inplace=True)
    rapport_df = rapport_df[['Heure', 'NomAgence', 'nb_attente']].astype({'nb_attente': int})
    
    # --- NOUVELLE ÉTAPE : Supprimer les heures futures du rapport ---
    now = pd.Timestamp.now()
    rapport_df_final = rapport_df[rapport_df['Heure'] <= now].copy()
    
    return rapport_df_final

# --- 3. PIPELINE DE TRAITEMENT (INCHANGÉ) ---

def run_analysis_pipeline(_df_source, filtrer_semaine=True):
    if filtrer_semaine: df_a_traiter = filtrer_derniere_semaine_pandas(_df_source)
    else: df_a_traiter = _df_source.copy()
    df_evenements = calculer_attente_pandas(df_a_traiter)
    
    df_rapport = creer_rapport_horaire_pandas_simple(df_evenements)
    return df_rapport


############################ Afluence ##########################


import holidays
from tensorflow.keras.models import load_model
from joblib import load
\

# ==============================================================================
# PARTIE 1 : VOS FONCTIONS DE PRÉTRAITEMENT (INCHANGÉES)
# ==============================================================================
# Ces fonctions sont nécessaires pour préparer les données avant la prédiction.

COUNTRY_CODE = 'SN' 
HOLIDAYS_OBJ = holidays.CountryHoliday(COUNTRY_CODE)

def _apply_common_processing_steps_base(df_raw, all_known_agencies, fixed_min_date=None, fixed_max_date=None, is_actual_data_processing=False, current_time_for_processing=None):
    if not df_raw.empty:
        df_raw.drop_duplicates(subset=['Date_Reservation', 'NomAgence'], inplace=True)
        df_raw.dropna(subset=['Date_Reservation'], inplace=True)
    agencies_in_raw_data = df_raw['NomAgence'].unique().tolist() if not df_raw.empty else []
    agencies_to_process = sorted(list(set(all_known_agencies or []) | set(agencies_in_raw_data)))
    if not agencies_to_process: return None
    df_events_by_agency = pd.DataFrame(columns=['NomAgence', 'nb_attente'], index=pd.to_datetime([]))
    if not df_raw.empty:
        def _calculate_nb_attente_for_group(group_df):
            starts = group_df[['Date_Reservation']].copy(); starts.rename(columns={'Date_Reservation': 'time'}, inplace=True); starts['change'] = 1
            ends = group_df[['Date_Fin']].dropna().copy(); ends.rename(columns={'Date_Fin': 'time'}, inplace=True); ends['change'] = -1
            events = pd.concat([starts, ends]).sort_values('time').reset_index(drop=True)
            events['active_clients'] = events['change'].cumsum()
            events['nb_attente'] = events['active_clients'].shift(1).fillna(0)
            df_events_with_wait = events[events['change'] == 1][['time', 'nb_attente']].rename(columns={'time': 'Date_Reservation'})
            df_events_with_wait['nb_attente'] = df_events_with_wait['nb_attente'].clip(lower=0).astype(int)
            return df_events_with_wait
        temp_df_events_by_agency = df_raw.groupby('NomAgence').apply(_calculate_nb_attente_for_group)
        if not temp_df_events_by_agency.empty:
            df_events_by_agency = temp_df_events_by_agency.reset_index(level='NomAgence')
            df_events_by_agency.set_index('Date_Reservation', inplace=True)
    final_hourly_dfs = []
    system_current_max_date = current_time_for_processing.ceil('H') if is_actual_data_processing else None
    if df_raw.empty:
        default_min_date = fixed_min_date if fixed_min_date else (pd.Timestamp.now().floor('D') + pd.Timedelta(hours=7))
        default_max_date = fixed_max_date if fixed_max_date else system_current_max_date if is_actual_data_processing else (pd.Timestamp.now().ceil('D') - pd.Timedelta(minutes=1))
    else:
        default_min_date = fixed_min_date if fixed_min_date else df_raw['Date_Reservation'].min().floor('D')
        default_max_date_from_raw = fixed_max_date if fixed_max_date else df_raw['Date_Reservation'].max().ceil('D') - pd.Timedelta(minutes=1)
        if is_actual_data_processing: default_max_date = min(system_current_max_date, default_max_date_from_raw)
        else: default_max_date = default_max_date_from_raw
    for agency in agencies_to_process:
        df_agency_events = df_events_by_agency[df_events_by_agency['NomAgence'] == agency]
        if not df_agency_events.empty:
            min_date = df_agency_events.index.min().floor('D')
            max_date_candidate = df_agency_events.index.max().ceil('H')
            if is_actual_data_processing: max_date = min(system_current_max_date, max_date_candidate)
            else: max_date = max_date_candidate
        else: min_date = default_min_date; max_date = default_max_date
        if min_date > max_date: continue
        full_time_index = pd.date_range(start=min_date, end=max_date, freq="T")
        if full_time_index.empty: continue
        df_base = pd.DataFrame(index=full_time_index)
        df_minute = pd.merge_asof(left=df_base, right=df_agency_events.sort_index(), left_index=True, right_index=True)
        df_minute['nb_attente'].fillna(0, inplace=True)
        df_hourly = df_minute['nb_attente'].resample('H').mean().to_frame()
        df_hourly['nb_attente'].fillna(0, inplace=True)
        df_hourly['jour_semaine'] = df_hourly.index.dayofweek
        df_hourly['est_ferie'] = df_hourly.index.to_series().dt.date.isin(HOLIDAYS_OBJ).astype(int)
        df_hourly.loc[~df_hourly.index.hour.isin(range(7, 19)), 'nb_attente'] = 0
        df_hourly.loc[df_hourly.index.dayofweek >= 5, 'nb_attente'] = 0
        df_hourly.loc[df_hourly['est_ferie'] == 1, 'nb_attente'] = 0
        df_hourly['NomAgence'] = agency
        final_hourly_dfs.append(df_hourly)
    if not final_hourly_dfs: return None
    df_global_processed = pd.concat(final_hourly_dfs).set_index('NomAgence', append=True).swaplevel(0, 1).sort_index()
    return df_global_processed

# ==============================================================================
# PARTIE 2 : PIPELINE DE PRÉDICTION (MISE EN CACHE)
# ==============================================================================
# Étape A : Charger les ressources lourdes UNE SEULE FOIS
@st.cache_resource
def load_model_and_scaler():
    """Charge le modèle et le scaler depuis le disque. Mis en cache pour toute la session."""
    
    try:
        model = load_model('final_lstm_model.h5')
        scaler = load('final_scaler.gz')
        return model, scaler
    except Exception as e:
        st.error(f"Erreur critique lors du chargement des fichiers modèle/scaler : {e}")
        return None, None
    

@st.cache_data(show_spinner="Prédiction en cours...")
def run_prediction_pipeline(df_raw_actual, df_raw_past):

    
    """Fonction principale qui exécute tout le pipeline et met en cache les résultats."""
    # On récupère les ressources lourdes depuis leur propre fonction cachée
    model, scaler = load_model_and_scaler()
    if not model or not scaler:
        return None, None, None
    # --- 1. Paramètres ---
    LOOK_BACK = 24
    HOURS_TO_PREDICT = 24
    FEATURES = ['nb_attente', 'jour_semaine', 'est_ferie']
    N_FEATURES = len(FEATURES)
    
    
    CURRENT_TIME = df_raw_actual['Date_Reservation'].max().floor('H')
                  

    # --- 2. Chargement des artefacts ---
    try:
        model = load_model('final_lstm_model.h5')
        scaler = load('final_scaler.gz')
    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle ou du scaler : {e}")
        return None, None, None

    # --- 3. Prétraitement des données ---
    all_agencies = df_raw_actual['NomAgence'].unique().tolist()
    date_for_history = CURRENT_TIME.floor('D') - pd.Timedelta(days=1)
    
    

    df_past_processed = _apply_common_processing_steps_base(df_raw_past, all_agencies, date_for_history.floor('D'), date_for_history.ceil('D') - pd.Timedelta(minutes=1), current_time_for_processing=CURRENT_TIME)
    df_actual_processed = _apply_common_processing_steps_base(df_raw_actual, all_agencies, CURRENT_TIME.floor('D'), is_actual_data_processing=True, current_time_for_processing=CURRENT_TIME)
    
    df_observed = pd.concat([df_past_processed, df_actual_processed])
    df_observed = df_observed[~df_observed.index.duplicated(keep='last')].sort_index()
    
    final_predictions_all_agencies = []
    
    for agency in all_agencies:
        agency_data = df_observed.loc[agency]
        
        # --- 4. Préparation de la séquence d'entrée ---
        last_known_hour = agency_data.index.max()
        start_time_sequence = last_known_hour - pd.Timedelta(hours=LOOK_BACK - 1)
        last_sequence = agency_data.loc[start_time_sequence : last_known_hour]
        
        if len(last_sequence) < LOOK_BACK:
            missing_hours = LOOK_BACK - len(last_sequence)
            pad_index = pd.date_range(start=start_time_sequence - pd.Timedelta(hours=missing_hours), periods=missing_hours, freq='H')
            pad_df = pd.DataFrame(0, index=pad_index, columns=FEATURES)
            pad_df['jour_semaine'] = pad_df.index.dayofweek
            pad_df['est_ferie'] = pad_df.index.to_series().dt.date.isin(HOLIDAYS_OBJ).astype(int)
            last_sequence = pd.concat([pad_df, last_sequence[FEATURES]])
        
        input_features = last_sequence[FEATURES]
        scaled_input = scaler.transform(input_features)
        current_batch = scaled_input.reshape((1, LOOK_BACK, N_FEATURES))
        
        # --- 5. Boucle de prédiction ---
        future_predictions_scaled = []
        for i in range(HOURS_TO_PREDICT):
            pred_scaled = model.predict(current_batch, verbose=0)[0]
            future_predictions_scaled.append(pred_scaled)
            next_hour = last_known_hour + pd.Timedelta(hours=i + 1)
            temp_scaler_input = np.array([[0, next_hour.dayofweek, 1 if next_hour.date() in HOLIDAYS_OBJ else 0]])
            scaled_features = scaler.transform(temp_scaler_input)[0]
            next_step_features = np.array([pred_scaled[0], scaled_features[1], scaled_features[2]])
            next_batch_reshaped = next_step_features.reshape((1, 1, N_FEATURES))
            current_batch = np.append(current_batch[:, 1:, :], next_batch_reshaped, axis=1)

        # --- 6. Post-traitement ---
        future_predictions_scaled_array = np.array(future_predictions_scaled)
        to_inverse = np.zeros((len(future_predictions_scaled_array), N_FEATURES))
        to_inverse[:, 0] = future_predictions_scaled_array.ravel()
        future_predictions_raw = scaler.inverse_transform(to_inverse)[:, 0]
        future_predictions_processed = np.round(future_predictions_raw).clip(0)
        future_dates = pd.date_range(start=last_known_hour + pd.Timedelta(hours=1), periods=HOURS_TO_PREDICT, freq='H')
        df_predictions = pd.DataFrame(future_predictions_processed, index=future_dates, columns=['prediction'])
        df_predictions.loc[~df_predictions.index.hour.isin(range(7, 19)), 'prediction'] = 0
        df_predictions.loc[df_predictions.index.dayofweek >= 5, 'prediction'] = 0
        df_predictions.loc[df_predictions.index.to_series().dt.date.isin(HOLIDAYS_OBJ), 'prediction'] = 0
        df_predictions['NomAgence'] = agency
        final_predictions_all_agencies.append(df_predictions)
        
    if not final_predictions_all_agencies:
        return None, None, None

    df_final_predictions = pd.concat(final_predictions_all_agencies).set_index('NomAgence', append=True).swaplevel(0, 1).sort_index()
    
    
    
     # Affichage des dimensions des DataFrames pour le débogage
    return df_observed, df_final_predictions, CURRENT_TIME

#@st.cache_data
def get_historical_data(_df):
    all_agencies = _df['NomAgence'].unique().tolist()
    return _apply_common_processing_steps_base(_df, all_agencies, is_actual_data_processing=True, current_time_for_processing=_df['Date_Reservation'].max())
