import streamlit as st
import zipfile
import os
from io import BytesIO

def export_history(history):
    export = "\\n\\n".join(history)
    st.download_button(
        "📅 Télécharger le compte-rendu",
        data=export,
        file_name="discussion_projet.txt"
    )

def download_zip_with_history_and_generated(workspace: str):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for foldername, _, filenames in os.walk(workspace):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, workspace)
                zip_file.write(file_path, arcname=os.path.join("workspace", arcname))

        if "history" in st.session_state:
            history_txt = "\\n\\n".join(st.session_state.history)
            zip_file.writestr("historique.txt", history_txt)

    zip_buffer.seek(0)
    st.download_button(
        label="📦 Télécharger les fichiers générés + historique (.zip)",
        data=zip_buffer,
        file_name="projet_complet.zip",
        mime="application/zip"
    )