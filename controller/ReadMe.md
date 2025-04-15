# 🎛️ app_controller.py — Contrôleur principal de l'application

Ce fichier est le **point de coordination principal** de l'interface Streamlit. Il orchestre la structure visuelle de l'application, le déclenchement des processus collaboratifs entre agents, l'affichage du tableau de bord et la sauvegarde des projets.

---

## 🔧 Rôle du fichier

- Gérer **l'interface utilisateur** (via `st.columns`, `st.button`, `st.session_state`, etc.)
- Connecter les agents avec les services de collaboration (`run_collaboration`)
- Déclencher le rafraîchissement automatique du tableau de bord admin
- Sauvegarder les projets finalisés (historique, timeline, métamémoire)
- Lancer l’exécution des agents **étape par étape**

---

## 🎯 Fonctionnalités clés

### 📋 Initialisation
- Initialise les clés essentielles dans `st.session_state` :
  - `agent_team`, `history`, `shared_metamemory`, `timeline_by_agent`

### 🧭 Interface en colonnes
- Colonne de gauche : panneau d'administration (`display_admin_page()`)
- Colonne de droite : interface projet (description, sélection agents, bouton de lancement)

### ▶️ Lancement d'une collaboration
- Nettoie le workspace (`clean_workspace`)
- Lance `run_collaboration()` en boucle
- Met à jour dynamiquement la vue admin via `admin_placeholder.container()`
- Interrompt la boucle dès qu’un agent écrit `###PROJET_TERMINER`

### 💾 Sauvegarde
- Sauvegarde le projet complet en `.json` dans `saved_projects/`
- Propose un export `.zip` avec tous les fichiers générés

---
