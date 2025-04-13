from asyncio.windows_events import CONNECT_PIPE_INIT_DELAY
import streamlit as st
from utils_agent import create_team_from_project, extract_next_agent, get_avatar

from utils.internet import duckduckgo_search_and_browse
from utils.file import write_generated_files
from utils.terminal import execute_terminal_blocks

from ui_elements import (
    display_agent_response,
    display_agent_prompt,
    display_agent_context,
    display_conversation_history,
    display_no_team_warning,
    display_export_button
)
import re, time, datetime
from io import StringIO, BytesIO
import os
import subprocess
import zipfile
from base_agent import resume_message, BaseAgent

# 🗭 CONFIG PAGE
st.set_page_config(page_title="🧐 Équipe IA RAG", layout="wide")
st.title("🤖 Interface RAG + Équipe d'Agents IA Augmentée")

# 🌟 INIT SESSION STATE
for key in ["agent_team", "logs", "history", "timeline_by_agent", "shared_metamemory"]:
    if key not in st.session_state:
        if key == "agent_team":
            st.session_state[key] = {}
        elif key == "timeline_by_agent":
            st.session_state[key] = {}
        elif key == "shared_metamemory":
            st.session_state[key] = []
        else:
            st.session_state[key] = []

# 📝 ZONE DE SAISIE DU PROJET
st.subheader("📌 Décris ton projet ou besoin client")
project_description = st.text_area("📝 Description du projet :", value="Crée un hello WORLD originale en python", height=150, key="project_description")

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("🚀 Créer l'équipe automatiquement"):
        success, msg = create_team_from_project(project_description, st.session_state.shared_metamemory)
        #success, msg = create_team_from_project(project_description)
        if not success:
            st.error(msg)

# 👥 ÉQUIPE D’AGENTS
agent_team = st.session_state.agent_team
if not agent_team:
    display_no_team_warning()
    st.stop()

agent_names = list(agent_team.keys())
selected_agents = st.multiselect("✅ Choisis les agents participants :", agent_names, default=agent_names)

if not selected_agents:
    st.warning("❗ Aucune équipe sélectionnée.")
    st.stop()

# 🎮 BOUTON DE DÉMARRAGE
simulate = st.button("▶️ Lancer la collaboration")

# 📊 ZONE PRINCIPALE : COLLABORATION
st.subheader("📢 Collaboration en chaînage intelligent :")

def format_log_entry(agent_name, response):
    return f"🧐 {agent_name} a répondu à {datetime.datetime.now().strftime('%H:%M:%S')}:\n{response}"

def export_history(history):
    export = "\n\n".join(history)
    st.download_button(
        "📅 Télécharger le compte-rendu",
        data=export,
        file_name="discussion_projet.txt"
    )

def download_zip_with_history_and_generated(workspace: str):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), workspace)
        for foldername, subfolders, filenames in os.walk(root_dir):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, root_dir)
                zip_file.write(file_path, arcname=os.path.join(workspace, arcname))

        if "history" in st.session_state:
            history_txt = "\n\n".join(st.session_state.history)
            zip_file.writestr("historique.txt", history_txt)

    zip_buffer.seek(0)
    st.download_button(
        label="📦 Télécharger les fichiers générés + historique (.zip)",
        data=zip_buffer,
        file_name="projet_complet.zip",
        mime="application/zip"
    )

workspace = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace")

for file in os.listdir(workspace):
    path = os.path.join(workspace, file)
    if os.path.isfile(path):
        os.remove(path)

