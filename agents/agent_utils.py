import json
import re
from agents.base_agent import BaseAgent
import streamlit as st
import time
from core.llm import run_chat_completion

from utils.internet import duckduckgo_search_and_browse

# 🎨 Avatar en fonction du rôle
def get_avatar(role: str) -> str:
    role = role.lower()

    avatar_map = {
        "dev": "💻", "développeur": "💻", "developer": "💻", "programmation": "💻", "code": "💻",
        "chef": "🧑‍💼", "lead": "🧑‍💼", "project": "🧑‍💼", "manager": "🧑‍💼", "coordinateur": "🧑‍💼",
        "expert": "🧠", "consultant": "🧠", "stratégie": "🧠", "specialist": "🧠", "analyste": "🧠",
        "ux": "🎨", "ui": "🎨", "design": "🎨", "graphique": "🎨", "créatif": "🎨",
        "data": "📊", "ml": "📊", "ai": "📊", "intelligence": "📊", "analyse": "📊", "big data": "📊",
        "infra": "🛠️", "ops": "🛠️", "système": "🛠️", "admin": "🛠️", "cloud": "🛠️", "réseau": "🛠️", "sécurité": "🛠️",
        "test": "🔍", "qa": "🔍", "qualité": "🔍", "vérification": "🔍", "validation": "🔍",
        "rédacteur": "📝", "content": "📝", "communication": "📝", "copy": "📝", "rédaction": "📝",
        "marketing": "📢", "produit": "📢", "product owner": "📢", "po": "📢", "market": "📢",
        "rh": "📋", "human": "📋", "ressources": "📋", "administratif": "📋", "admin": "📋",
        "finance": "💰", "compta": "💰", "accounting": "💰", "budget": "💰",
        "legal": "⚖️", "juridique": "⚖️", "droit": "⚖️", "avocat": "⚖️",
        "formateur": "🎓", "formation": "🎓", "coach": "🎓", "enseignant": "🎓", "pédagogie": "🎓",
    }

    for keyword, emoji in avatar_map.items():
        if keyword in role:
            return emoji
    return "👤"


# 🧠 Création d'une équipe d'agents depuis un prompt projet
def create_team_from_project(project_description: str, shared_metamemory: list):
    print("------------    Appel de create_team_from_project")

    date_str = time.strftime('%d/%m/%Y')
    system_prompt = (
        f"Nous sommes aujourd'hui le {date_str}.\n"
        "Tu es un Chef de Projet IA expérimenté et ta mission est de constituer une équipe d’agents autonomes "
        "pour mener à bien le projet du client. L'équipe doit être la plus efficace possible.\n\n"

        "Voici les points essentiels pour rendre l'équipe plus performante :\n"
        "1. Assure une répartition des rôles claire et exhaustive. Chaque agent doit couvrir un domaine précis.\n"
        "2. Impose des méthodes de collaboration efficaces.\n"
        "3. Prévois au moins un agent chargé de vérifier la qualité ou de gérer les risques.\n"
        "4. Mets en place une validation itérative des livrables.\n"
        "5. Ajuste la taille de l’équipe en fonction de la complexité du projet.\n"
        "6. Chaque agent doit avoir un `system_prompt` détaillé.\n"
        "7. Utilise strictement le format JSON ci-dessous pour la réponse finale :\n"
        "   ```json\n"
        "   [\n"
        "       {\n"
        "           \"name\": \"...\",\n"
        "           \"role\": \"...\",\n"
        "           \"system_prompt\": \"...\",\n"
        "           \"token_limit\": 4000\n"
        "       }\n"
        "   ]\n"
        "   ```\n"
        "8. Aucune information hors du format JSON ne doit être renvoyée.\n"
        "9. Le premier livrable doit être une feuille de route avec les étapes clés du projet.\n"
    )

    try:
        response = run_chat_completion(
            system_prompt=system_prompt,
            user_prompt=f"Voici la demande du client :\\n\\n\\\"{project_description}\\\"",
            model="gpt-4o",
            temperature=0.2,
            max_tokens=2000
        )
        print("Raw response Json team:", response)
        json_str = response.split("```json")[1].split("```")[0].strip()
        team_definition = json.loads(json_str)
    except Exception as e:
        return False, f"❌ Erreur lors du parsing JSON : {e}"

    team_context = ["Voici ton équipe constituée :"]
    print("team_definition:", team_definition)
    for agent_info in team_definition:
        team_context.append(f'{agent_info["name"]}: {agent_info["role"]}')
    team_context_block = "\\n".join(team_context)

    try:
        agent_team = {}
        for agent_info in team_definition:
            name = agent_info["name"]
            print(f"Agent name: {name}")
            role = agent_info["role"]
            system_prompt = agent_info["system_prompt"]
            token_limit = agent_info.get("token_limit", 3000)
            memory_id = "ctx_" + agent_info.get("memory", name.lower())
            memory_id = memory_id.strip('_')[:63]
            print(f"Memory ID: {memory_id}")
            agent_team[name] = BaseAgent(
                name=name,
                role_name=role,
                shared_metamemory=shared_metamemory,
                system_prompt=f"Tu t'appel {name}.\\n" + system_prompt + f"\\n\\n{team_context_block}",
                memory=memory_id,
                max_context_tokens_history=token_limit
            )

        st.session_state.agent_team = agent_team
        return True, f"✅ Équipe de {len(agent_team)} agents créée avec succès."
    except Exception as e:
        return False, f"❌ Erreur lors de l’instanciation des agents : {e}"


# 🔀 Gestion balise AGENT dans une réponse
def extract_next_agent(response: str, current_agent_name: str, agent_names: list):
    match = re.search(r"##AGENT\\((.*?),\\s*(.*?)\\)", response)
    if match:
        next_agent_name = match.group(1).strip().replace('"', '')
        next_instruction = match.group(2).strip()
        if next_agent_name in agent_names:
            return next_agent_name, next_instruction

    next_index = (agent_names.index(current_agent_name) + 1) % len(agent_names)
    fallback_name = agent_names[next_index]
    fallback_instruction = "Voici où en est le développement du projet, continue le développement."
    return fallback_name, fallback_instruction