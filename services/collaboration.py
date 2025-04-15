# services/collaboration.py
import streamlit as st
import datetime, os
from utils.internet import duckduckgo_search_and_browse
from utils.file import write_generated_files
from utils.terminal import execute_terminal_blocks
from agents.agent_utils import extract_next_agent, get_avatar
from agents.base_agent import BaseAgent
import shlex
import subprocess

def format_log_entry(agent_name, response):
    return f"🧐 {agent_name} a répondu à {datetime.datetime.now().strftime('%H:%M:%S')} :\n{response}"

def run_collaboration(project_description, selected_agents, workspace, max_turns=1):
    agent_team = st.session_state.agent_team

    if not agent_team:
        st.warning("🚧 Aucune équipe définie.")
        st.stop()

    if not selected_agents:
        st.warning("❗ Aucun agent sélectionné.")
        st.stop()

    if "step_counter" not in st.session_state:
        st.session_state.step_counter = 0

    context = project_description
    previous_responses = {}
    st.session_state.timeline_by_agent = st.session_state.get("timeline_by_agent", {})

    for file in os.listdir(workspace):
        path = os.path.join(workspace, file)
        if os.path.isfile(path):
            os.remove(path)

    for turn_index in range(max_turns):
        current_index = st.session_state.step_counter % len(selected_agents)
        current_agent_name = selected_agents[current_index]
        current_agent = agent_team[current_agent_name]

        st.session_state.step_counter += 1
        st.markdown(f"### 🔄 Étape {st.session_state.step_counter} — Agent : **{current_agent_name}**")

        with st.spinner(f"⏳ {current_agent_name} réfléchit..."):
            response = current_agent.chat(context)
            previous_responses[current_agent_name] = response

        written_files = write_generated_files(response, workspace)
        recherche_internet = duckduckgo_search_and_browse(response)
        terminal = execute_terminal_blocks(response, workspace)

        if current_agent_name not in st.session_state.timeline_by_agent:
            st.session_state.timeline_by_agent[current_agent_name] = []

        st.session_state.timeline_by_agent[current_agent_name].append({
            "context": context,
            "response": response,
            "internet": recherche_internet if recherche_internet else None,
            "terminal": terminal if terminal else None,
            "files": written_files if written_files else None,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })

        log_entry = format_log_entry(current_agent_name, response)
        st.session_state.history.append(log_entry)

        if recherche_internet:
            st.markdown("#### 🌐 Résultat de la recherche Internet")
            st.code(recherche_internet)
            st.session_state.history.append(format_log_entry("Internet", recherche_internet))
            context += "\n\n" + recherche_internet

        if terminal:
            st.markdown("#### 💻 Résultat du terminal")
            st.code(terminal)
            st.session_state.history.append(format_log_entry("Terminal", terminal))
            context += "\n\n" + terminal

        if written_files:
            st.markdown("#### 📁 Fichiers générés")
            for f in written_files:
                st.write(f"📄 {f}")
            file_list_text = "\n".join(f"📄 {f}" for f in written_files)
            st.session_state.history.append(format_log_entry("Fichier", file_list_text))
            context += "\n\nFichier généré :\n" + file_list_text

        if "###PROJET_TERMINER" in response:
            return True

        if not (recherche_internet or terminal):
            next_agent_name, next_instruction = extract_next_agent(response, current_agent_name, selected_agents)
            historique = [f"{k}: {v}" for k, v in previous_responses.items()]
            context = (
                f"📝 Demande initiale :\n{project_description}\n\n"
                f"📌 Avancement actuel :\n" + "\n".join(historique) + "\n\n"
                f"➡️ Étape suivante :\n{next_instruction}"
            )

    return False