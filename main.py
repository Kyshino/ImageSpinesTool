from tkinter import Tk, Label, Frame, StringVar, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from tabs.processing_tab import ProcessingTab
from tabs.settings_tab import SettingsTab
from tabs.spine_creator_tab import SpineCreatorTab
from translations import translations, get_text
from variables import language_map
from version import VERSION, FULL_APP_NAME
from utils.utils import (open_support_link, open_kofi_link, check_for_updates)

class MainApplication:
    def __init__(self):
        self.root = Tk()
        self.current_language = 'en'
        self.current_version = VERSION
        self.support_link = None
        self.kofi_link = None
        self.setup_window()
        self.setup_language_frame()
        self.setup_notebook()
        self.add_signature()
        check_for_updates(self.current_language)
        
    def setup_window(self):
        self.root.title(FULL_APP_NAME)
        
        # Try to set favicon, but continue if not found
        try:
            favicon_path = './images/favicon.ico'
            favicon_image = Image.open(favicon_path)
            favicon = ImageTk.PhotoImage(favicon_image)
            self.root.iconphoto(False, favicon)
        except:
            # If favicon is not found, continue without it
            pass
        
        self.root.resizable(False, False)
        
        window_width = 800
        window_height = 500
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{int(y)}")

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.configure(padx=20, pady=20)

    def setup_language_frame(self):
        language_frame = ttk.Frame(self.root)
        language_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=(0, 10))
        language_frame.grid_columnconfigure(1, weight=1)

        self.language_label = ttk.Label(
            language_frame, 
            text=get_text(self.current_language, 'select_language', 'Select language:')
        )
        self.language_label.grid(row=0, column=0, padx=(0, 10), pady=5)

        self.language_selected = StringVar(value="English")
        self.language_combobox = ttk.Combobox(
            language_frame, 
            textvariable=self.language_selected, 
            values=list(language_map.keys()), 
            state='readonly', 
            width=15
        )
        self.language_combobox.grid(row=0, column=1, sticky='w', pady=5)
        self.language_combobox.bind("<<ComboboxSelected>>", self.on_language_change)

    def setup_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        
        # Crear las pestañas
        self.processing_tab = ProcessingTab(self.notebook, self.current_language)
        self.settings_tab = SettingsTab(self.notebook, self.current_language)
        self.spine_creator_tab = SpineCreatorTab(self.notebook, self.current_language)
        
        # Conectar las pestañas (añadir el processing_tab como observador del settings_tab)
        self.settings_tab.add_observer(self.processing_tab)
        
        # Añadir las pestañas al notebook
        self.notebook.add(self.processing_tab, text=get_text(self.current_language, 'image_processing_tab', 'Image Processing'))
        self.notebook.add(self.settings_tab, text=get_text(self.current_language, 'settings_tab', 'Settings'))
        self.notebook.add(self.spine_creator_tab, text=get_text(self.current_language, 'spine_creator_tab', 'Spine Creator'))

    def on_language_change(self, event):
        selected_lang = self.language_selected.get()
        lang_code = language_map[selected_lang]
        self.current_language = lang_code
        
        # Actualizar las pestañas
        self.processing_tab.update_language(lang_code)
        self.settings_tab.update_language(lang_code)
        self.spine_creator_tab.update_language(lang_code)
        
        # Actualizar los títulos de las pestañas
        self.notebook.tab(self.processing_tab, text=get_text(lang_code, 'image_processing_tab', 'Image Processing'))
        self.notebook.tab(self.settings_tab, text=get_text(lang_code, 'settings_tab', 'Settings'))
        self.notebook.tab(self.spine_creator_tab, text=get_text(lang_code, 'spine_creator_tab', 'Spine Creator'))
        
        # Actualizar el enlace de soporte
        if self.support_link:
            self.support_link.config(text=f"• {get_text(lang_code, 'support_me', 'Support me')}")

        if self.kofi_link:
            self.kofi_link.config(text=f"• Become a Member on Ko-fi")

    def add_signature(self):
        signature_frame = Frame(self.root, bg=self.root.cget("bg"))
        signature_frame.place(relx=0.98, rely=0.99, anchor='se')

        signature = Label(signature_frame, text="By Kyshino |", font=('Arial', 8), fg='gray', bg=self.root.cget("bg"))
        signature.pack(side='left')

        self.support_link = Label(
            signature_frame, 
            text=f"• {get_text(self.current_language, 'support_me', 'Support me')}", 
            font=('Arial', 8), 
            fg='blue', 
            cursor='hand2',
            bg=self.root.cget("bg")
        )
        self.support_link.pack(side='left', padx=(0, 0))
        self.support_link.bind("<Button-1>", lambda e: self.open_kofi_link(e))

        self.kofi_link = Label(
            signature_frame, 
            text=f"• Become a Member on Ko-fi", 
            font=('Arial', 8), 
            fg='blue', 
            cursor='hand2',
            bg=self.root.cget("bg")
        )
        self.kofi_link.pack(side='left', padx=(0, 0))
        self.kofi_link.bind("<Button-1>", lambda e: self.open_kofi_link(e))



    def open_support_link(self, event):
        open_support_link()

    def open_kofi_link(self, event):
        open_kofi_link()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApplication()
    app.run()
