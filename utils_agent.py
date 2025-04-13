import json
import re
from base_agent import BaseAgent,resume_message
import streamlit as st
from utils.internet import duckduckgo_search_and_browse
import time

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
    # Prompt système enrichi pour une meilleure efficacité de l’équipe
    date_str = time.strftime('%d/%m/%Y')
    system_prompt = (
        f"Nous sommes aujourd'hui le {date_str}.\n"
        "Tu es un Chef de Projet IA expérimenté et ta mission est de constituer une équipe d’agents autonomes "
        "pour mener à bien le projet du client. L'équipe doit être la plus efficace possible.\n\n"

        "Voici les points essentiels pour rendre l'équipe plus performante :\n"
        "1. Assure une répartition des rôles claire et exhaustive. Chaque agent doit couvrir un domaine précis "
        "   (ex. planification, développement, QA, test, documentation, etc.).\n"
        "2. Impose des méthodes de collaboration efficaces. Chaque agent doit connaître l'existence, le rôle "
        "   et la mission des autres agents pour coordonner ses actions. Clarifie comment les informations et "
        "   les livrables circulent d’un agent à l’autre.\n"
        "3. Prévois au moins un agent chargé de vérifier la qualité ou de gérer les risques (QA, veille technologique, etc.).\n"
        "4. Mets en place une validation itérative des livrables. Dès qu’un agent produit une partie du projet, "
        "   un autre agent doit la vérifier et valider.\n"
        "5. Ajuste la taille de l’équipe en fonction de la complexité du projet. Évite la duplication inutile "
        "   mais assure une couverture complète de toutes les activités.\n"
        "6. Chaque agent doit avoir un `system_prompt` détaillé, rappelant son rôle, celui des autres, et les livrables attendus.\n"
        "7. Utilise strictement le format JSON ci-dessous pour la réponse finale, avec la structure suivante :\n"
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
        "9. Le premier livrable doit être une feuille de route avec les étapes clés du projet. Chaque agent utilisera ensuite cette roadmap pour s’organiser.\n"

    )

    print("--------------        Creation de l'agent TeamBuilder")
    team_builder = BaseAgent(
        name="TeamBuilder",
        role_name="Chef d'Équipe IA",
        system_prompt=system_prompt,
        memory="team_builder",
        shared_metamemory=shared_metamemory,
        max_context_tokens_history=6000
    )
    
    
    try:
        print("--------------        Chat")
        raw_response = team_builder.chat(f"Voici la demande du client :\n\n\"{project_description}\"")
        print("Raw response Json team:", raw_response)
        json_str = raw_response.split("```json")[1].split("```")[0].strip()
        team_definition = json.loads(json_str)
        
    except Exception as e:
        
        return False, f"❌ Erreur lors du parsing JSON : {e}"
    
    #Ajoute au sytem prompt de chaque agent la description de l'equipe 
    team_context = ["Voici ton équipe constituée :"]
    for agent_info in team_definition:
        team_context.append(f'{agent_info["name"]}: {agent_info["role"]}')
    team_context_block = "\n".join(team_context)
        
    
    try:
        agent_team = {}
        for agent_info in team_definition:
            name = agent_info["name"]
            role = agent_info["role"]
            system_prompt = agent_info["system_prompt"]
            token_limit = agent_info.get("token_limit", 3000)
            memory_id = "ctx_"+agent_info.get("memory", name.lower())
            memory_id = memory_id.strip('_')[:63]
            print(f"Création de l'agent : {name} avec mémoire : {memory_id}")


            agent_team[name] = BaseAgent(
                name=name,
                role_name=role,
                shared_metamemory=shared_metamemory,
                system_prompt=f"Tu t'appel {name}.\n" + system_prompt + f"\n\n{team_context_block}",
                memory=memory_id,
                max_context_tokens_history=token_limit
            )

        st.session_state.agent_team = agent_team
        return True, f"✅ Équipe de {len(agent_team)} agents créée avec succès."
    except Exception as e:
        return False, f"❌ Erreur lors de l’instanciation des agents : {e}"


# 🔀 Gestion balise AGENT dans une réponse
def extract_next_agent(response: str, current_agent_name: str, agent_names: list):
    match = re.search(r"##AGENT\((.*?),\s*(.*?)\)", response)
    if match:
        next_agent_name = match.group(1).strip().replace('"', '')
        next_instruction = match.group(2).strip()
        if next_agent_name in agent_names:
            return next_agent_name, next_instruction

    # Par défaut, désigner le suivant dans la liste
    next_index = (agent_names.index(current_agent_name) + 1) % len(agent_names)
    fallback_name = agent_names[next_index]
    fallback_instruction = "Voici où en est le développement du projet, continue le développement."
    return fallback_name, fallback_instruction

