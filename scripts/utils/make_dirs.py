import os

def make_dirs(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)