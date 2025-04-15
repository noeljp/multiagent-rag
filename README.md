
# 🤖 Multi-Agent Collaboration Platform (Streamlit)

Ce projet est une plateforme de collaboration multi-agent pilotée par Streamlit, combinant intelligence artificielle, génération de code, orchestration d’agents spécialisés, et mémoire vectorielle pour une productivité augmentée.

---

## 🚀 Fonctionnalités principales

### 🎯 Collaboration par agents autonomes
- Génération automatique d'une équipe d'agents IA à partir d'une description de projet.
- Chaque agent agit à tour de rôle, avec un contexte partagé.
- L'agent peut :
  - Écrire du code avec `##GENERATE_FILE`
  - Exécuter des commandes terminal avec `##RUN_TERMINAL`
  - Déclencher des recherches en ligne
  - Collaborer avec d’autres agents via `##AGENT(...)`

### 📊 Interface d’administration
- Vue admin synchronisée en temps réel.
- Affiche :
  - Historique des réponses
  - Statistiques détaillées par agent
  - Métamémoire partagée
  - Projets sauvegardés

### 💻 Exécution de terminal et génération de fichiers
- Les fichiers générés sont écrits automatiquement dans le répertoire `workspace/`.
- Les commandes terminal sont interprétées et exécutées dans ce répertoire, avec affichage des sorties (`stdout`/`stderr`).

### 🧠 Mémoire vectorielle (RAG)
- Moteur RAG avec `SmartTextSplitter` et embeddings pour enrichir le contexte des agents.

---

## 📁 Structure du projet

```
multiagent/
│
├── controller/             # Contrôle principal de l'application
│   └── app_controller.py
├── ui/                     # Interface utilisateur
│   ├── admin_ui.py
│   └── main_ui.py
├── agents/                 # Définition des agents
│   └── base_agent.py
├── services/               # Collaboration, export, persistence
│   ├── collaboration.py
│   ├── export.py
│   └── persist.py
├── utils/                  # Fonctions terminal, internet, fichiers
│   ├── terminal.py
│   ├── internet.py
│   └── file.py
├── workspace/              # Répertoire temporaire de travail
└── main.py                 # Point d’entrée de l’application Streamlit
```

---

## ▶️ Démarrage rapide

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Lancer l'application

```bash
streamlit run main.py
```

---

## 📝 Exemple de prompt projet

> Crée une API REST en Python qui prédit les ventes à partir d’un fichier CSV. L’API doit inclure une documentation Swagger et être dockerisée.

---

## 💾 Sauvegarde et rechargement

Les projets sont automatiquement sauvegardés avec l’historique complet :
- Dialogue entre agents
- Métamémoire
- Arborescence de fichiers générés

---

## ✅ Fin automatique d’un projet

L'agent peut terminer le projet en insérant :
```
###PROJET_TERMINER
```
dans sa réponse. Cela arrête immédiatement le processus collaboratif.

---

## 🛠️ À venir

- Orchestrateur intelligent (planification dynamique)
- Support multi-utilisateurs
- Export PDF de la collaboration
- Intégration API REST (mode headless)

---

## 🧑‍💻 Auteur

Développé par [Ton Nom], dans le cadre d'une expérimentation sur l'intelligence collective automatisée.

