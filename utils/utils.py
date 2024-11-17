import webbrowser
import requests
import packaging.version as version
from tkinter import messagebox
from translations.texts import texts
from version import VERSION

def open_support_link():
    webbrowser.open("https://www.paypal.com/donate/?hosted_button_id=RANLKSWR8UZC2")

def check_for_updates(current_language):
    try:
        response = requests.get('https://api.github.com/repos/Kyshino/ImageSpinesTool/releases/latest')
        if response.status_code == 200:
            data = response.json()
            latest_version = data['tag_name'].replace('v', '')
            current_version = VERSION
            
            if version.parse(latest_version) > version.parse(current_version):
                mensaje = texts[current_language]['update_available'].format(latest_version, current_version)
                if messagebox.askyesno(texts[current_language]['update_title'], mensaje):
                    if data['assets'] and len(data['assets']) > 0:
                        download_url = data['assets'][0]['browser_download_url']
                        webbrowser.open(download_url)
    except Exception as e:
        print(f"Error al verificar actualizaciones: {e}") 