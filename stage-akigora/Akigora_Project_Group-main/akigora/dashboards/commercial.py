# dashboards/commercial.py
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PIL import Image
import base64
from io import BytesIO
from matplotlib.patches import Arc
from matplotlib.patches import Wedge
from matplotlib.animation import FuncAnimation
import calendar
from datetime import datetime
import numpy as np
import seaborn as sns
import folium
from matplotlib.patches import Arc
from matplotlib.patches import Wedge
from matplotlib.animation import FuncAnimation
from ipyleaflet import Map, Marker, Popup
from ipywidgets import widgets
from IPython.display import display
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

from utils.utils import fig_to_base64


def generate_commercial_dashboard(data_profile, data_user, data_intervention):
    
    # Créer une ligne dans le tableau
    row1_col1, row1_col2 = st.columns([2,3])

    # Graphique 1
    with row1_col1:
        # Assurez-vous que la colonne 'date_debut' est au format datetime
        data_intervention['date_debut'] = pd.to_datetime(data_intervention['date_debut'])

        # Gérer les valeurs manquantes dans la colonne 'date_debut'
        data_intervention['date_debut'].fillna(pd.to_datetime('19000101'), inplace=True)

        # Filtrer les années uniques après le remplacement des valeurs manquantes
        unique_years = data_intervention['date_debut'].dt.year.unique()
        unique_years = unique_years[unique_years != 1900]

        # Sélectionner une année via un menu déroulant
        options_years = ['Sélectionnez une année'] + unique_years.astype(str).tolist()

        selected_year = st.selectbox("Sélectionner une année", options=options_years)
        
        # Filtrer les données pour l'année sélectionnée
        if selected_year != 'Sélectionnez une année':
            try:
                # Convertir l'année sélectionnée en entier
                selected_year_int = int(selected_year)

                selected_year_int = selected_year

                # Filtrer les données pour l'année sélectionnée
                missions_par_annee_selected = data_intervention[data_intervention['date_debut'].dt.year == int(selected_year_int)]

                # Calculer le nombre total de missions pour l'année sélectionnée
                total_missions_selected_year = missions_par_annee_selected.shape[0]

                # Afficher le total pour l'année sélectionnée sans le ".0"
                missions_text = f"Nombre total de missions pour {selected_year_int} : <span style='font-size:2em; margin-left:2%; color: white;'>{total_missions_selected_year}</span>"
            except ValueError:
                st.warning("Veuillez sélectionner une année valide.")
        else:
            # Afficher le total de toutes les missions si aucune année n'est sélectionnée
            total_missions_all_years = data_intervention.shape[0]
            missions_text = f"Nombre total de missions : <span style='font-size:2em; margin-left:2%; color: white;'>{total_missions_all_years}</span>"

        # Intégrer les informations dans la div
        st.markdown(
            f"""
            <div style='margin: 20px 0; padding: 2%; background-color: #00bc93; width: 95%; border-radius: 20px; text-align: center; font-size: 1.5rem; color: white;'>
                {missions_text}
            </div>
            """,
            unsafe_allow_html=True
        )


        # Créer une division (div) avec un trait de couleur
        st.markdown(
            """
            <div style="margin: 50px 0 20px 0; padding: 2%; background-color: #f2f6fc;"></div>
            """,
            unsafe_allow_html=True
        )


        ###################################
        # Taux journalier minimum/maximum #
        ###################################

        st.header('Taux journalier minimum/maximum et horaire moyen')

        experts_df = data_profile[data_profile['type'] == 'expert']
        experts_df['createdAt'] = pd.to_datetime(experts_df['createdAt'])
        experts_df[['daily_hourly_prices.daily_price_min', 'daily_hourly_prices.daily_price_max']] = \
            experts_df[['daily_hourly_prices.daily_price_min', 'daily_hourly_prices.daily_price_max']].astype(float)

        experts_df['year'] = experts_df['createdAt'].dt.year
        experts_df['month_year'] = experts_df['createdAt'].dt.to_period('M')

        taux_journalier_min = experts_df['daily_hourly_prices.daily_price_min'].min()
        taux_journalier_max = experts_df['daily_hourly_prices.daily_price_max'].max()

        taux_journalier_par_annee = experts_df.groupby('year').agg(
            daily_price_min=('daily_hourly_prices.daily_price_min', 'min'),
            daily_price_max=('daily_hourly_prices.daily_price_max', 'max')
        )

        taux_journalier_par_mois = experts_df.groupby('month_year').agg(
            daily_price_min=('daily_hourly_prices.daily_price_min', 'min'),
            daily_price_max=('daily_hourly_prices.daily_price_max', 'max')
        )

        # Intégrer les informations dans la div
        st.markdown(
            f"""
            <div style='margin: 20px 0; padding: 1%; background-color: #35424a; width: 75%; border-radius: 20px; text-align: center; font-size: 1.5rem; color: white;'>
                Taux journalier minimum : <span style='font-size:2em; margin-left:2%'>{taux_journalier_min:.2f}</span> €/jr
            </div>
            """,
            unsafe_allow_html=True
        )

        # Intégrer les informations dans la div
        st.markdown(
            f"""
            <div style='margin: 20px 0; padding: 1%; background-color: #7d43c8; width: 65%; border-radius: 20px; text-align: center; font-size: 1.5rem; color: white;'>
                Taux journalier maximum : <span style='font-size:2em; margin-left:2%;'>{taux_journalier_max:.2f} </span>€/jr
            </div>
            """,
            unsafe_allow_html=True
        )



        ######################
        # Taux horaire moyen #
        ######################

        # st.write('Dashboard Commerce - Taux horaire moyen')

        # Assurez-vous que la colonne 'createdAt' est au format datetime
        data_profile['createdAt'] = pd.to_datetime(data_profile['createdAt'])

        # Extraire l'année à partir de la colonne 'createdAt'
        data_profile['year'] = data_profile['createdAt'].dt.year.astype(str)

        data_profile['hourly_rate_mean'] = (data_profile['daily_hourly_prices.daily_price_min'] + data_profile['daily_hourly_prices.daily_price_max']) / 2
        taux_horaire_moyen = data_profile['hourly_rate_mean'].mean()
        taux_horaire_moyen_par_annee = data_profile.groupby('year')['hourly_rate_mean'].mean()
        taux_horaire_moyen_par_mois = data_profile.groupby(data_profile['createdAt'].dt.to_period('M'))['hourly_rate_mean'].mean()

        # Intégrer les informations dans la div
        st.markdown(
            f"""
            <div style='margin: 20px 0; padding: 1%; background-color: #00bc93; width: 50%; border-radius: 20px; text-align: center; font-size: 1.5rem; color: white;'>
                Taux horaire moyen : <span style='font-size:2em; margin-left:2%;'>{taux_horaire_moyen:.2f}</span> €/h        
            </div>
            """,
            unsafe_allow_html=True
        )


    ############################
    # Nb. d'heures de missions #
    ############################
    with row1_col2:
        # Convertir la colonne 'hours_planned_modif' en numérique, gérer les erreurs en remplaçant par 0
        data_intervention['hours_planned'] = pd.to_numeric(data_intervention['hours_planned'], errors='coerce').fillna(0)

        # Convertir les colonnes 'date_debut' et 'date_fin' en datetime
        data_intervention['date_debut'] = pd.to_datetime(data_intervention['date_debut'])
        data_intervention['date_fin'] = pd.to_datetime(data_intervention['date_fin'])

        data_intervention['month_year'] = data_intervention['date_debut'].dt.to_period('M')
        data_intervention['year'] = data_intervention['date_debut'].dt.to_period('Y')

        nb_heures_missions_total = data_intervention['hours_planned'].sum()
        nb_heures_missions_par_mois = data_intervention.groupby('month_year')['hours_planned'].sum()
        nb_heures_missions_par_annee = data_intervention.groupby('year')['hours_planned'].sum()

        # Intégrer les informations dans la div
        st.markdown(
            f"""
            <div style='margin: 20px auto; padding: 1%; background-color: #35424a; width: 70%; border-radius: 20px; text-align: center; font-size: 1.5rem; color: white'>
                Nb. d'heures de missions total : <span style='font-size:2em; margin-left:2%;'>{nb_heures_missions_total:.2f}</span> h        
            </div>
            """,
            unsafe_allow_html=True
        )



        # Assurez-vous que la colonne 'hours_planned' est numérique
        data_intervention['hours_planned'] = pd.to_numeric(data_intervention['hours_planned'], errors='coerce')

        # Filtrer les missions avec des heures planifiées non nulles
        missions_with_hours = data_intervention[data_intervention['hours_planned'].notnull()]

        # Calculer la moyenne des heures planifiées
        average_hours = missions_with_hours['hours_planned'].mean()

        # Intégrer les informations dans la div
        st.markdown(
            f"""
            <div style='margin: 20px auto; padding: 1%; background-color: #00bc93; width: 70%; border-radius: 20px; text-align: center; font-size: 1.5rem; color: white'>
                Durée moyenne des missions : <span style='font-size:2em; margin-left:2%;'>{average_hours:.2f}</span> h        
            </div>
            """,
            unsafe_allow_html=True
        )









        # Bouton radio pour choisir entre les mois et les années
        choice = st.radio("Choisir les données à afficher", ['Par Mois', 'Par Année'])

        # Tracer les données en fonction du choix
        if choice == 'Par Année':
            fig, ax = plt.subplots(figsize=(18, 6))
            ax.bar(nb_heures_missions_par_annee.index.astype(str), nb_heures_missions_par_annee, color='#00BC93')
            ax.set(xlabel='Année', ylabel="Nombre d'heures de missions")
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)
        elif choice == 'Par Mois':
            fig, ax = plt.subplots(figsize=(18, 6))
            ax.bar(nb_heures_missions_par_mois.index.astype(str), nb_heures_missions_par_mois, color='#00BC93')
            ax.set(xlabel='Mois', ylabel="Nombre d'heures de missions")
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)


            # Créer une division (div) avec un trait de couleur
        st.markdown(
            """
            <div style="margin: 50px 0 20px 0; padding: 2%; background-color: #f2f6fc;"></div>
            """,
            unsafe_allow_html=True
        )



    row1_col1, row1_col2 = st.columns([2, 1]) 

    # Graphique 1
    with row1_col1:

         # Bouton radio pour choisir entre les mois et les années
        choice = st.radio("Choisir les données à afficher", ['Par Année', 'Par Mois'], key="unique_key")

        # Tracer les données en fonction du choix
        if choice == 'Par Année':
            st.subheader("Taux horaire moyen par année")
            fig, ax = plt.subplots(figsize=(16, 4))  # Ajustez la taille ici
            ax.bar(taux_horaire_moyen_par_annee.index.astype(str), taux_horaire_moyen_par_annee, color='#00BC93', alpha=0.8, width=0.7)
            ax.set(xlabel='Année', ylabel="Taux horaire moyen")
            ax.tick_params(axis='x', rotation=45, labelsize=5)
            ax.tick_params(axis='y', labelsize=5)
            plt.subplots_adjust(left=0.4, right=0.9, top=0.9, bottom=0.1)  # Ajustez les marges ici
            st.pyplot(fig)
        elif choice == 'Par Mois':
            st.subheader("Taux horaire moyen par mois")
            fig, ax = plt.subplots(figsize=(12, 4))  # Ajustez la taille ici
            ax.bar(taux_horaire_moyen_par_mois.index.astype(str), taux_horaire_moyen_par_mois, color='#00BC93', alpha=0.8, width=0.7)
            ax.set(xlabel='Mois', ylabel="Taux horaire moyen")
            ax.tick_params(axis='x', rotation=45, labelsize=5)
            ax.tick_params(axis='y', labelsize=5)
            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)  # Ajustez les marges ici
            st.pyplot(fig)


