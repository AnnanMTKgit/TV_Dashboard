# pages/3_📊_Tableau_Global.py
import streamlit as st
from shared_code import *
from st_aggrid.shared import JsCode

# Mettre le minuteur en place dès le début de la page
setup_auto_refresh(interval_minutes=10)

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

st.markdown("<h1 style='text-align: center;font-size:1.5em;'>Tableau Global</h1>", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

Kpi=df_all_filtered.groupby("NomService")["UserName"].nunique().reset_index()
Kpi = Kpi.rename(columns={"UserName": "Nombre_Agents"})



if not Kpi.empty:
    cols = st.columns(len(Kpi))  # une colonne par service
    for i, row in Kpi.iterrows():
        with cols[i]:
            st.metric(label="Nombre Agents " + row["NomService"], value=row["Nombre_Agents"])

st.markdown("<br/>", unsafe_allow_html=True)

# --- Affichage du tableau ---
(
    agence_mensuel,
    agence_global,
    reseau_mensuel,
    reseau_global
) = AgenceTable2(df_all_filtered, df_queue_filtered)


# --- 2. Création du sélecteur de vue dans l'interface Streamlit ---

view_options = {
    "Statistiques Globales par Agence": (agence_global, "Global_Agence"),
    "Statistiques Mensuelles par Agence": (agence_mensuel, "Mensuel_Agence"),
    "Statistiques Globales du Réseau ": (reseau_global, "Global_Reseau"),
    "Statistiques Mensuelles du Réseau ": (reseau_mensuel, "Mensuel_Reseau"),
}

# Créez le selectbox pour que l'utilisateur choisisse la vue
selected_view_name = st.selectbox(
    "Choisissez la vue à afficher :",
    options=list(view_options.keys())
)

# Récupérez le DataFrame et le préfixe de fichier correspondant au choix
df_to_display, file_prefix = view_options[selected_view_name]


# --- 3. Affichage du tableau dynamique basé sur la sélection ---
if not df_to_display.empty:
    st.markdown(f"### {selected_view_name}")
    
    # Bouton de téléchargement principal (pour la table complète)
    buffer = create_excel_buffer(df_to_display)
    st.download_button(
        label="📥 Télécharger la vue actuelle en Excel",
        data=buffer,
        file_name=f'{file_prefix}_{st.session_state.start_date}_to_{st.session_state.end_date}.xlsx',
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    

    # --- 3. JavaScript for Conditional Formatting ---
    # Use JsCode to define JavaScript functions for cell styling
    # Green background for "Temps Moyen d'Operation (MIN)" > 5
    cellsytle_jscode_operation = JsCode("function(params) {if (params.value > 5) {return {'backgroundColor': '#BBD600'}}return {'backgroundColor': 'white'}};").js_code

    # Blue background for "Temps Moyen d'Attente (MIN)" > 15
    cellsytle_jscode_attente = JsCode("function(params) {if (params.value > 15) {return {'backgroundColor': '#1B698D','color':'white'}}return {'backgroundColor': 'white'}};").js_code

    
    # Build the GridOptions
    gb = GridOptionsBuilder.from_dataframe(df_to_display)

    # Appliquer le style conditionnel
    gb.configure_column("Temps Moyen d'Operation (MIN)", cellStyle=cellsytle_jscode_operation)
    gb.configure_column("Temps Moyen d'Attente (MIN)", cellStyle=cellsytle_jscode_attente)

    # Configuration par défaut pour toutes les colonnes
    gb.configure_default_column(
        flex=1,
        minWidth=180, # Légère réduction pour une meilleure vue d'ensemble
        groupable=True,
        enableRowGroup=True,
        aggFunc='sum',
        editable=False,
        filter=True
    )
     # Cacher Longitude et Latitude SEULEMENT si elles existent dans le DataFrame
    # Ceci évite les erreurs pour les vues "Réseau"
    if 'Longitude' in df_to_display.columns:
        gb.configure_column('Longitude', hide=True)
    if 'Latitude' in df_to_display.columns:
        gb.configure_column('Latitude', hide=True)
    




    custom_css = {
    ".ag-theme-alpine.headers1": {
        "--ag-header-height": "30px",
        "--ag-header-foreground-color": "white",
        "--ag-header-background-color": "black",
        "--ag-header-cell-hover-background-color": "rgb(80, 40, 140)",
        "--ag-header-cell-moving-background-color": "rgb(80, 40, 140)",
    },
    ".ag-theme-alpine.headers1 .ag-header": {
        "font-family": "cursive"
    },
    ".ag-theme-alpine.headers1 .ag-header-group-cell": {
        "font-weight": "normal",
        "font-size": "22px"
    },
    ".ag-theme-alpine.headers1 .ag-header-cell": {
        "font-size": "18px"
    }
}


   
    
    # Ajouter les autres fonctionnalités interactives
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True)
    gb.configure_side_bar()

    gridOptions = gb.build()

    # Afficher la table AgGrid
    grid_response = AgGrid(
        df_to_display,
        height=500,
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        theme='alpine',
        custom_css=custom_css
    )

    # --- Gestion de la sélection pour le téléchargement partiel ---
    selected_rows = grid_response['selected_rows']
    
    if selected_rows is not None and not selected_rows.empty:
        selected_df = pd.DataFrame(selected_rows)
        selected_df.drop(columns=['_selectedRowNodeInfo'], inplace=True, errors='ignore')
        
        st.write("Télécharger la sélection en format Excel :")
        
        buffer_selected = create_excel_buffer(selected_df)
        st.download_button(
            label="📥 Télécharger la sélection",
            data=buffer_selected,
            file_name=f'Selection_{file_prefix}_{st.session_state.start_date}_to_{st.session_state.end_date}.xlsx',
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key='download_selected' # Clé unique pour éviter les conflits
        )
    else:
        st.info("Sélectionnez une ou plusieurs lignes dans le tableau pour télécharger une sélection.")

else:
    # Message si le DataFrame sélectionné est vide
    st.warning(f"Aucune donnée disponible pour la vue : '{selected_view_name}'.")