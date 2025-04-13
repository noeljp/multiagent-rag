import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import html2text
import re
from urllib.parse import urlparse

from openai import OpenAI
client2 = OpenAI()
import streamlit as st
import time
import io
from PyPDF2 import PdfReader

def clean_text(text: str) -> str:
    """Nettoie le texte Markdown pour éliminer les caractères superflus."""
    text = re.sub(r'\n{3,}', '\n\n', text)  # Pas plus de 2 sauts de ligne
    text = re.sub(r'[ \t]+', ' ', text)     # Espaces multiples → un seul espace
    return text.strip()

def resume_search_results(text : str, query : str) -> str:
    # on donne a une ia le texte a resumé
    # on utilise l'ia pour resumé le texte
    # on retourne le texte resumé
    
    # limite le text à  4096 token
    if len(text) > 4096:
        text = text[0:4096]


    prompt_system = {"role": "system", "content": "Tu es un agent IA utile. qui résume les texte de manière précise et concise , si le contenu n'est pas pertinant pour la question,répond par ###NOPE"}
    user_prompt = {"role": "user", "content": f"La question:\n{query}\La recherche :\n{text}\n---\n"}
    response = client2.chat.completions.create(
        model="gpt-4",
        messages = [prompt_system, user_prompt],
        temperature=0.2,
        
        max_tokens=330
    )
    return response.choices[0].message.content

def fetch_page_text(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10, stream=True)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()

        if "application/pdf" in content_type:
            
            pdf_data = response.content
            reader = PdfReader(io.BytesIO(pdf_data))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text or "📄 PDF récupéré mais aucun texte détecté."

        elif "text/html" in content_type:
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
                tag.decompose()
            text = soup.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines()]
            return "\n".join(line for line in lines if line)

        else:
            return f"📎 Contenu non supporté ({content_type}), aucun texte extrait."

    except Exception as e:
        return f"❌ Erreur de récupération de contenu : {e}"




def is_valid_result(href: str) -> bool:
    """Filtre les résultats non exploitables comme ceux de Google ou YouTube."""
    if not href:
        return False
    bad_domains = [ "google.","youtube.", "facebook.", "linkedin."]
    return not any(domain in href for domain in bad_domains)

def duckduckgo_search_and_browse(response: str, follow_links: bool = True, max_links: int = 5) -> str:
    """
    Recherche les requêtes ##INTERNET("...") dans la réponse de l'agent, 
    effectue une recherche sur DuckDuckGo et explore les résultats.

    Args:
        response (str): La réponse contenant les requêtes de recherche Internet.
        follow_links (bool): Si True, explore les pages des résultats.
        max_links (int): Nombre maximum de résultats à suivre.

    Returns:
        str: Résumé formaté des résultats de recherche et du contenu extrait.
    """
    search_queries = re.findall(r'##INTERNET\("(.+?)"\)', response)
    if not search_queries:
        return ""

    final_output = []

    for query in search_queries:
        st.info(f"🔎 Recherche Internet : **{query}**")
        output = [f"🔎 Résultats pour : **{query}**\n"]

        try:
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=10)  # Prend plus de résultats pour pouvoir filtrer
                valid_results = [r for r in results if is_valid_result(r.get("href", ""))][:max_links]

                for i, r in enumerate(valid_results, 1):
                    title = r.get("title", "Sans titre")
                    href = r.get("href", "")
                    output.append(f"### 🔗 {i}. {title}\n{href}")

                    if follow_links and href:
                        page_text = fetch_page_text(href)
                        summarized_text = resume_search_results(page_text, query)
                        output.append(f"**📝 Contenu extrait :**\n\n{summarized_text}\n")

            search_result_text = "\n\n".join(output)
            st.info(f"📚 Résultats de la recherche :\n\n{search_result_text}")
            final_output.append(search_result_text)
            time.sleep(1.5)  # Petit délai entre les requêtes

        except Exception as e:
            error_msg = f"❌ Erreur pendant la recherche : {e}"
            st.error(error_msg)
            final_output.append(error_msg)

    return "\n\n".join(final_output)


if __name__ == "__main__":
    recherche = duckduckgo_search_and_browse("**innovations récentes en intelligence artificielle 2023**")
    print(recherche)
    