# Graphique 2
    with row1_col2:



        st.title("Nombre de clients par type")
        to_plot = data_user.companyOrSchool.value_counts()

        f, ax = plt.subplots(figsize=(2, 2))
        labels_custom = {"school": "Ecole", "company": "Entreprise", "inconnu": "Inconnu"}
        to_plot = to_plot.rename(index=labels_custom)
        colors_company_school = ["#5A5A5A", "#00BC93", "#7D43C8"]

        # Utilisez textprops pour ajuster la taille de la police
        ax.pie(
            to_plot.values,
            labels=to_plot.index,
            autopct="%1.1f%%",
            colors=colors_company_school,
            shadow={"ox": -0.04, "edgecolor": "none", "shade": 0.9},
            textprops={"fontsize": 8},
        )
        ax.set_ylabel("")

        st.pyplot(f)
        to_plot_table = to_plot.rename(index=labels_custom)
        st.write(to_plot_table.reset_index().to_html(index=False, header=False), unsafe_allow_html=True)
        
    # Appliquer la marge à la div mère
    # Créer une division (div) avec un trait de couleur
    st.markdown(
        """
        <div style="margin: 50px 0 20px 0; padding: 1%; background-color: #f2f6fc;"></div>
        """,
        unsafe_allow_html=True
    )  



    # % de clients par ville 
    merged_data_profile_user = pd.merge(data_user, data_profile, left_on='_id', right_on='userId', how='left')

    # Filtrer les données pour exclure les lignes avec des valeurs NaN dans 'ville'
    merged_data_profile_user = merged_data_profile_user.dropna(subset=['ville'])

    pourcentage_par_ville = merged_data_profile_user['ville'].value_counts(normalize=True) * 100


    pourcentage_par_ville = pourcentage_par_ville.round(2)

    # Tableau
    # st.write("Pourcentage de clients par ville")
    # st.write(pourcentage_par_ville.reset_index().to_html(index=False, header=False), unsafe_allow_html=True)

    # % de clients par région 
    merged_data_profile_user = pd.merge(data_user, data_profile, left_on='_id', right_on='userId', how='left')

    merged_data_profile_user = merged_data_profile_user.dropna(subset=['region'])

    pourcentage_par_region = merged_data_profile_user['region'].value_counts(normalize=True) * 100
    pourcentage_par_region = pourcentage_par_region.round(2)

    # Tableau
    # st.write("Pourcentage de clients par région")
    # st.write(pourcentage_par_region.reset_index().to_html(index=False, header=False), unsafe_allow_html=True)


    # Intégration de la carte dans Streamlit avec une fenêtre centrée
    st.markdown("<div style='text-align: center;'><h2>Pourcentage de client par ville / région et leurs positions</h2></div>", unsafe_allow_html=True)

    row1_col1, row1_col2, row1_col3= st.columns([1,2,1])

    with row1_col1:
        pass

    with row1_col2:
        # Création de la carte centrée sur la première ville (à ajuster selon vos besoins)
        if not merged_data_profile_user.empty:
            map_center = [merged_data_profile_user['Latitude'].iloc[0], merged_data_profile_user['Longitude'].iloc[0]]
            my_map = folium.Map(location=map_center, zoom_start=5.2)

            # Création d'un cluster de marqueurs
            marker_cluster = MarkerCluster().add_to(my_map)

            # Ajout des marqueurs pour chaque ville avec le pourcentage d'utilisateurs
            for index, row in merged_data_profile_user.iterrows():
                pourcentage_ville = pourcentage_par_ville.get(row['ville'], 0)
                pourcentage_region = pourcentage_par_region.get(row['region'], 0)
                popup_text = f"{row['ville']}: {pourcentage_ville:.2f}%, {row['region']}: {pourcentage_region:.2f}%"
                folium.Marker([row['Latitude'], row['Longitude']],
                            popup=popup_text).add_to(marker_cluster)

            # Intégration de la carte dans Streamlit avec une fenêtre centrée
            my_map_html = folium_static(my_map, width=850, height=400)

            # Ajouter du style CSS pour centrer la carte sur la page
            st.markdown(
                f"""
                <style>
                    #{my_map_html} {{
                        margin: auto !important;
                        display: block !important;
                        width: 80%;  /* Ajustez la largeur selon vos besoins */
                    }}
                </style>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning("Aucune donnée disponible pour créer la carte.")

    with row1_col3:
        pass
