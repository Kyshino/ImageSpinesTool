import webbrowser
import requests
import packaging.version as version
from tkinter import messagebox
from translations import get_text
from version import VERSION

def open_support_link():
    webbrowser.open("https://www.paypal.com/donate/?hosted_button_id=RANLKSWR8UZC2")

def open_kofi_link():
    webbrowser.open("https://ko-fi.com/kyshino")

# Temporarily disabled update checking
"""
try:
    response = requests.get('https://api.github.com/repos/Kyshino/ImageSpinesTool/releases/latest')
    if response.status_code == 200:
        data = response.json()
        latest_version = data['tag_name'].replace('v', '')
        current_version = VERSION
        
        if version.parse(latest_version) > version.parse(current_version):
            mensaje = get_text(current_language, 'update_available', 'A new version is available: {}\nYour current version is: {}').format(
                latest_version, current_version
            )
            if messagebox.askyesno(
                get_text(current_language, 'update_title', 'Update Available'), 
                mensaje
            ):
                if data['assets'] and len(data['assets']) > 0:
                    download_url = data['assets'][0]['browser_download_url']
                    webbrowser.open(download_url)
except Exception as e:
    print(f"Error al verificar actualizaciones: {e}") 
"""