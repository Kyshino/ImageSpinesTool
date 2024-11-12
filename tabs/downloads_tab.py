from tkinter import Frame, Label

class DownloadsTab(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Configurar el grid del tab
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.setup_ui()
        parent.add(self, text="Downloads")

    def setup_ui(self):
        downloads_label = Label(self, text="Downloads Section")
        downloads_label.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')