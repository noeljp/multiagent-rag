import os

def clean_workspace(workspace):
    for file in os.listdir(workspace):
        path = os.path.join(workspace, file)
        if os.path.isfile(path):
            os.remove(path)