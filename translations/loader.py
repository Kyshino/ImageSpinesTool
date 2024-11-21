import yaml
import os

def get_translations():
    translations = {}
    translations_dir = os.path.dirname(__file__)
    
    for file in os.listdir(translations_dir):
        if file.endswith('.yml'):
            lang_code = file.split('.')[0]
            try:
                with open(os.path.join(translations_dir, file), 'r', encoding='utf-8') as f:
                    translations[lang_code] = yaml.safe_load(f)
            except Exception as e:
                print(f"Error loading {file}: {str(e)}")
    
    return translations

translations = get_translations()

def get_text(lang_code, key, default=''):
    try:
        return translations[lang_code][key]
    except:
        return default