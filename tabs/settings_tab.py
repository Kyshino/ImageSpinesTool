from tkinter import Frame, Label, StringVar, messagebox
from tkinter import ttk
from translations.texts import texts
from utils.widgets import create_button
from utils.config_manager import get_side_margin, set_side_margin
from variables import side_margin as default_side_margin

class SettingsTab(Frame):
    def __init__(self, parent, current_language):
        super().__init__(parent)
        self.current_language = current_language
        
        # Configurar el grid del tab
        self.grid_columnconfigure(1, weight=1)
        
        self.setup_variables()
        self.setup_ui()
        parent.add(self, text=texts[self.current_language]['settings_tab'])

    def setup_variables(self):
        self.side_margin = StringVar(value=str(get_side_margin()))

    def setup_ui(self):
        # Label con valor por defecto
        self.margin_label = Label(
            self, 
            text=f"{texts[self.current_language]['side_margin_label']} (default: {default_side_margin})"
        )
        self.margin_label.grid(row=0, column=0, padx=(10,5), pady=10, sticky='w')
        
        # Entry para el valor
        self.margin_entry = ttk.Entry(self, textvariable=self.side_margin, width=10)
        self.margin_entry.grid(row=0, column=1, padx=(0,10), pady=10, sticky='w')

        # Save button
        self.save_button = ttk.Button(
            self,
            text=texts[self.current_language]['save_button'],
            command=self.save_settings
        )
        self.save_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky='w')

    def save_settings(self):
        try:
            new_margin = int(self.side_margin.get())
            if new_margin < 0:
                raise ValueError("Margin must be positive")
            set_side_margin(new_margin)
            messagebox.showinfo("Success", texts[self.current_language]['settings_saved'])
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number")

    def update_language(self, new_language):
        self.current_language = new_language
        # Update texts
        self.master.tab(self, text=texts[self.current_language]['settings_tab'])
        
        # Update label with default value
        self.margin_label.config(
            text=f"{texts[self.current_language]['side_margin_label']} (default: {default_side_margin})"
        )
        
        # Update save button
        self.save_button.config(text=texts[self.current_language]['save_button'])