import json
import os

CONFIG_FILE = 'config.json'

def save_config(theme):
    config = {'theme': theme}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {'theme': 'journal'}  # 默认主题