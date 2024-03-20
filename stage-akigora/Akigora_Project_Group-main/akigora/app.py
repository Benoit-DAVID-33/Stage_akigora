# app.py
import pandas as pd
import streamlit as st
from datas.data_loader import load_profile_data, load_user_data, \
                              load_intervention_data, load_recommendation_data, \
                              load_search_data, load_newsletter_data, \
                              load_consultation_data
from dashboards.rh import generate_rh_dashboard
from dashboards.commercial import generate_commercial_dashboard
from dashboards.marketing import generate_marketing_dashboard
from utils.utils import generate_calendar
  
def main():
    
    # Création des url pour téléchargement des données  
    url_consultations = 'datas/consultations.csv'    
    url_intervention = 'datas/intervention.csv'
    url_newsletter = 'datas/newsletter.csv' 
    url_profile_type_expert = 'datas/profile_type_expert.csv'   
    url_recommendations = 'datas/recommendations.csv'
    url_search = 'datas/search.csv'
    url_user = 'datas/user.csv'
                   
    # Chargement des données
    data_profile = load_profile_data(url_profile_type_expert)
    data_profile['createdAt'] = pd.to_datetime(data_profile['createdAt'], errors='coerce')

    data_user = load_user_data(url_user)
    data_intervention = load_intervention_data(url_intervention)
    data_recommendation = load_recommendation_data(url_recommendations)
    data_search = load_search_data(url_search)
    data_newsletter = load_newsletter_data(url_newsletter)
    data_consultation = load_consultation_data(url_consultations)
    
    # Configuration de la mise en page
    st.set_page_config(page_title="Dashboard Combiné", page_icon=":chart_with_upwards_trend:", layout="wide")

    st.markdown(
        """
        <div style='background-color: black'>
        </div>
        <div style='display: flex; justify-content: space-between;'>
            <img src="https://akigora.com/img/logo_rvb_horizontal_petit.png">
        </div>
        """,
        unsafe_allow_html=True
    )

    # Titre central avant de choisir un rôle
    title_section = st.empty()
    title_section.title("Dashboard pré Alpha") 
    
    # Vérifier si l'utilisateur est connecté en utilisant une session
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None

    st.sidebar.title("Système de Connexion")

    # Menu déroulant pour choisir le rôle
    user_role = st.sidebar.selectbox("Choix du rôle", ["Choisissez un rôle", "RH", "Service commercial", "Marketing"])

    # Personnaliser la couleur du menu déroulant
    if user_role != "Choisissez un rôle":
        # Style CSS lorsque l'utilisateur a fait un choix
        st.markdown(
            f"""
            <style>
                /* Personnaliser le conteneur du menu déroulant */
                div[data-baseweb="select-container"] {{
                    background-color: #7d43c8 !important;
                }}
                /* Personnaliser les options du menu déroulant */
                div[data-baseweb="select"] div:first-child {{
                    color: white !important;
                    background-color: #7d43c8 !important;
                    border-radius: 150px !important; /* Ajout du border-radius */
                }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        # Style CSS lorsque l'utilisateur n'a pas encore fait de choix
        st.markdown(
            f"""
            <style>
                /* Personnaliser le conteneur du menu déroulant avant le choix */
                div[data-baseweb="select-container"] {{
                    background-color: #7d43c8 !important;
                }}
                /* Personnaliser les options du menu déroulant avant le choix */
                div[data-baseweb="select"] div:first-child {{
                    color: white !important;
                    background-color: #7d43c8 !important;
                    border-radius: 150px !important; /* Ajout du border-radius */
                }}
            </style>
            """,
            unsafe_allow_html=True
        )

    if user_role and user_role != "Choisissez un rôle":
        if user_role == "RH":
            role_image_path = "https://cdn0.iconfinder.com/data/icons/man-user-human-profile-avatar-business-person/100/09B-1User-512.png"
            title_section.empty()  # Efface le titre initial
            st.title("Tableau de bord RH")
            generate_rh_dashboard(data_profile, data_user, data_intervention, data_recommendation)
        elif user_role == "Service commercial":
            role_image_path = "https://cdn0.iconfinder.com/data/icons/man-user-human-profile-avatar-business-person/100/09B-1User-512.png"
            title_section.empty()  # Efface le titre initial
            st.title("Tableau de bord Commercial")
            generate_commercial_dashboard(data_profile, data_user, data_intervention)
        elif user_role == "Marketing":
            role_image_path = "https://cdn0.iconfinder.com/data/icons/man-user-human-profile-avatar-business-person/100/09B-1User-512.png"
            title_section.empty()  # Efface le titre initial
            st.title("Tableau de bord Marketing")
            generate_marketing_dashboard(data_recommendation, data_search, data_profile, data_user, data_consultation, data_newsletter)   

        # Déplacez la balise <img> à l'extérieur de st.sidebar.markdown
        st.sidebar.success(f"Connecté en tant que {user_role}")
        st.sidebar.image(role_image_path, width=100)



    # Ajoutez une ligne vide pour créer un espace
    st.sidebar.markdown("<br>", unsafe_allow_html=True)

   # Ajoutez le bouton "Support" avec le lien pour ouvrir dans une nouvelle page
    st.sidebar.markdown(
        """
        <a href="https://akigora-dashboard-documentation.streamlit.app" target="_blank">
            <button style="background-color: #00bc93; color: white; border-radius: 10px; padding: 10px 20px; cursor: pointer;">
                Support
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

    generate_calendar()

    # Ajouter la partie de la personnalisation du style ici...
    st.markdown(
        """
        <style>
            .streamlit-table {
                color: white;
                background-color: #35424a;
            }
            .streamlit-dataframe th {
                color: white;
                background-color: #35424a;
            }
            .st-emotion-cache-vk3wp9 {
                width: 200px !important;
            }
            .avatar{
                position: absolute;
                top: -45vh;
                left: 4vw;
                margin-bottom: 4%;
            }
            .st-emotion-cache-ocqkz7:nth-of-type(2) {
                width: 50% !important;
            }
            .centered-avatar {
                display: block;
                margin-left: auto;
                margin-right: auto;
                margin-bottom: 10px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

# Exécutez l'application
if __name__ == "__main__":
    main()