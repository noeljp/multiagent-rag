from openai import OpenAI
client = OpenAI()
import tiktoken
from typing import List
from rag_manager import RAGManager
import re
from utils.internet import duckduckgo_search_and_browse
import time


def count_tokens(messages, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    total_tokens = 0
    for msg in messages:
        total_tokens += 4
        total_tokens += len(encoding.encode(msg["content"]))
    total_tokens += 2
    return total_tokens

tool_instruction = f"Nous sommes aujourd'hui le{time.strftime('%d/%m/%Y')}.\n" + """
Tu disposes de plusieurs outils pour produire des livrables et collaborer.
Pour déclencher ces actions automatiquement, suis précisément les syntaxes suivantes dans tes réponses :

1. **Générer un fichier (facultatif)**  
   Utilise la balise :

   ##GENERATE_FILE "/chemin/vers/fichier"
   ```<lang>
   < contenu >
   ```
   (Place ton contenu entre les balises triple backticks.)

2. **Recherche sur Internet pour plus d'information**  
   Utilise la balise :

   ##INTERNET("Ma requête de recherche")


3. **Interaction (obligatoire) avec un autre agent**  
   Utilise la balise :

   ##AGENT("NomDeLAgent", "Votre requête ici")
   
   
4. **Exécuter une commande dans le terminal windows pour executer,tester ,valider ...(facultatif)**  
   Tu travailles dans le dossier generated_files. 
   Tous les chemins que tu utilises doivent être relatifs à ce dossier. 
   N’utilise jamais de chemins absolus (comme /scripts/… ou C:\…).
   Utilise la balise :

   ##RUN_TERMINAL
   ```bash
   <commande à exécuter>
   ```
5.  **Enfin, lorsque tu juges que tous les objectifs du projet sont atteints, tu dois faire figurer dans 
    ton propre `system_prompt` la balise suivante :
    ###PROJET_TERMINER\n"(Place ta commande entre les balises triple backticks.)


⚠️ **Important** : Seule l’utilisation exacte de ces syntaxes déclenchera les actions correspondantes.
7. **Note** : Reponds de manière direct orienté objectif et solution.
"""

class BaseAgent:
    def __init__(self, name: str, role_name: str, system_prompt: str, memory: str, shared_metamemory: List[str], max_context_tokens_history=2000):
        self.rag_manager = RAGManager(memory)
        self.name = name
        self.role_name = role_name
        self.system_prompt = system_prompt + "\n\n" + tool_instruction
        self.max_context_tokens_history = max_context_tokens_history
        self.conversation_history = []  # Historique local de l'agent
        self.shared_metamemory = shared_metamemory  # Métamémoire partagée

        print(f"Agent {self.name} initialisé avec rôle : {self.role_name}")

    def _get_base_context(self) -> List[dict]:
        return [{"role": "system", "content": self.system_prompt}]

    def _get_relevant_context(self, query: str, k: int = 3) -> List[str]:
        search = self.rag_manager.get_context(query=query, k=k)
        if not search:
            return []

        message = [{"role": "user", "content": "Résume les résultats suivants de manière concise:\n" + "\n---\n".join(search)}]
        resume = client.chat.completions.create(
            model="gpt-4o",
            messages=message,
            temperature=0.1,
            max_tokens=500
        )
        print("*"*20)
        print(f"Résumé des résultats RAG : {resume.choices[0].message.content}")
        return resume.choices[0].message.content.split("\n---\n")

    def _build_context(self, user_message: str) -> List[dict]:
        base = self._get_base_context()

        # Ajout des derniers échanges locaux
        local_context = self.conversation_history[-5:] if len(self.conversation_history) > 5 else self.conversation_history
        base += local_context

        # Ajout de la métamémoire partagée
        for entry in self.shared_metamemory[-3:]:
            base.append({"role": "user", "content": f"[Info partagée] {entry}"})

        # Contexte RAG enrichi selon la requête
        rag_context = self._get_relevant_context(user_message)
        for snippet in rag_context:
            base.append({"role": "user", "content": f"[Doc technique] {snippet}"})

        # Message courant de l'utilisateur
        base.append({"role": "user", "content": user_message})
        return base

    def chat(self, user_message: str, max_tokens=2000) -> str:
        print(f"\n🧠 {self.name} traite une nouvelle requête...")
        messages = self._build_context(user_message)

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.2,
            max_tokens=max_tokens
        )

        assistant_response = completion.choices[0].message.content

        # Historique local
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": assistant_response})

        # Ajout à la métamémoire partagée
        self.shared_metamemory.append(f"{self.name}: {assistant_response}")
        # Ajout à la mémoire de l'agent
        self.rag_manager.add_document(assistant_response)

        return assistant_response

# Utilitaire de résumé (externe à l'agent)
def resume_message(text: str) -> str:
    prompt_system = {"role": "system", "content": "Tu es un agent IA. Résume et reformule le message de manière claire, concise et enrichie."}
    user_prompt = {"role": "user", "content": text}
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[prompt_system, user_prompt],
        temperature=0.5,
        max_tokens=500
    )
    return response.choices[0].message.content
