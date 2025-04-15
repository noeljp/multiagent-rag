import streamlit as st
from agents.agent_utils import get_avatar



# 🧾 Bloc visuel pour la réponse d'un agent (style Trello amélioré)
def display_agent_response(name: str, role: str, response: str):
    avatar = get_avatar(role)

    st.markdown(f"""
    <div style="
        background-color: #333;
        color: #0ff;
        border: 1px solid #555;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 1px 2px 8px rgba(0,0,0,0.3);
        margin-bottom: 1rem;
    ">
        <div style="font-size: 32px; text-align: center;">{avatar}</div>
        <h4 style="text-align: center; margin-bottom: 0;">{name}</h4>
        <p style="text-align: center;"><em>{role}</em></p>
        <hr style="margin-top:10px; margin-bottom:10px;">
        <p style="font-size: 14px;">{response}</p>
    </div>
    """, unsafe_allow_html=True)


# 🧠 Bloc inspectable : système prompt d’un agent
def display_agent_prompt(name: str, system_prompt: str):
    with st.expander(f"🧾 Prompt système de {name}", expanded=False):
        st.code(system_prompt, language="markdown")
# 🧠 Bloc inspectable : context prompt d’un agent
def display_agent_context(name: str, system_prompt: str):
    with st.expander(f"🧾 Contexte de {name}", expanded=False):
        st.code(system_prompt, language="markdown")


# 🔁 Affichage d’un historique de conversation entre agents
def display_conversation_history(history_dict: dict):
    st.subheader("📚 Historique de la conversation")
    for name, msg in history_dict.items():
        avatar = get_avatar(name)
        st.markdown(f"""
        <div style="margin-bottom: 10px; padding: 10px; border-left: 4px solid #ccc;">
            <strong>{avatar} {name}</strong><br>
            <div style="font-size: 14px;">{msg}</div>
        </div>
        """, unsafe_allow_html=True)


# 🛑 Bloc d'avertissement si aucune équipe n’est définie
def display_no_team_warning():
    st.warning("🚧 Aucune équipe n'est définie. Crée une équipe pour commencer.")
    st.stop()


# 📤 Bouton d’export de l’historique (facultatif)
def display_export_button(history_dict: dict):
    if history_dict:
        history_text = "\n\n".join([f"{name}:\n{resp}" for name, resp in history_dict.items()])
        st.download_button("📥 Exporter l’historique", history_text, file_name="conversation.txt")
