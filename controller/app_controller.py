# controller/app_controller.py
import streamlit as st
from ui.main_ui import handle_project_input
from ui.admin_ui import display_admin_page
from services.collaboration import run_collaboration
from services.export import download_zip_with_history_and_generated
from services.workspace import clean_workspace
from services.persist import save_project

import os
import time

def run():
    st.set_page_config(page_title="🧐 Équipe IA RAG", layout="wide")
    st.title("🤖 Interface RAG + Équipe d'Agents IA Augmentée")

    for key in ["agent_team", "logs", "history", "timeline_by_agent", "shared_metamemory"]:
        if key not in st.session_state:
            st.session_state[key] = {} if "agent_team" in key or "timeline" in key else []

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("## 📈 Admin (auto-refresh)")
        admin_placeholder = st.empty()

    with col2:
        st.markdown("## 👥 Projet & Équipe")
        project_description = handle_project_input(st.session_state.shared_metamemory)

        agent_team = st.session_state.agent_team
        if not agent_team:
            st.warning("🚧 Aucune équipe n'est définie. Crée une équipe pour commencer.")
            return

        agent_names = list(agent_team.keys())
        selected_agents = st.multiselect("✅ Choisis les agents participants :", agent_names, default=agent_names)

        simulate = st.button("▶️ Lancer la collaboration")
        workspace = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "workspace")

        if simulate:
            #clean_workspace(workspace)

            for i in range(len(selected_agents)):
                is_done = run_collaboration(project_description, selected_agents, workspace)
                with admin_placeholder.container():
                    display_admin_page()
                time.sleep(0.5)
                if is_done:
                    st.success("🎉 Le projet est terminé automatiquement.")
                    break


            st.markdown("---")
            st.subheader("📅 Exporter et Sauvegarder le projet")
            if st.button("💾 Sauvegarder le projet actuel"):
                filename = save_project(
                    project_description,
                    st.session_state.history,
                    st.session_state.timeline_by_agent,
                    st.session_state.shared_metamemory
                )
                st.success(f"💾 Projet sauvegardé sous {filename}")
            download_zip_with_history_and_generated(workspace)
        else:
            with admin_placeholder.container():
                display_admin_page()