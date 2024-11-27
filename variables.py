import os
language_map = {
    "English": "en",
    "Español": "es",
    "Français": "fr",
    "Deutsch": "de",
    "Italiano": "it",
    "Português": "pt",
    "Русский": "ru",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko"
}

sizes = {
    "Switch PET": (131, 2000),  # 17cm x 1.1cm
    "Switch without PET": (112, 1890),  # 16cm x 0.95cm
}

paper_horizontal_sizes = {
    "A4 (210mm x 297mm)": (3508, 2480),  # Horizontal: 297mm x Vertical: 210mm
    "A3 (297mm x 420mm)": (4961, 3508),  # Horizontal: 420mm x Vertical: 297mm
    "B4 (364mm x 257mm)": (5144, 3035),  # Horizontal: 364mm x Vertical: 257mm
    "Letter (216mm x 279mm)": (3508, 2551),  # Horizontal: 279mm x Vertical: 216mm
    "Legal (355.6mm x 215.9mm)": (4200, 2550),  # Horizontal: 355.6mm x Vertical: 215.9mm
}

side_margin = 60
spacing = 1

image_folder = r"C:\Users\Spines\Desktop\SpinesImages"
output_folder = r"C:\Users\Spines\Desktop\SpinesImages\Output"
reddit_client_id = ""
reddit_client_secret = ""

switch_color = '#DA1820'

colors = {
    'switch_color': switch_color,  # Color rojo por defecto
    'blue': '#0066CC',  # El azul que usamos antes
    # Puedes añadir más colores aquí
} 

switch_color_enabled = False

TEMPLATES = {
    "switch": os.path.join(os.path.dirname(__file__), "templates", "switch_spine_template.png"),
    "wii": os.path.join(os.path.dirname(__file__), "templates", "wii_spine_template.png")
}

switch_spines_url = "https://mega.nz/folder/PYskFBAa#oiv6fG9BFveoTIDqnqZ13g"

project_url = "https://api.github.com/repos/Kyshino/ImageSpinesTool/releases/latest"