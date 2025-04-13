from multiprocessing import context
import os
import re
import subprocess
import streamlit as st

def execute_terminal_blocks(response: str, workspace: str ) -> str:
    """Exécute les blocs de commande terminal trouvés dans la réponse de l’agent."""
    context = ""
    terminal_matches = re.findall(
        r'##RUN_TERMINAL\s+```(?:bash|sh)?\s*\n(.*?)\n```',
        response,
        re.DOTALL
    )

    if not terminal_matches:
        return context  # rien à faire

    generated_root = workspace

    for i, command in enumerate(terminal_matches, 1):
        st.markdown(f"### 🖥️ Exécution terminal #{i} demandée par l’agent :")
        st.code(command.strip(), language="bash")

        try:
            # 🔧 Nettoyage des commentaires -> echo
            processed_command = re.sub(r'^\s*#(.*)', r'echo "\1"', command, flags=re.MULTILINE)
            processed_command = processed_command.replace("python3", "python")

            # ✂️ Découpage ligne par ligne
            individual_commands = [
                line.strip() for line in processed_command.strip().split('\n') if line.strip()
            ]

            for j, cmd in enumerate(individual_commands, 1):
                st.markdown(f"#### 🔹 Sous-commande {j} : `{cmd}`")

                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=generated_root
                )

                stdout = result.stdout.strip()
                stderr = result.stderr.strip()

                if stdout:
                    st.success("✅ Résultat :")
                    st.code(stdout)
                if stderr:
                    st.warning("⚠️ Erreurs ou avertissements :")
                    st.code(stderr)

                context += (
                    f"\n\n🖥️ Sous-commande exécutée : `{cmd}`"
                    f"\n\n🔧 Résultat :\n{stdout if stdout else '(aucune sortie)'}"
                    f"\n\n⚠️ Erreurs :\n{stderr if stderr else '(aucune)'}"
                )

        except subprocess.TimeoutExpired:
            st.error("⏱️ Erreur : une sous-commande a dépassé le temps limite.")
            context += f"\n\n❌ Timeout pendant l'exécution d’une commande dans le bloc :\n```bash\n{command.strip()}\n```"
        except Exception as e:
            st.error(f"❌ Erreur lors de l’exécution du bloc de commandes : {e}")
            context += f"\n\n❌ Erreur pendant le bloc de commandes : `{command.strip()}`\n{e}"

    return context
