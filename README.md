```markdown
<h1 align="center">
  🤖 Multi-Agent IA avec Streamlit + RAG
</h1>

<p align="center">
  <strong>Simulez une équipe d'agents intelligents, collaboratifs et autonomes.</strong><br>
  Génération automatique de rôles, supervision, coordination, RAG, et export projet complet.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Streamlit-IA_augmentée-red?style=flat-square&logo=streamlit">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python">
  <img src="https://img.shields.io/github/license/noeljp/multiagent-rag?style=flat-square">
</p>


Bienvenue dans ce projet ambitieux qui met en scène une **équipe d'agents IA autonomes** capables de collaborer sur une tâche définie par l'utilisateur. Le tout est orchestré dans une interface ergonomique construite avec [Streamlit](https://streamlit.io).

---

## 🌟 Fonctionnalités clés

- ⚙️ **Génération automatique d'équipe IA** à partir d'un prompt client
- 🧠 **Agents spécialisés** (développement, QA, stratégie, etc.)
- 🔁 **Chaînage intelligent** entre agents via des instructions contextuelles
- 📚 **RAG (Retrieval-Augmented Generation)** pour enrichir les réponses avec une base de connaissances
- 📦 **Export du projet** (historique + fichiers générés) dans un `.zip`
- 🧾 **Affichage visuel détaillé** de chaque échange entre agents

---

## 🧪 Exemples de cas d’usage

- Créer un script Python original
- Rédiger un document structuré avec validation croisée
- Organiser une roadmap technique
- Simuler une équipe produit Agile

---

## 🚀 Lancer le projet

### 1. Clone ce dépôt

```bash
git clone https://github.com/noeljp/multiagent-rag.git
cd multiagent-rag
```

### 2. Installe les dépendances

Crée un environnement virtuel (recommandé) :
```bash
python -m venv env
source env/bin/activate      # Linux/macOS
env\\Scripts\\activate.bat   # Windows
```

Installe les paquets :
```bash
pip install -r requirements.txt
```

### 3. Lance l’application

```bash
streamlit run app.py
```

---

## 🖼️ Aperçu visuel

| 👥 Création d'équipe | 📂 Suivi par agent | 🧠 Collaboration enrichie |
|----------------------|-------------------|---------------------------|
| ![](assets/team.png) | ![](assets/agents.png) | ![](assets/flow.png)     |

*(Ajoute tes captures dans un dossier `assets/`)*

---

## 🧰 Structure du projet

```bash
multiagent-rag/
│
├── app.py                    # Application principale Streamlit
├── base_agent.py             # Classe de base des agents
├── utils_agent.py            # Création & orchestration des agents
├── utils/                    # Fonctions Internet, fichiers, terminal
├── workspace/                # Fichiers générés par les agents
├── ui_elements.py            # Composants visuels de l'interface
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🧠 Technologies utilisées

- [Streamlit](https://streamlit.io)
- [OpenAI GPT-4 / GPT-4o](https://platform.openai.com)
- [ChromaDB](https://www.trychroma.com) (vectorisation)
- [DuckDuckGo API](https://duckduckgo.com) (recherche web intégrée)
- Python 3.10+

---

## 🙌 Contributions

Les contributions sont les bienvenues !  
Crée une issue ou une pull request si tu veux proposer une amélioration 💡

---

## 📄 Licence

Ce projet est open-source sous licence MIT.

---

*Développé avec ❤️ par [@noeljp](https://github.com/noeljp) – 2024.*
```
