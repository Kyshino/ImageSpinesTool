from tkinter import Frame, Label, StringVar, messagebox, filedialog
from tkinter import ttk
from translations.texts import texts
from utils.widgets import create_button
from utils.config_manager import (
    get_side_margin, set_side_margin,
    get_spacing, set_spacing,
    get_image_folder, set_image_folder,
    get_output_folder, set_output_folder
)
from variables import (
    side_margin as default_side_margin,
    spacing as default_spacing,
    image_folder as default_image_folder,
    output_folder as default_output_folder
)

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
        self.spacing = StringVar(value=str(get_spacing()))
        self.image_folder = StringVar(value=str(get_image_folder()))
        self.output_folder = StringVar(value=str(get_output_folder()))

    def setup_ui(self):
        # Margen lateral
        self.margin_label = Label(
            self, 
            text=f"{texts[self.current_language]['side_margin_label']} (default: {default_side_margin})"
        )
        self.margin_label.grid(row=0, column=0, padx=(10,5), pady=5, sticky='w')
        
        self.margin_entry = ttk.Entry(self, textvariable=self.side_margin, width=10)
        self.margin_entry.grid(row=0, column=1, padx=(0,10), pady=5, sticky='w')

        # Espaciado
        self.spacing_label = Label(
            self, 
            text=f"{texts[self.current_language]['spacing_label']} (default: {default_spacing})"
        )
        self.spacing_label.grid(row=1, column=0, padx=(10,5), pady=5, sticky='w')
        
        self.spacing_entry = ttk.Entry(self, textvariable=self.spacing, width=10)
        self.spacing_entry.grid(row=1, column=1, padx=(0,10), pady=5, sticky='w')

        # Carpeta de imágenes
        self.image_folder_label = Label(
            self, 
            text=f"{texts[self.current_language]['image_folder_label']}"
        )
        self.image_folder_label.grid(row=2, column=0, padx=(10,5), pady=5, sticky='w')
        
        image_folder_frame = Frame(self)
        image_folder_frame.grid(row=2, column=1, padx=(0,10), pady=5, sticky='ew')
        image_folder_frame.columnconfigure(0, weight=1)
        
        self.image_folder_entry = ttk.Entry(image_folder_frame, textvariable=self.image_folder, width=70)
        self.image_folder_entry.grid(row=0, column=0, sticky='ew')
        
        self.browse_image_button = ttk.Button(
            image_folder_frame,
            text="Browse",
            command=self.browse_image_folder
        )
        self.browse_image_button.grid(row=0, column=1, padx=(5,0))

        # Carpeta de salida
        self.output_folder_label = Label(
            self, 
            text=f"{texts[self.current_language]['output_folder_label']}"
        )
        self.output_folder_label.grid(row=3, column=0, padx=(10,5), pady=5, sticky='w')
        
        output_folder_frame = Frame(self)
        output_folder_frame.grid(row=3, column=1, padx=(0,10), pady=5, sticky='ew')
        output_folder_frame.columnconfigure(0, weight=1)
        
        self.output_folder_entry = ttk.Entry(output_folder_frame, textvariable=self.output_folder, width=70)
        self.output_folder_entry.grid(row=0, column=0, sticky='ew')
        
        self.browse_output_button = ttk.Button(
            output_folder_frame,
            text="Browse",
            command=self.browse_output_folder
        )
        self.browse_output_button.grid(row=0, column=1, padx=(5,0))

        # Save button
        self.save_button = ttk.Button(
            self,
            text=texts[self.current_language]['save_button'],
            command=self.save_settings
        )
        self.save_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='w')

    def save_settings(self):
        try:
            # Obtener valores actuales
            margin_value = self.side_margin.get().strip()
            spacing_value = self.spacing.get().strip()
            image_folder_value = self.image_folder.get().strip()
            output_folder_value = self.output_folder.get().strip()
            
            # Convertir y validar números
            new_margin = int(margin_value) if margin_value else default_side_margin
            new_spacing = int(spacing_value) if spacing_value else default_spacing
            
            # Validar que los números sean positivos
            if new_margin < 0 or new_spacing < 0:
                raise ValueError("Values must be positive")
            
            # Usar valores por defecto si están vacíos
            new_image_folder = image_folder_value if image_folder_value else default_image_folder
            new_output_folder = output_folder_value if output_folder_value else default_output_folder
            
            # Guardar valores
            set_side_margin(new_margin)
            set_spacing(new_spacing)
            set_image_folder(new_image_folder)
            set_output_folder(new_output_folder)
            
            # Refrescar los inputs con los valores guardados
            self.side_margin.set(str(get_side_margin()))
            self.spacing.set(str(get_spacing()))
            self.image_folder.set(get_image_folder())
            self.output_folder.set(get_output_folder())
            
            messagebox.showinfo("Success", texts[self.current_language]['settings_saved'])
        except ValueError:
            messagebox.showerror("Error", texts[self.current_language]['invalid_number'])

    def update_language(self, new_language):
        self.current_language = new_language
        self.master.tab(self, text=texts[self.current_language]['settings_tab'])
        
        self.margin_label.config(
            text=f"{texts[self.current_language]['side_margin_label']} (default: {default_side_margin})"
        )
        self.spacing_label.config(
            text=f"{texts[self.current_language]['spacing_label']} (default: {default_spacing})"
        )
        self.image_folder_label.config(
            text=texts[self.current_language]['image_folder_label']
        )
        self.output_folder_label.config(
            text=texts[self.current_language]['output_folder_label']
        )
        
        self.save_button.config(text=texts[self.current_language]['save_button'])

    def browse_image_folder(self):
        folder = filedialog.askdirectory(
            title=texts[self.current_language]['select_image_folder'],
            initialdir=self.image_folder.get() or default_image_folder
        )
        if folder:
            self.image_folder.set(folder)

    def browse_output_folder(self):
        folder = filedialog.askdirectory(
            title=texts[self.current_language]['select_output_folder'],
            initialdir=self.output_folder.get() or default_output_folder
        )
        if folder:
            self.output_folder.set(folder)