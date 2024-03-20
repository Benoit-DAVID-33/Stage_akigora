# dashboards/rh.py
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


def generate_rh_dashboard(data_profile, data_user, data_intervention, data_recommendation):  

    # Updated extract_name function
    def extract_name(json_str):
        try:
            json_str = str(json_str)
            json_data = json.loads(json_str)
            return json_data
        except json.JSONDecodeError:
            return {}

    # Updated has_ref function
    def has_ref(json_obj):
        try:
            if 'name' in json_obj[0]:
                name = json_obj[0]['name']
                if name == '':
                    return False
                else:
                    return True
            else:
                return False
        except:
            return False

    # Vérifier si la colonne 'has_ref' existe dans le DataFrame
    # if 'has_ref' not in data_profile.columns:
    data_profile["has_ref"] = data_profile.references.apply(extract_name).apply(has_ref)

    # Intégrer les informations dans la div
    st.markdown(
        f"""
        <div style='display: flex; justify-content: space-between;'>
            <div style='text-align:center; color:white; background-color:#00bc93; padding:2% 3%; width: 30%; height: 3%; margin: 10px; border-radius: 20px;'>
                Nb. d'experts inscrits :
                <span style='font-size:2em; margin-left:2%;'>{len(data_profile.loc[data_profile.type == 'expert'])}</span>
            </div>
            <div style='text-align:center; color:white; background-color:#7d43c8; padding:1% 3%; width: 30%; height: 3%; margin: 10px; border-radius: 20px;'>
                % d'experts avec références : 
                <span style='font-size:2em; margin-left:2%;'>{round(100* len(data_profile.loc[data_profile.has_ref == True])/data_profile.shape[0],2)}</span>
                <br>
                % d'experts sans références :
                <span style='font-size:2em; margin-left:2%;'>{round(100* len(data_profile.loc[data_profile.has_ref == False])/data_profile.shape[0],2)}</span>
            </div>
            <div style='text-align:center; color:white; background-color:#00bc93; padding:2% 4%; width: 30%; height: 3%; margin: 10px; border-radius: 20px;'>
                % Profil complété à 100% : 
                <span style='font-size:2em; margin-left:2%;'>{len(data_profile.loc[(data_profile.type == 'expert')
                            & (data_profile.done == True)
                            & (data_profile.isFake == False)
                            & (data_profile.percentage == 100)])}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    #################################################
    # GRAPHIQUE : Nombre d'expert inscrits par date #
    #################################################

    #### DEBUT ####

    st.markdown("**Nombre d'experts**")

    selected_y_axis = st.radio("Statut :", ['Inscrits', 'Désinscrits'])

    # Convert min and max values to timestamp
    min_date = pd.to_datetime(data_profile['createdAt'].min())
    max_date = pd.to_datetime(data_profile['createdAt'].max())

    # Date range slider
    try:
        start_date, end_date = st.slider(
            "Période :",
            min_value=min_date.to_pydatetime(),
            max_value=max_date.to_pydatetime(),
            value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
            format="DD-MM-YYYY",  # Specify the format of the date
        )
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.stop()

    # Select data within the chosen date range
    try:
        selected_data = data_profile.loc[
            (data_profile['type'] == 'expert')
            & (data_profile['done'] == (selected_y_axis == 'Inscrits'))
            & (data_profile['createdAt'] >= start_date)
            & (data_profile['createdAt'] <= end_date),
            'createdAt'
        ]
    except Exception as e:
        st.error(f"An error occurred while selecting data: {e}")
        st.stop()

    # Create the graph with the selected data
    try:
        fig = px.histogram(
            selected_data,
            nbins=30,
            color_discrete_sequence=['#00A08B']
        )

        fig.update_layout(
            xaxis_title='Date de création',
            yaxis_title=f"Nombre d'experts {selected_y_axis.lower()}",
            bargap=0.05,
            width=800,
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred while creating the graph: {e}")
        st.stop()

    #### FIN ####

    row1_col1, row1_col2 = st.columns(2)

    ######################################################
    # GRAPHIQUE : % d'experts par domaine d'intervention #
    ######################################################

    #### DEBUT ####

    with row1_col1:
        
        st.markdown("**% d'experts par domaine d'intervention**")
        
        # Date range slider with unique key
        try:
            start_date, end_date = st.slider(
                "Période :",
                min_value=min_date.to_pydatetime(),
                max_value=max_date.to_pydatetime(),
                value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
                format="DD-MM-YYYY",  # Specify the format of the date
                key="date_range_slider"  # Unique key
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()

        # Select data within the chosen date range
        try:
            selected_data = data_profile.loc[
                (data_profile['type'] == 'expert')
                & (data_profile['done'] == (selected_y_axis == 'Inscrits'))
                & (data_profile['createdAt'] >= start_date)
                & (data_profile['createdAt'] <= end_date),
                ['createdAt', 'domains']  # Keep 'domain' column
            ].reset_index(drop=True)
        except Exception as e:
            st.error(f"An error occurred while selecting data: {e}")
            st.stop()

        # Plot bar chart if there is data
        if not selected_data.empty:
            try:
                plt.figure(figsize=(4, 5))
                ax1 = selected_data['domains'].value_counts()[:20].sort_values(ascending=True).plot.barh()
                st.pyplot(ax1.figure)
            except Exception as e:
                st.error(f"An error occurred while creating the bar chart: {e}")
        else:
            st.warning("No data available for the selected date range.")

    ### FIN ###

    ######################################
    # GRAPHIQUE : % d'experts par région #
    ######################################

    #### DEBUT ####

    with row1_col2:   
       
        st.markdown("**% d'experts**")
        
        selected_display = st.radio("Afficher par :", ['Region', 'Ville', 'Departement'])
       
        # Date range slider with unique key
        try:
            start_date, end_date = st.slider(
                "Période :",
                min_value=min_date.to_pydatetime(),
                max_value=max_date.to_pydatetime(),
                value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
                format="DD-MM-YYYY",  # Specify the format of the date
                key="date_range_slider_2"  # Unique key
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()

        # Select data within the chosen date range
        try:
            selected_data = data_profile.loc[
                (data_profile['type'] == 'expert')
                & (data_profile['done'] == (selected_y_axis == 'Inscrits'))
                & (data_profile['createdAt'] >= start_date)
                & (data_profile['createdAt'] <= end_date),
                ['createdAt', selected_display]  # Keep selected column
            ].reset_index(drop=True)
        except Exception as e:
            st.error(f"An error occurred while selecting data: {e}")
            st.stop()

        # Display the graph
        if not selected_data.empty:
            try:
                plt.figure(figsize=(4, 5))
                ax2 = selected_data[selected_display].value_counts()[:20].sort_values(ascending=True).plot.barh()
                ax2.set_xlabel("Nombre d'experts")
                ax2.set_ylabel(selected_display)
                plt.show()
            except Exception as e:
                st.error(f"An error occurred while creating the bar chart: {e}")
        else:
            st.warning("No data available for the selected date range.")
        
    ### FIN ###
    
    #####################
    # AFFICHAGE VALEURS #
    #####################
        
        # Utilisation d'un conteneur HTML avec style de débordement
        st.markdown(
            f"""
            <div style="overflow-x: auto; max-height: 400px;">
                <figure class="streamlit-figure" style="width: 100%;">
                    <figcaption class="streamlit-figure-caption" style="text-align: left;">
                    </figcaption>
                    <img src="data:image/png;base64,{fig_to_base64(plt.gcf())}" alt="Graphique" style="width: 100%;"/>
                </figure>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Intégrer les informations dans la div
    st.markdown(
        f"""
        <div style='display: flex; justify-content: space-between;'>
            <div style='text-align:center; color:white; background-color:#35424a; padding:3% 3%; width: 30%; height: 150px; margin: 10px; border-radius: 20px;'>
                Nb. d'experts visibles :<br>
                <span style='font-size:2em; margin-left:2%;'>{len(data_profile.loc[(data_profile.type == 'expert')
                                        & (data_profile.done == True)
                                        & (data_profile.visible == True)
                                        | (data_profile.isFake == False)
                                        | (data_profile.temporarilyInvisible == False)])}</span>
            </div>
            <div style='text-align:center; color:white; background-color:#35424a; padding:3% 4%; width: 30%; height: 150px; margin: 10px; border-radius: 20px;'>
                % d'experts évalués :<br>
                <span style='font-size:2em; margin-left:2%;'>{(len(data_intervention.dropna(subset=['note_communication', 'note_quality', 'note_level'], how='all')) / len(data_intervention)) * 100:.2f}</span>
            </div>
            <div style='text-align:center; color:white; background-color:#35424a; padding:3% 3%; width: 30%; height: 150px; margin: 10px; border-radius: 20px;'>
                Note moyenne :<br>
                <span style='font-size:2em; margin-left:2%;'>{data_intervention[['note_communication', 'note_quality', 'note_level']].mean(axis=1, skipna=True).mean(skipna=True):.2f}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Calcul du pourcentage d'experts recommandés
    merged_data_profile_recommandations = pd.merge(data_profile, data_recommendation, left_on='_id', right_on='expertId', how='inner')
    pourcentage_experts_recommandes = (len(merged_data_profile_recommandations) / len(data_profile)) * 100

    st.markdown(
        f"""
        <div style='text-align:center; color:white; background-color:#00bc93; padding:1% 3%; width: 50%; height: 80px; margin: 1% auto; border-radius: 20px;'>
            Pourcentage d'experts recommandés :
            <span style='font-size:2em; margin-left:2%;'>{pourcentage_experts_recommandes:.2f} %</span>
        </div>                              
        """,
        unsafe_allow_html=True
    )

    # Créer une division (div) avec un trait de couleur
    st.markdown(
        """
        <div style="margin: 20px 0 20px 0; padding: 1%; background-color: #f2f6fc;"></div>
        """,
        unsafe_allow_html=True
    )