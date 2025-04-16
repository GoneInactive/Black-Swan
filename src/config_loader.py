# src/config_loader.py

import yaml
import os

def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # src/
    project_root = os.path.abspath(os.path.join(base_dir, ".."))  # project-root/
    config_path = os.path.join(project_root, "config", "config.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

config = load_config()

KRAKEN_API_KEY = config['KRAKEN']['API_KEY']
KRAKEN_API_SECRET = config['KRAKEN']['API_SECRET']
