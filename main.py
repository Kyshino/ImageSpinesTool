from tkinter import Tk, Label, Frame, StringVar, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from tabs.processing_tab import ProcessingTab
from tabs.settings_tab import SettingsTab
from translations.texts import texts
from variables import language_map
from utils.config_manager import (get_side_margin, set_side_margin,
                                get_spacing, set_spacing,
                                get_image_folder, set_image_folder,
                                get_output_folder, set_output_folder,
                                get_reddit_client_id, set_reddit_client_id,
                                get_reddit_client_secret, set_reddit_client_secret)
from threading import Thread

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
        window_height = 450
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
        self.settings_tab = SettingsTab(self.notebook, self.current_language)
        self.processing_tab = ProcessingTab(self.notebook, self.current_language)
        self.setup_downloads_frame()
        
        self.notebook.add(self.processing_tab, text=texts[self.current_language]['image_processing_tab'])
        self.notebook.add(self.downloads_frame, text=texts[self.current_language]['downloads_tab'])
        self.notebook.add(self.settings_tab, text=texts[self.current_language]['settings_tab'])
        
        self.notebook.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)

    def setup_downloads_frame(self):
        self.downloads_frame = ttk.Frame(self.notebook)
        
        # Frame principal para los inputs
        input_frame = ttk.Frame(self.downloads_frame)
        input_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)

        # Reddit Client ID (solo mostrar)
        ttk.Label(input_frame, text=texts[self.current_language]['client_id']).grid(row=0, column=0, sticky='e', padx=(0, 10), pady=5)
        client_id_label = ttk.Label(input_frame, text=get_reddit_client_id())
        client_id_label.grid(row=0, column=1, sticky='w', pady=5)

        # Reddit Client Secret (solo mostrar)
        ttk.Label(input_frame, text=texts[self.current_language]['client_secret']).grid(row=1, column=0, sticky='e', padx=(0, 10), pady=5)
        client_secret_label = ttk.Label(input_frame, text="*" * len(get_reddit_client_secret()))
        client_secret_label.grid(row=1, column=1, sticky='w', pady=5)

        input_frame.grid_columnconfigure(1, weight=1)

        # Frame para los botones
        button_frame = ttk.Frame(self.downloads_frame)
        button_frame.grid(row=1, column=0, sticky='ew', padx=20, pady=(0, 10))

        self.download_button = ttk.Button(
            button_frame, 
            text=texts[self.current_language]['download_spines'],
            command=self.download_switch_spines
        )
        self.download_button.grid(row=0, column=0, sticky='e')

        self.cancel_button = ttk.Button(
            button_frame, 
            text=texts[self.current_language]['cancel_download'],
            command=self.cancel_download,
            state='disabled'
        )
        self.cancel_button.grid(row=0, column=1, sticky='e', padx=(5, 0))

        button_frame.grid_columnconfigure(0, weight=1)

        # Frame para la barra de progreso
        progress_frame = ttk.Frame(self.downloads_frame)
        progress_frame.grid(row=2, column=0, sticky='ew', padx=20, pady=(0, 20))
        
        self.progress_var = StringVar(value="")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=200
        )
        self.progress_bar.grid(row=1, column=0, sticky='ew')
        
        progress_frame.grid_columnconfigure(0, weight=1)
        
        # Configurar expansión del frame principal
        self.downloads_frame.grid_columnconfigure(0, weight=1)
        self.downloads_frame.grid_rowconfigure(0, weight=1)

    def update_download_progress(self, progress, downloaded, skipped, total):
        progress = min(progress, 100)
        self.progress_bar['value'] = progress
        self.progress_var.set(texts[self.current_language]['download_progress'].format(
            downloaded=downloaded,
            skipped=skipped,
            total=total,
            progress=progress
        ))
        
    def download_switch_spines(self):
        self.is_downloading = True
        
        def download_thread():
            try:
                self.download_button.configure(state='disabled')
                self.cancel_button.configure(state='normal')
                
                # Verificar credenciales
                client_id = get_reddit_client_id()
                client_secret = get_reddit_client_secret()
                
                if not client_id or not client_secret:
                    raise Exception(texts[self.current_language]['missing_credentials'])
                
                self.progress_var.set(texts[self.current_language]['checking_credentials'])
                self.progress_bar['value'] = 0
                
                from downloaders.switch_spines_downloader import SwitchSpinesDownloader
                self.downloader = SwitchSpinesDownloader()
                
                # Verificar si las credenciales son válidas
                try:
                    if not self.downloader.verify_credentials(client_id, client_secret):
                        raise Exception(texts[self.current_language]['invalid_credentials'])
                except Exception as e:
                    if '401' in str(e) or '403' in str(e) or 'unauthorized' in str(e).lower() or 'forbidden' in str(e).lower():
                        raise Exception(texts[self.current_language]['invalid_credentials'])
                    else:
                        raise e  # Si es otro tipo de error, lo propagamos
                
                self.progress_var.set(texts[self.current_language]['credentials_ok'])
                
                def update_progress(progress, downloaded, skipped, total):
                    if not self.is_downloading:  # Verificar si se debe continuar
                        raise Exception("Download cancelled by user")
                    self.root.after(0, lambda: self.update_download_progress(progress, downloaded, skipped, total))
                
                self.downloader.set_progress_callback(update_progress)
                if not self.downloader.download_all():  # Verificar el resultado
                    raise Exception("Download cancelled by user")
                
                self.root.after(0, self.download_complete)
                
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.download_error(error_msg))
            finally:
                self.is_downloading = False
                self.cancel_button.configure(state='disabled')

        Thread(target=download_thread, daemon=True).start()

    def cancel_download(self):
        print("\n🛑 Cancel requested by user...")
        self.is_downloading = False
        self.progress_var.set("Download cancelled")
        self.progress_bar['value'] = 0
        self.download_button.configure(state='normal')
        self.cancel_button.configure(state='disabled')
        print("✅ Download cancelled successfully")

    def download_complete(self):
        self.progress_bar['value'] = 100
        self.progress_var.set("Download complete!")
        self.download_button.configure(state='normal')
        self.cancel_button.configure(state='disabled')
        messagebox.showinfo("Success", "Switch spines downloaded successfully!")
        self.progress_var.set("")
        self.progress_bar['value'] = 0

    def download_error(self, error_message):
        self.progress_bar['value'] = 0
        self.progress_var.set("")  # Limpiamos el mensaje de progreso
        self.download_button.configure(state='normal')
        self.cancel_button.configure(state='disabled')
        
        if error_message == "Download cancelled by user":
            self.progress_var.set(texts[self.current_language]['download_cancelled'])
        else:
            messagebox.showerror("Error", error_message)

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
