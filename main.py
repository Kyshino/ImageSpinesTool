from tkinter import Tk, Label, Frame, StringVar
from tkinter import ttk
from PIL import Image, ImageTk
from tabs.processing_tab import ProcessingTab
from tabs.settings_tab import SettingsTab
from translations.texts import texts
from variables import language_map

class MainApplication:
    def __init__(self):
        self.root = Tk()
        self.current_language = 'en'
        self.setup_window()
        self.setup_language_frame()
        self.setup_notebook()
        self.add_signature()
        
    def setup_window(self):
        self.root.title('Image Spines Tool v0.5-beta')
        
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
        window_height = 370
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{int(y)}")

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.configure(padx=20, pady=20)

    def setup_language_frame(self):
        language_frame = Frame(self.root)
        language_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=(0, 10))

        language_frame.grid_columnconfigure(1, weight=1)

        self.language_selected = StringVar(value="English")
        language_label = Label(language_frame, text="Select language:")
        language_label.grid(row=0, column=0, padx=(0, 10), pady=5)

        language_combobox = ttk.Combobox(
            language_frame, 
            textvariable=self.language_selected, 
            values=list(language_map.keys()), 
            state='readonly', 
            width=15
        )
        language_combobox.grid(row=0, column=1, sticky='w', pady=5)
        language_combobox.bind("<<ComboboxSelected>>", self.on_language_change)

    def setup_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, padx=10, pady=(0, 10), sticky='nsew')

        # Inicializar tabs
        self.processing_tab = ProcessingTab(self.notebook, self.current_language)
        self.settings_tab = SettingsTab(self.notebook, self.current_language)

    def on_language_change(self, event):
        selected_lang = self.language_selected.get()
        lang_code = language_map[selected_lang]
        self.current_language = lang_code
        self.processing_tab.update_language(lang_code)
        self.settings_tab.update_language(lang_code)
        self.notebook.tab(self.processing_tab, text=texts[self.current_language]['image_processing_tab'])
        self.notebook.tab(self.settings_tab, text=texts[self.current_language]['settings_tab'])

    def add_signature(self):
        signature = Label(self.root, text="By Kyshino", font=('Arial', 8), fg='gray', bg=self.root.cget("bg"))
        signature.place(relx=0.98, rely=0.99, anchor='se')

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApplication()
    app.run()
