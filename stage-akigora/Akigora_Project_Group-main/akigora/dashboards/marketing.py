# dashboards/marketing.py
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
from utils.utils import fig_to_base64
import plotly.graph_objects as go


def generate_marketing_dashboard(data_recommendation, data_search, data_profile, data_user, data_consultation, data_newsletter):

    df = data_recommendation.copy()
####################
    non_rensigne = data_profile['experienceTime'].isnull().sum()/data_profile.shape[0]
    if non_rensigne > 0:
        st.warning(str(round(non_rensigne,1))+"% des expert au nbe anne de reference non renseigné")
        
        
                ##### TRANSFO DATA
        
    dict_exp = {'Inconnu':0,
                'mois de 10 ans':1,
                'moins de 10 ans':1,
                '10 à 20 ans':2,             
                '20 à 30 ans':3, 
                '+ de 30 ans':4,
                'Entre 5 et 10 ans':1, 
                'Entre 10 et 15 ans':2, 
                'Entre 15 et 25 ans':3,
                '+ de 25 ans':4, 
                }
            # creation nouvelle colonne necessaire?
    data_profile.replace({"experienceTime": dict_exp}, inplace=True)
            # prepare data à plotter
    to_plot = data_profile.experienceTime.value_counts().sort_index()
    dict_label = {0:'inconnu',
                    1:'entre 5 et 10',
                    2:'entre 10 et 15',
                    3:'entre 15 et 25',
                    4:'25 ans et plus'}
    #st.markdown("<div style='text-align:center; color:white; background-color:#35424a; padding:10px;'>Nombre de morts dans le Titanic: X</div>", unsafe_allow_html=True)
    row1_col1, row1_col2, row1_col3 = st.columns(3)

    with row1_col1:
            #Nb. de recherche
        # Convert 'timestamp' column to datetime format
        data_search['timestamp'] = pd.to_datetime(data_search['timestamp'])

        # Calculate the number of researches for the previous year (n-1)
        current_year = datetime.now().year
        previous_year_researches = data_search[data_search['timestamp'].dt.year == current_year - 1].shape[0]

        # Calculate the delta
        delta_researches = data_search.shape[0] - previous_year_researches

        # print the st.metric 
        st.metric(label='Nb. de recherches cette année', value=data_search.shape[0], delta=f"{delta_researches} Evolution par rapport à l'année dernière ")

        # Convert 'timestamp' column to datetime format
        data_search['timestamp'] = pd.to_datetime(data_search['timestamp'])

        # Calculate the number of researches for the current month
        current_month_researches = data_search[data_search['timestamp'].dt.month == datetime.now().month].shape[0]

        # Calculate the number of researches for the previous month (n-1)
        previous_month_researches = data_search[
            (data_search['timestamp'].dt.year == datetime.now().year - 1) &
            (data_search['timestamp'].dt.month == datetime.now().month)
        ].shape[0]
        # Calculate the delta
        delta_researches = current_month_researches - previous_month_researches

        # Print the st.metric
        st.metric(label='Nb. de recherches ce mois-ci', value=current_month_researches, delta=f"{delta_researches} Evolution par rapport au même mois l'année dernière ")

        #Nb. moyen d'années d'expérience
    with row1_col2:
        # Ensure 'updatedAt' is of datetime type
        data_profile['updatedAt'] = pd.to_datetime(data_profile['updatedAt'])

        # Get the current year
        current_year = datetime.now().year

        # Calculate the mean of "experienceTime" for the current year
        mean_experience_current_year = round(data_profile[data_profile['updatedAt'].dt.year == current_year]
                                            .replace({"experienceTime": {1: 5, 2: 15, 3: 25, 4: 35}})
                                            .loc[(data_profile['experienceTime'] != 0), 'experienceTime'].mean(), 2)

        # Calculate the mean of "experienceTime" for the previous year (n-1)
        mean_experience_previous_year = round(data_profile[data_profile['updatedAt'].dt.year == current_year - 1]
                                            .replace({"experienceTime": {1: 5, 2: 15, 3: 25, 4: 35}})
                                            .loc[(data_profile['experienceTime'] != 0), 'experienceTime'].mean(), 2)

        # Calculate the delta
        delta_experience = mean_experience_current_year - mean_experience_previous_year
        # Display metrics using st.metric
        st.metric(label='Nb. moyen d\'années d\'expérience cette année',
                value=mean_experience_current_year,
                delta=f"{round(delta_experience,2)} Évolution par rapport à l\'année précédente")


        #% d'abonnés à la newsletter
    with row1_col3:
        # Ensure 'createdAt' is of datetime type
        data_newsletter['createdAt'] = pd.to_datetime(data_newsletter['createdAt'], errors='coerce')
        data_user['createdAt'] = pd.to_datetime(data_user['createdAt'], errors='coerce')

        # Get the current month and year
        current_month = datetime.now().month
        current_year = datetime.now().year

        # Calculate the total percentage of newsletter subscriptions
        total_subscription_percent = round(100 * data_newsletter['_id'].nunique() / data_user['_id'].nunique(), 2)

        # Calculate the percentage of newsletter subscriptions for the current month
        current_month_subscription_percent = round(100 * data_newsletter[data_newsletter['createdAt'].dt.month == current_month].shape[0] / data_user.shape[0], 2)

        # Calculate the percentage of newsletter subscriptions for the previous month (n-1)
        previous_month_subscription_percent = round(100 * data_newsletter[
            (data_newsletter['createdAt'].dt.year == current_year) &
            (data_newsletter['createdAt'].dt.month == current_month - 1)
        ].shape[0] / data_user.shape[0], 2)

        # Calculate the delta as the evolution from the last month
        delta_subscription_percent = current_month_subscription_percent - previous_month_subscription_percent

        # Display metrics using st.metric
        st.metric(label='Pourcentage d\'abonnés à la newsletter (Total)',
                value=total_subscription_percent)

        st.metric(label=f'Pourcentage d\'abonnés à la newsletter (Mois en cours)',
                value=current_month_subscription_percent,
                delta=f"{round(delta_subscription_percent, 2)} Évolution par rapport au mois précédent ")
    
    # A AJOUTER DOCU=================================================================================================================================
    # IMPOSSIBLE DE CALCULER UNE MOYENNE AVEC DES DONNEES DISCRETES
    st.warning('Attention ! Impossible de calculer une moyenne avec des tranches d\'années')
    # Créer une ligne dans le tableau
    row2_col1, row2_col2, row2_col3 = st.columns(3)

    #Répartition des experts / statut juridique en %
    with row2_col1:       
        st.markdown("**Répartition des experts par statut juridique**")

        
        # Regrouper les données par statut juridique et compter les occurrences
        status_count = data_user['company.type'].value_counts()
        
        # Créer un graphique à barres avec Seaborn
        plt.figure(figsize=(8, 6))
        sns.barplot(x=status_count.index, y=status_count.values)
        plt.xlabel('Statut Juridique')
        plt.ylabel("Nombre d'experts")
        plt.title('Répartition des experts par statut juridique')
        plt.xticks(rotation=45)
        
        # Ajouter des étiquettes avec les valeurs chiffrées
        for index, value in enumerate(status_count):
            plt.text(index, value + 0.5, str(value), ha='center', va='bottom')
        
        # Afficher le graphique dans Streamlit en utilisant st.pyplot()
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot()


        
    #Répartition des experts / nbe anné exp %
    with row2_col2:
        st.markdown("**Répartition par tranche d'années d'expérience**")

        
                # affiche figure
         # Create a pie chart
        fig = px.pie(names=to_plot.index.map(dict_label),
                    values=to_plot.values)
        #f, ax = plt.subplots(figsize=(3,3))
        #ax.pie(to_plot.values, labels=to_plot.index.map(dict_label), autopct='%1.1f%%',
               #shadow={'ox': -0.04, 'edgecolor': 'none', 'shade': 0.9})
        #ax.set_ylabel("")
        # Display the pie chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)
        #st.pyplot(f)

       


    #Nb. moyen d'années d'expérience
        
    with row2_col3:
        with st.container(border=True):
            st.markdown("**Nb. de vues par expert (Filtres au choix)**")

            data_consultation.createdAt = pd.to_datetime(data_consultation.createdAt)
            data_consultation['year'] = data_consultation.createdAt.dt.year

            annee = st.multiselect('select', data_consultation.year.unique())
            type_viewer = st.selectbox('select', data_consultation.viewerType.unique())
            nbe_expert = st.number_input('Nombre d\'experts', value=5, step=1)
            nbe_expert = int(nbe_expert)
            to_show = data_consultation.loc[(data_consultation.year.isin(annee))&(data_consultation.viewerType == type_viewer)]
            st.table(pd.DataFrame(to_show.groupby("expertId")['viewerType'].count().sort_values(ascending=False)[:nbe_expert]))
            
 

    row3_col1, row3_col2 = st.columns([2, 1])
    #Répartition des experts / type de diplôme le plus haut obtenu en %
    with row3_col1:
        with st.container(border=True):

            # Exclusion des NaN
            degree_level = data_profile["studyLevel"].unique()
            degree_level = [level for level in degree_level if pd.notna(level)]

            # Sélectionner le niveau de diplôme
            selected_level = st.selectbox("",
                                        ["Sélectionnez un niveau de diplôme"] + list(degree_level),
                                        key="dropdown")

            # Vérifier si un niveau de diplôme est sélectionné
            if selected_level != "Sélectionnez un niveau de diplôme":
                # Filtrer le DataFrame en fonction du niveau de diplôme sélectionné
                filtered_df = data_profile[data_profile["studyLevel"] == selected_level]

                # Calcul du %
                percentage = len(filtered_df) / len(data_profile[data_profile["studyLevel"].notna()]) * 100

                st.markdown(f"Le pourcentage de personnes avec le diplôme **{selected_level}** est de "
                            f"<span style='color: #00bc93; font-weight: bold;'>{percentage:.2f}%</span>",
                            unsafe_allow_html=True)


            #GRAPHIQUE
            distribution = data_profile["studyLevel"].value_counts(normalize=True) * 100

            fig = px.bar(x=distribution.index, y=distribution.values,
                        labels={"x": "Type de Diplôme", "y": "Pourcentage d'experts"},
                        title="Répartition des experts par type de diplôme",
                        color=distribution.index,
                        color_discrete_map={"BAC": "red", "BAC +2": "blue", "BAC +3": "green", "BAC +4": "purple", "BAC +5": "orange"})

            st.plotly_chart(fig)
        
    #Répartition des entreprises / type de structure en %
    with row3_col2:
        st.markdown("**Répartition des entreprises / type de structure en %**")
        to_plot = data_user.companyOrSchool.value_counts()
        fig = px.pie(names=to_plot.index,
                    values=to_plot.values)
        st.plotly_chart(fig, use_container_width=True)

    with st.container(border=True):
        row4_col1, row4_col2 = st.columns([2, 1])

        #Répartition des experts / type d'expertise 
        with row4_col2:
            st.markdown("**Liste des experts par domaine d'expertise sélectionné**")
            domain_ = st.selectbox('Select a variable', data_profile.domains.unique())
            st.text(data_profile.loc[(data_profile.domains == domain_)])

        with row4_col1:
            st.markdown("**Répartition des experts / Domaine d'expertise supérieur à 1 %**")
            to_plot = data_profile['domains'].value_counts()
            labels = to_plot.index
            values = to_plot.values

            # Calculate percentages
            percentages = values / sum(values) * 100

            # Filter labels and values based on the threshold (1%)
            filtered_labels = [label for label, percent in zip(labels, percentages) if percent >= 1]
            filtered_values = [value for value, percent in zip(values, percentages) if percent >= 1]

            fig = go.Figure(data=[go.Pie(labels=filtered_labels, values=filtered_values, hole=0.5, textinfo='label+percent')])

            # Customize layout
            fig.update_layout(
                showlegend=False,  # Hide legend
                annotations=[
                    {
                        'font': {'size': 14},
                        'showarrow': False,
                        'text': 'Domaines',
                        'x': 0.5,
                        'y': 0.5
                    }
                ]
            )

            st.plotly_chart(fig)

    with st.container(border=True):

        row5_col1, row5_col2 = st.columns([2, 1])

        # Graphe
        with row5_col1:
            st.markdown("**Répartition des experts / Secteur d'expertise supérieur à 1%**")
            to_plot = data_profile['sectors'].value_counts()
            labels = to_plot.index
            values = to_plot.values

            # Calculate percentages
            percentages = values / sum(values) * 100

            # Filter labels and values based on the threshold (1%)
            filtered_labels = [label for label, percent in zip(labels, percentages) if percent >= 1]
            filtered_values = [value for value, percent in zip(values, percentages) if percent >= 1]

            fig = go.Figure(data=[go.Pie(labels=filtered_labels, values=filtered_values, hole=0.5, textinfo='label+percent')])

            # Customize layout
            fig.update_layout(
                showlegend=False,  # Hide legend
                annotations=[
                    {
                        'font': {'size': 14},
                        'showarrow': False,
                        'text': 'Domaines',
                        'x': 0.5,
                        'y': 0.5
                    }
                ]
            )

            st.plotly_chart(fig)


        #table    
        with row5_col2:
            st.markdown("**Liste des experts par secteur d'expertise sélectionné**")
            sector_ = st.selectbox('Select a variable', data_profile.sectors.unique())
            st.text(data_profile.loc[data_profile.sectors == sector_])




    row6_col1, row6_col2, row6_col3 = st.columns(3)

    # Graphe
    with row6_col3:
        st.markdown("**Nb. de recherche par date**")
        data_search.keywords = data_search.keywords.apply(lambda x: str(x).lower().strip())
        data_search['timestamp'] = pd.to_datetime(data_search['timestamp'])
        data_search['date'] = data_search.timestamp.dt.strftime("%m/%Y")
        to_plot = pd.DataFrame(data_search.groupby('date')['keywords'].count()).reset_index()
        to_plot.date = pd.to_datetime(to_plot.date)

        sns.lineplot(data = to_plot, x='date', y='keywords')
        plt.ylabel("Nombre de recherches")
        plt.xticks(rotation=45)
        st.pyplot()

    # Graphe et filtres
    with row6_col1:
        with st.container(border=True):

            st.markdown("**Afficher les mots clés les plus utilisés par années et trimestres**")
            st.markdown("***Il faut choisir au moins une année ET un trimestre pour qu'ils s'affichent sur le graphe***")
            data_search['year'] = data_search['timestamp'].dt.year
            data_search['trimestre'] = data_search['timestamp'].dt.month.apply(lambda x: 1 + (x - 1) // 3)

            annee = st.multiselect('Choisir année', data_search['year'].unique())
            trimestre = st.multiselect('Choisir trimestre', data_search['trimestre'].unique())
            nbe_mot_cle = st.number_input('Nombre de mots clés', value=5, step=1)
            nbe_mot_cle = int(nbe_mot_cle)

            to_plot = data_search.loc[~(data_search.keywords == 'nan') & (data_search['year'].isin(annee)) & (data_search['trimestre'].isin(trimestre))]['keywords']
            
            # Count occurrences of each keyword
            keyword_counts = to_plot.value_counts()

            # Plot the bar chart
            plt.figure(figsize=(8, 6))
            sns.barplot(x=keyword_counts.head(nbe_mot_cle).values, y=keyword_counts.head(nbe_mot_cle).index)
            plt.xlabel('Nombre d\'occurrences')
            plt.title('Mots clés les plus utilisés')
            st.pyplot()

    with row6_col2:
        with st.container(border=True):

            st.markdown("**Afficher les mots clés les plus utilisés par années et trimestres**")
            st.markdown("***Il faut choisir au moins une année ET un trimestre pour qu'ils s'affichent sur le graphe***")
            data_search['year'] = data_search['timestamp'].dt.year
            data_search['trimestre'] = data_search['timestamp'].dt.month.apply(lambda x: 1 + (x - 1) // 3)

            annee = st.multiselect('Choisir année ', data_search['year'].unique())
            trimestre = st.multiselect('Choisir trimestre ', data_search['trimestre'].unique())
            nbe_mot_cle = st.number_input('Nombre de mots clés ', value=5, step=1)
            nbe_mot_cle = int(nbe_mot_cle)

            to_plot = data_search.loc[~(data_search.keywords == 'nan') & (data_search['year'].isin(annee)) & (data_search['trimestre'].isin(trimestre))]['keywords']
            
            # Count occurrences of each keyword
            keyword_counts = to_plot.value_counts()

            # Plot the bar chart
            plt.figure(figsize=(8, 6))
            sns.barplot(x=keyword_counts.head(nbe_mot_cle).values, y=keyword_counts.head(nbe_mot_cle).index)
            plt.xlabel('Nombre d\'occurrences')
            plt.title('Mots clés les plus utilisés')
            st.pyplot()
