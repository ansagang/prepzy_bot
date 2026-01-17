from pathlib import Path

def get_project_root(path):
    root = Path(__file__).parent.parent
    filename = root.joinpath(path)
    return filename