import json
import os
import sys
from variables import side_margin as default_side_margin

def get_executable_path():
    """Get the path of the executable or script"""
    if getattr(sys, 'frozen', False):
        # If it's an executable
        return os.path.dirname(sys.executable)
    else:
        # If it's the Python script
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_config_file_path():
    """Get the full path to settings.json"""
    return os.path.join(get_executable_path(), 'settings.json')

def load_config():
    config_file = get_config_file_path()
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            return {'side_margin': default_side_margin}
    return {'side_margin': default_side_margin}

def save_config(config):
    config_file = get_config_file_path()
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except:
        return False

def get_side_margin():
    config = load_config()
    return config.get('side_margin', default_side_margin)

def set_side_margin(value):
    config = load_config()
    config['side_margin'] = value
    return save_config(config) 