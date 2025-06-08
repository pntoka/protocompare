import os

def get_uploads_dir_path():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    return script_directory
