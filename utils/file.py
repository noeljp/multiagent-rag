import os
import re
import streamlit as st
from typing import List

def write_generated_files(response: str, workspace: str) -> List[str]:
    """Recherche et écrit les fichiers générés par un agent à partir de la réponse.

    Args:
        response (str): La réponse de l'agent contenant les blocs ##GENERATE_FILE.

    Returns:
        List[str]: Liste des chemins relatifs des fichiers écrits.
    """
    file_match = re.findall(
        r'##GENERATE_FILE\s+"(.+?)"\s+```(?:\w+)?\s*\n(.*?)\n```',
        response,
        re.DOTALL
    )

    generated_root = workspace
    written_files = []

    if file_match:
        st.markdown("### 📂 Fichiers générés (relatifs au dossier du script) :")

        for relative_path, file_content in file_match:
            try:
                # Nettoyage du chemin relatif
                relative_path = relative_path.lstrip("/\\")
                abs_path = os.path.join(generated_root, relative_path)

                # Création des répertoires si besoin
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)

                # Écriture du fichier
                with open(abs_path, "w", encoding="utf-8") as f:
                    f.write(file_content)

                written_files.append(relative_path)

                st.success(f"✅ Fichier écrit : `{relative_path}`")
                with st.expander(f"📄 Aperçu : {relative_path}"):
                    st.code(file_content)

            except Exception as e:
                st.error(f"❌ Erreur lors de l’écriture de `{relative_path}` : {e}")

    return written_files
