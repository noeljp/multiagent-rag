
# 🧠 Agents - Module de collaboration intelligente

Ce dossier contient les **composants centraux liés aux agents intelligents** de la plateforme multi-agent. Chaque agent agit de manière autonome, avec un rôle bien défini, une mémoire contextuelle, et la capacité de générer du code, de communiquer, et d'interagir avec les autres agents.

---

## 📁 Fichiers inclus

### `base_agent.py`
Contient la classe `BaseAgent`, le cœur du comportement de chaque agent IA :
- Initialisation avec nom, rôle, mémoire et système de prompt.
- Construction dynamique du contexte de conversation.
- Appel au modèle LLM via `run_chat_completion`.
- Intégration de contexte vectoriel (RAG) via `RAGManager`.
- Enregistrement automatique de l'historique des réponses.

---

### `agent_utils.py`
Contient des **fonctions utilitaires** pour la gestion des agents :

- `get_avatar(role: str)`  
  Renvoie un emoji représentant visuellement un rôle d’agent (ex. développeur, manager...).

- `create_team_from_project(project_description, shared_metamemory)`  
  Génère automatiquement une équipe d’agents à partir d’un prompt projet.  
  Utilise un appel à un LLM pour définir les rôles et prompts de chaque agent.

- `extract_next_agent(response, current_agent_name, agent_names)`  
  Analyse une réponse contenant `##AGENT(...)` et déduit quel agent doit répondre ensuite.

---

## 🚀 Objectif du module

Permettre de créer une **coopération fluide entre plusieurs agents IA**, où chacun :
- connaît son rôle
- suit un système de prompt spécifique
- mémorise son historique
- peut enrichir la mémoire collective