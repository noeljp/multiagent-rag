import os
import uuid
import signal
import subprocess
import time

class DetachedScriptRunner:
    def __init__(self, script_code: str, working_dir: str = "./workspace"):
        self.script_code = script_code
        self.working_dir = working_dir
        self.script_id = uuid.uuid4().hex[:8]
        self.script_name = f"external_{self.script_id}.py"
        self.script_path = os.path.join(self.working_dir, self.script_name)
        self.stdout_path = os.path.join(self.working_dir, f"{self.script_id}_stdout.log")
        self.stderr_path = os.path.join(self.working_dir, f"{self.script_id}_stderr.log")
        self.pid = None
        self.process = None

    def start(self):
        os.makedirs(self.working_dir, exist_ok=True)

        with open(self.script_path, "w") as f:
            f.write(self.script_code)

        try:
            self.stdout_file = open(self.stdout_path, "w")
            self.stderr_file = open(self.stderr_path, "w")

            self.process = subprocess.Popen(
                ["python", self.script_path],
                stdout=self.stdout_file,
                stderr=self.stderr_file,
                cwd=self.working_dir,
                start_new_session=True
            )
            self.pid = self.process.pid
            time.sleep(1)
            return True, f"✅ Script lancé (PID: {self.pid})"
        except Exception as e:
            return False, f"❌ Erreur : {str(e)}"

    def read_logs(self) -> dict:
        return {
            "stdout": open(self.stdout_path, "r").read() if os.path.exists(self.stdout_path) else "",
            "stderr": open(self.stderr_path, "r").read() if os.path.exists(self.stderr_path) else ""
        }

    def stop(self) -> str:
        if not self.pid:
            return "⚠️ Aucun processus à arrêter."
        try:
            os.kill(self.pid, signal.SIGTERM)
            return f"✅ Processus {self.pid} arrêté."
        except ProcessLookupError:
            return f"⚠️ Aucun processus trouvé avec le PID {self.pid}."
        except Exception as e:
            return f"❌ Erreur lors de l'arrêt du processus : {str(e)}"

    def is_running(self) -> bool:
        if self.pid is None:
            return False
        try:
            os.kill(self.pid, 0)
            return True
        except OSError:
            return False

    def get_info(self) -> dict:
        return {
            "pid": self.pid,
            "script": self.script_path,
            "stdout_log": self.stdout_path,
            "stderr_log": self.stderr_path,
            "running": self.is_running()
        }

    def __del__(self):
        if self.process:
            self.process.kill()
        if hasattr(self, "stdout_file"):
            self.stdout_file.close()
        if hasattr(self, "stderr_file"):
            self.stderr_file.close()
        if os.path.exists(self.script_path):
            os.remove(self.script_path)
        if os.path.exists(self.stdout_path):
            os.remove(self.stdout_path)
        if os.path.exists(self.stderr_path):
            os.remove(self.stderr_path)
# main initialisation
            
if __name__ == "__main__":
    # Exemple serveur Flask
    script1 = """
    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def hello():
        return "Hello depuis l'agent IA !"

    app.run(host='0.0.0.0', port=5050)
    """
    # Exemple graphique matplotlib
    script2 = """
    import matplotlib.pyplot as plt
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.title("Test graphique")
    plt.show()
    """
    # Execute le script1
    runner1 = DetachedScriptRunner(script1)
    status, message = runner1.start()
    print(message)
    # Execute le script2
    runner2 = DetachedScriptRunner(script2)
    status, message = runner2.start()
    print(message)
    # Affiche les logs
    print(runner1.read_logs())
    print(runner2.read_logs())
    # Arrete les scripts
    print(runner1.stop())
    print(runner2.stop())
    # Affiche les infos
    print(runner1.get_info())
    print(runner2.get_info())
    # Supprime les fichiers temporaires
    del runner1
    del runner2
    

            
         