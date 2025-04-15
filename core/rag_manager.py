import os
from typing import List
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from core.smart_splitter import SmartTextSplitter
import re
import unicodedata

def normalize_collection_name(name: str) -> str:
    # Supprime les accents
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    # Remplace tout caractère non alphanumérique ou _ ou - par un underscore
    name = re.sub(r"[^\w\-]", "_", name)
    # Réduit les séquences de _ à un seul _
    name = re.sub(r"_+", "_", name)
    # Supprime les underscores ou tirets au début/fin
    name = name.strip("_-")
    # Force en minuscules (optionnel)
    return name.lower()


class RAGManager:
    def __init__(self, project_name: str, base_path: str = "./chroma_db"):
        self.project_name = normalize_collection_name(project_name)
        self.project_path = os.path.join(base_path, project_name)
        os.makedirs(self.project_path, exist_ok=True)

        self.embedding_model = OpenAIEmbeddings()
        self.vectorstore = Chroma(
            collection_name=project_name,
            embedding_function=self.embedding_model,
            persist_directory=self.project_path
        )

        # Remplace RecursiveCharacterTextSplitter par SmartTextSplitter
        self.text_splitter = SmartTextSplitter(chunk_size=500,chunk_overlap=50)

    def add_document(self, text: str):
        """
        Ajoute un document à la base vectorielle du projet.
        """

        chunks = self.text_splitter.split_text(text)
        self.vectorstore.add_texts(chunks)

    def get_context(self, query: str, k: int = 3) -> List[str]:
        """
        Récupère les k chunks les plus pertinents.
        """
        docs = self.vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]

    def generate_answer(self, user_message: str, system_prompt: str = "Tu es un agent IA utile.") -> str:
        """
        Génère une réponse basée sur le contexte vectoriel.
        """
        context_chunks = self.get_context(user_message, k=3)
        context_text = "\n".join(context_chunks)

        full_prompt = f"{system_prompt}\n\nContexte:\n{context_text}\n\nQuestion:\n{user_message}"

        llm = OpenAI(model="gpt-3.5-turbo", temperature=0)
        response = llm.invoke(full_prompt)
        return response.content
