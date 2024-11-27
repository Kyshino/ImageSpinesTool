from tkinter import Frame, Label
from translations import get_text
from variables import switch_spines_url

class DownloadsTab(Frame):
    def __init__(self, parent, current_language):
        super().__init__(parent)
        self.current_language = current_language
        self.setup_ui()

    def setup_ui(self):
        self.label_switch_spines = Label(self, text=f"{get_text(self.current_language, 'switch_spines_label', 'Switch Spines')}:")
        self.label_switch_spines.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.link_label = Label(self, text=get_text(self.current_language, 'download_link', 'Download Here'), fg='blue', cursor='hand2')
        self.link_label.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        self.link_label.bind("<Button-1>", self.download_link_switch_spines)

    def download_link_switch_spines(self, event):
        import webbrowser
        webbrowser.open(switch_spines_url)

    def update_language(self, new_language):
        self.current_language = new_language
        self.label_switch_spines.config(text=f"{get_text(new_language, 'switch_spines_label', 'Switch Spines')}:")
        self.link_label.config(text=get_text(new_language, 'download_link', 'Download Here'))