if simulate:
    current_index = 0
    context = project_description
    previous_responses = {}
    st.session_state.timeline_by_agent = {name: [] for name in selected_agents}

    max_turns = 0
    while current_index < len(selected_agents):
        current_agent_name = selected_agents[current_index]
        current_agent = agent_team[current_agent_name]

        with st.spinner(f"⏳ {current_agent_name} réfléchit..."):
            response = current_agent.chat(context)
            previous_responses[current_agent_name] = response

        # Actions automatiques
        recherche_internet = duckduckgo_search_and_browse(response)
        terminal = execute_terminal_blocks(response, workspace)
        written_files = write_generated_files(response, workspace)

        # Timeline enrichie par agent
        st.session_state.timeline_by_agent[current_agent_name].append({
            "context": context,
            "response": response,
            "internet": recherche_internet if recherche_internet else None,
            "terminal": terminal if terminal else None,
            "files": written_files if written_files else None
        })

        # Historique global texte
        log_entry = format_log_entry(current_agent_name, response)
        st.session_state.history.append(log_entry)
        max_turns += 1

        if "###PROJET_TERMINER" in response:
            st.success("✅ Le projet est terminé !")
            break

        recherche_internet = duckduckgo_search_and_browse(response)
        if recherche_internet:
            st.session_state.history.append(format_log_entry("Internet", recherche_internet))
            context += "\n\n" + recherche_internet

        terminal = execute_terminal_blocks(response, workspace)
        if terminal:
            st.session_state.history.append(format_log_entry("Terminal", terminal))
            context += "\n\n" + terminal

        written_files = write_generated_files(response, workspace)
        if written_files:
            file_list_text = "\n".join(f"📄 {f}" for f in written_files)
            st.session_state.history.append(format_log_entry("Fichier", file_list_text))
            context += "\n\n" + "Fichier généré :\n"

        if recherche_internet or terminal:
            continue

        next_agent_name, next_instruction = extract_next_agent(response, current_agent_name, selected_agents)
        historique = [f"{k}: {v}" for k, v in previous_responses.items()]
        context = (
            f"📝 Demande initiale :\n{project_description}\n\n"
            f"📌 Avancement actuel :\n" + "\n".join(historique) + "\n\n"
            f"➡️ Étape suivante :\n{next_instruction}"
        )
        current_index = selected_agents.index(next_agent_name)

        # Affichage actualisé en colonnes synchrones
        st.subheader("📂 Suivi des réponses par agent")
        agent_cols = st.columns(len(selected_agents))
        # 📂 Affichage avancé des échanges par agent
        st.subheader("📂 Suivi détaillé des échanges par agent")
        agent_cols = st.columns(len(selected_agents))
        for idx, agent_name in enumerate(selected_agents):
            with agent_cols[idx]:
                role = st.session_state.agent_team[agent_name].role_name
                avatar = get_avatar(role)

                st.markdown(f"### {avatar} {agent_name}")
                timeline = st.session_state.timeline_by_agent[agent_name]

                for turn in timeline:
                    context = turn.get("context", "Aucun contexte")
                    response = turn.get("response", "")
                    internet = turn.get("internet", "")
                    terminal = turn.get("terminal", "")
                    files = turn.get("files", [])

                    files_html = "<br>".join(f"📄 {f}" for f in files) if isinstance(files, list) and files else ""

                    st.markdown(f"""
                    <div style='background-color:#1e1e1e;padding:15px;margin:10px 0;border-radius:12px;box-shadow:1px 2px 8px rgba(0,0,0,0.4);'>
                        <strong style="color:#0ff;">🧠 Contexte transmis :</strong>
                        <pre style='background-color:#111;padding:10px;border-radius:6px;color:#0f0;font-size:13px;'>{context}</pre>

                        <strong style="color:#0ff;">✍️ Réponse de l’agent :</strong>
                        <div style='margin-bottom:10px; color:#fff; font-size:14px;'>{response}</div>

                        {"<div style='color:#ccc;'><strong>🌐 Résultat Internet :</strong><br>" + internet + "</div>" if internet else ""}
                        {"<div style='color:#ccc;'><strong>🖥️ Commande Terminal :</strong><br>" + terminal + "</div>" if terminal else ""}
                        {"<div style='color:#ccc;'><strong>📦 Fichiers générés :</strong><br>" + files_html + "</div>" if files_html else ""}
                    </div>
                    """, unsafe_allow_html=True)


                for _ in range(max_turns - len(timeline)):
                    st.markdown("<div style='padding:10px;margin:5px 0;'>&nbsp;</div>", unsafe_allow_html=True)


    st.markdown("---")
    st.subheader("📅 Exporter le projet")
    export_history(st.session_state.history)
    download_zip_with_history_and_generated(workspace)
