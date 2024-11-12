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
        
        # Configure the grid of the tab
        self.grid_columnconfigure(0, weight=1)
        
        self.setup_variables()
        self.setup_ui()
        parent.add(self, text=texts[self.current_language]['settings_tab'])

    def setup_variables(self):
        self.side_margin = StringVar(value=str(get_side_margin()))

    def setup_ui(self):
        # Frame for side margin
        margin_frame = Frame(self)
        margin_frame.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        # Label with default value
        margin_label = Label(
            margin_frame, 
            text=f"{texts[self.current_language]['side_margin_label']} (default: {default_side_margin})"
        )
        margin_label.pack(side='left', padx=(0, 10))
        
        # Entry for the value
        self.margin_entry = ttk.Entry(margin_frame, textvariable=self.side_margin, width=10)
        self.margin_entry.pack(side='left')

        # Save button
        self.save_button = create_button(
            self,
            texts[self.current_language]['save_button'],
            self.save_settings,
            1
        )

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
        for widget in self.winfo_children():
            if isinstance(widget, Frame):
                for child in widget.winfo_children():
                    if isinstance(child, Label):
                        child.config(
                            text=f"{texts[self.current_language]['side_margin_label']} (default: {default_side_margin})"
                        )
        
        # Update save button
        self.save_button.config(text=texts[self.current_language]['save_button'])