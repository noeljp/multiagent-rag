# 🧠 Core - Intelligence et moteur de traitement

Ce dossier contient les composants centraux de logique métier, notamment ceux qui interagissent avec les LLMs, les embeddings et les algorithmes de traitement de texte.

---

## 📁 Fichiers inclus

### `llm.py`
- Enveloppe les appels à OpenAI (`run_chat_completion`)
- Gère la structure des prompts, les modèles utilisés (GPT-4, GPT-4o...)
- Mesure le temps et les tokens utilisés pour chaque réponse

### `rag_manager.py`
- Gère le moteur RAG avec embeddings vectoriels (ChromaDB)
- Utilise `SmartTextSplitter` pour découper intelligemment les documents
- Fournit les fonctions :
  - `add_document()`
  - `get_context()`
  - `generate_answer()`

### `smart_splitter.py`
- Splitter intelligent qui découpe un texte en blocs structurés :
  - Ne coupe pas les blocs JSON ou `code`
  - Utilise `langchain.text_splitter.RecursiveCharacterTextSplitter` en fallback
- Améliore significativement la qualité du chunking pour la recherche vectorielle

---

## 🎯 Objectif du module

Ces fichiers forment le noyau des interactions IA :
- Communication avec les modèles de langage
- Préparation des prompts et du contexte
- Recherche documentaire intelligente via embeddings

---

## 🛠️ Utilisation typique

```python
from core.llm import run_chat_completion
from core.rag_manager import RAGManager

rag = RAGManager("mon_projet")
rag.add_document("Voici un texte à indexer...")
result = rag.get_context("Que contient ce document ?")
```

---

## 📌 À venir

- Support de modèles locaux via `llama.cpp` ou `ollama`
- Personnalisation des embeddings
- Export JSON du graphe de contexte

---

## 👨‍💻 Auteur

Développé dans le cadre du projet **multi-agent RAG**.
