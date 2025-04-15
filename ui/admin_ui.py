# ui/admin_ui.py
import streamlit as st
import pandas as pd
import plotly.express as px
from services.persist import list_saved_projects, load_project

def display_admin_page():
    st.markdown("## 🛠️ Tableau de Bord Admin - Équipe IA RAG")
    col1, col2 = st.columns(2)

    # 📜 Historique des réponses
    with col1:
        st.subheader("📜 Historique des réponses")
        if "history" in st.session_state and st.session_state.history:
            for entry in reversed(st.session_state.history[-10:]):
                st.markdown(f"<div style='padding:10px;background:#111;border-left:4px solid #0ff;margin-bottom:5px;'>{entry}</div>", unsafe_allow_html=True)
        else:
            st.info("Aucun historique disponible.")

    # 📊 Statistiques + Métamémoire
    with col2:
        st.subheader("📊 Statistiques des agents")
        agent_stats = []
        timeline_by_agent = st.session_state.get("timeline_by_agent", {})
        for name, timeline in timeline_by_agent.items():
            nb_turns = len(timeline)
            total_tokens = sum(len(turn.get("response", "")) for turn in timeline)
            nb_files = sum(len(turn.get("files", [])) for turn in timeline if isinstance(turn.get("files"), list))
            agent_stats.append({
                "Agent": name,
                "Interactions": nb_turns,
                "Réponse Totale (caractères)": total_tokens,
                "Fichiers générés": nb_files
            })

        if agent_stats:
            df_stats = pd.DataFrame(agent_stats)
            st.dataframe(df_stats, use_container_width=True)

            # 📈 Timeline d'activité
            st.subheader("📊 Activité temporelle des agents")
            timeline_data = []
            for agent, turns in timeline_by_agent.items():
                for i, turn in enumerate(turns):
                    timestamp = turn.get("timestamp") or f"Étape {i+1}"
                    timeline_data.append({"Agent": agent, "Étape": i + 1})
            if timeline_data:
                df_timeline = pd.DataFrame(timeline_data)
                fig = px.histogram(df_timeline, x="Étape", color="Agent", barmode="group")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée d’agent disponible.")

        # st.subheader("🧠 Métamémoire Partagée")
        # if "shared_metamemory" in st.session_state and st.session_state.shared_metamemory:
        #     for entry in reversed(st.session_state.shared_metamemory[-10:]):
        #         st.markdown(f"- {entry}")
        # else:
        #     st.info("Métamémoire vide.")

    # 📁 Projets sauvegardés
    st.markdown("---")
    st.subheader("📁 Projets enregistrés")
    saved_projects = list_saved_projects()
    if saved_projects:
        selected_project = st.selectbox("🔄 Recharger un projet :", saved_projects)
        if st.button("🔁 Charger ce projet"):
            loaded = load_project(selected_project)
            if loaded:
                st.session_state.history = loaded.get("history", [])
                st.session_state.timeline_by_agent = loaded.get("timeline", {})
                st.session_state.shared_metamemory = loaded.get("metamemory", [])
                st.success("✅ Projet rechargé avec succès.")
    else:
        st.info("Aucun projet sauvegardé trouvé.")
