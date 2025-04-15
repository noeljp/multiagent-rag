# 🧩 Services - Coordination de l'application multi-agent

Ce répertoire contient les **composants fonctionnels principaux** de l’orchestration multi-agent : gestion de la collaboration entre agents, orchestration dynamique, sauvegarde/restauration de projets, gestion du workspace, et export des livrables.

---

## 📁 Fichiers inclus

### `collaboration.py`
Module central pour la **chaîne de collaboration entre agents** :
- Gère l’enchaînement des agents à partir du projet.
- Analyse et exécute les balises spéciales :
  - `##GENERATE_FILE` → écrit les fichiers.
  - `##RUN_TERMINAL` → exécute des commandes.
  - `##AGENT(...)` → planifie la prochaine interaction.
- Gère l’affichage en temps réel de l’activité :
  - Résultats terminal, fichiers, recherches internet.
- Intègre un système de **timeline horodatée** et de **détection de fin automatique** (`###PROJET_TERMINER`).

---

### `export.py`
Module pour **l’export des résultats de la collaboration** :
- Sauvegarde l'historique dans un `.txt`.
- Génère une archive `.zip` contenant :
  - Les fichiers générés
  - L’historique des échanges
  - Le dossier `workspace/`

---

### `orchestrator.py`
Orchestrateur intelligent :
- Crée un **plan de projet dynamique** à partir du prompt initial.
- Affecte chaque tâche à l’agent le plus adapté.
- Supervise l’exécution complète d’un projet de bout en bout sans intervention humaine.

---

### `persist.py`
Module de **sauvegarde/rechargement des projets** :
- Sauvegarde l'état du projet en `.json` :
  - Description
  - Historique complet
  - Métamémoire
  - Timeline des agents
- Permet de recharger un projet sauvegardé depuis l'interface admin.

---

### `workspace.py`
Outils pour **nettoyer le répertoire de travail `workspace/`** entre deux collaborations.
- Supprime tous les fichiers précédemment générés.

---

## 🎯 Objectif du module

Centraliser tous les services nécessaires à :
- L’exécution de scénarios multi-agent complexes
- La persistance des projets dans le temps
- Le suivi et l’observation des résultats (via logs et export)
- La scalabilité vers une orchestration intelligente