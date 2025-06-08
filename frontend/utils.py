import os

def get_database_dir_path():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    return script_directory
