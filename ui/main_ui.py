import streamlit as st
from agents.agent_utils import create_team_from_project
from ui.ui_elements import display_no_team_warning




def handle_project_input(shared_metamemory):
    st.subheader("📌 Décris ton projet ou besoin client")
    project_description = st.text_area("📝 Description du projet :", value="Crée un hello WORLD originale en python", height=150, key="project_description")

    col1, _ = st.columns([1, 3])
    with col1:
        if st.button("🚀 Créer l'équipe automatiquement"):
            success, msg = create_team_from_project(project_description, shared_metamemory)
            if not success:
                st.error(msg)
    return project_description

