from typing import List
from core.rag_manager import RAGManager
from core.llm import run_chat_completion
import time
import tiktoken

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


3. **Interagire avec un autre agent (obligatoire)**  
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
        self.name = name 
        self.role_name = role_name 
        self.system_prompt = system_prompt + "\n\n" + tool_instruction 
        self.memory = memory 
        self.max_context_tokens_history = max_context_tokens_history 
        self.shared_metamemory = shared_metamemory 
        self.conversation_history = []
        self.rag_manager = RAGManager(memory)

        print(f"Agent {self.name} initialisé avec rôle : {self.role_name}")

    def _get_base_context(self) -> List[dict]:
        return [{"role": "system", "content": self.system_prompt}]

    def _get_relevant_context(self, query: str, k: int = 3) -> List[str]:
        search = self.rag_manager.get_context(query=query, k=k)
        if not search:
            return []

        joined_docs = "\\n---\\n".join(search)
        resume = run_chat_completion(
            system_prompt="Tu es un agent IA. Résume les résultats suivants de manière concise.",
            user_prompt=joined_docs,
            model="gpt-4o",
            temperature=0.1,
            max_tokens=500
        )
        return resume.split("\\n---\\n")

    def _build_context(self, user_message: str) -> List[dict]:
        base = self._get_base_context()
        base += self.conversation_history[-5:] if len(self.conversation_history) > 5 else self.conversation_history
        base += [{"role": "user", "content": f"[Info partagée] {m}"} for m in self.shared_metamemory[-3:]]

        for snippet in self._get_relevant_context(user_message):
            base.append({"role": "user", "content": f"[Doc technique] {snippet}"})

        base.append({"role": "user", "content": user_message})
        return base

    def chat(self, user_message: str, max_tokens=2000) -> str:
        print(f"🧠 {self.name} traite une nouvelle requête...")
        context = self._build_context(user_message)

        response = run_chat_completion(
            system_prompt=context[0]["content"],
            user_prompt="\\n".join([msg["content"] for msg in context[1:]]),
            model="gpt-4o",
            temperature=0.2,
            max_tokens=max_tokens
        )

        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": response})

        self.shared_metamemory.append(f"{self.name}: {response}")
        self.rag_manager.add_document(response)

        return response
