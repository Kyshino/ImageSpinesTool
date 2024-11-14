import json
import os
import sys
from variables import side_margin as default_side_margin
from variables import spacing as default_spacing
from variables import image_folder as default_image_folder
from variables import output_folder as default_output_folder
from variables import reddit_client_id as default_reddit_client_id
from variables import reddit_client_secret as default_reddit_client_secret

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
            return {
                'side_margin': default_side_margin,
                'spacing': default_spacing,
                'image_folder': default_image_folder,
                'output_folder': default_output_folder,
                'reddit_client_id': default_reddit_client_id,
                'reddit_client_secret': default_reddit_client_secret
            }
    return {
        'side_margin': default_side_margin,
        'spacing': default_spacing,
        'image_folder': default_image_folder,
        'output_folder': default_output_folder,
        'reddit_client_id': default_reddit_client_id,
        'reddit_client_secret': default_reddit_client_secret
    }

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
    value = config.get('side_margin', default_side_margin)
    return default_side_margin if value == '' else value

def set_side_margin(value):
    config = load_config()
    config['side_margin'] = value
    return save_config(config)

def get_spacing():
    config = load_config()
    value = config.get('spacing', default_spacing)
    return default_spacing if value == '' else value

def set_spacing(value):
    config = load_config()
    config['spacing'] = value
    return save_config(config)

def get_image_folder():
    config = load_config()
    value = config.get('image_folder', default_image_folder)
    return default_image_folder if value == '' else value

def set_image_folder(value):
    config = load_config()
    config['image_folder'] = value
    return save_config(config)

def get_output_folder():
    config = load_config()
    value = config.get('output_folder', default_output_folder)
    return default_output_folder if value == '' else value

def set_output_folder(value):
    config = load_config()
    config['output_folder'] = value
    return save_config(config)

def get_reddit_client_id():
    config = load_config()
    value = config.get('reddit_client_id', default_reddit_client_id)
    return default_reddit_client_id if value == '' else value

def set_reddit_client_id(value):
    config = load_config()
    config['reddit_client_id'] = value
    return save_config(config)

def get_reddit_client_secret():
    config = load_config()
    value = config.get('reddit_client_secret', default_reddit_client_secret)
    return default_reddit_client_secret if value == '' else value

def set_reddit_client_secret(value):
    config = load_config()
    config['reddit_client_secret'] = value
    return save_config(config) 