import json
import os
import multiprocessing
from utils.messages import get_message

DEFAULT_CONFIG = {
    "language": "ru",
    "processes": multiprocessing.cpu_count(),
    "threads_per_process": 25,
    "timeout": 2,
    "batch_size": 50,
    "output_file": "found_wallets.json"
}

def load_config():
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
            config = {**DEFAULT_CONFIG, **user_config}
    else:
        config = DEFAULT_CONFIG.copy()
    return config

def save_config(config):
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def get_text(key, config=None, **kwargs):
    lang = config.get('language', 'ru') if config else 'ru'
    return get_message(key, lang, **kwargs)