from tkinter import Frame, Label, StringVar, BooleanVar, messagebox, filedialog, Toplevel
from tkinter import ttk
from translations import translations, get_text
from utils.widgets import create_button
from utils.config_manager import (
    get_side_margin, set_side_margin,
    get_spacing, set_spacing,
    get_image_folder, set_image_folder,
    get_output_folder, set_output_folder,
    get_switch_color, set_switch_color,
    get_switch_color_enabled, set_switch_color_enabled
)
from variables import (
    side_margin as default_side_margin,
    spacing as default_spacing,
    image_folder as default_image_folder,
    output_folder as default_output_folder,
    switch_color as default_switch_color,
    switch_color_enabled as default_switch_color_enabled
)
from tkinter.colorchooser import askcolor
from variables import colors

class SettingsTab(Frame):
    def __init__(self, parent, current_language):
        super().__init__(parent)
        self.current_language = current_language
        self.observers = []  # Lista para los observadores
        
        # Configurar el grid del tab
        self.grid_columnconfigure(0, weight=1)
        
        self.setup_variables()
        self.setup_ui()
        parent.add(self, text=translations[self.current_language]['settings_tab'])

    def setup_variables(self):
        self.side_margin = StringVar(value=str(get_side_margin()))
        self.spacing = StringVar(value=str(get_spacing()))
        self.image_folder = StringVar(value=str(get_image_folder()))
        self.output_folder = StringVar(value=str(get_output_folder()))
        
        # Añadir las variables de color
        self.color_checkbox_var = BooleanVar(value=get_switch_color_enabled())
        self.color_input_var = StringVar(value=get_switch_color())

    def setup_ui(self):
        # Configurar el grid del tab
        self.grid_columnconfigure(0, weight=1)
        
        # Grupo de Espaciado (row=0)
        self.spacing_frame = ttk.LabelFrame(self, text=translations[self.current_language]['spacing_section'])
        self.spacing_frame.grid(row=0, column=0, padx=10, pady=(10,5), sticky='ew')
        self.spacing_frame.grid_columnconfigure(1, weight=1)

        # Margen lateral
        self.side_margin_label = ttk.Label(
            self.spacing_frame, 
            text=f"{translations[self.current_language]['side_margin']} (default: {default_side_margin}{'px'})"
        )
        self.side_margin_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.margin_entry = ttk.Entry(self.spacing_frame, textvariable=self.side_margin, width=10)
        self.margin_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Espaciado
        self.spacing_label = ttk.Label(
            self.spacing_frame, 
            text=f"{translations[self.current_language]['spacing']} (default: {default_spacing}{'px'})"
        )
        self.spacing_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        self.spacing_entry = ttk.Entry(self.spacing_frame, textvariable=self.spacing, width=10)
        self.spacing_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # Grupo de Carpetas (row=1)
        self.folders_frame = ttk.LabelFrame(self, text=translations[self.current_language]['folders_section'])
        self.folders_frame.grid(row=1, column=0, padx=10, pady=5, sticky='ew')
        self.folders_frame.grid_columnconfigure(1, weight=1)

        # Carpeta de imágenes
        self.image_folder_label = ttk.Label(
            self.folders_frame, 
            text=translations[self.current_language]['image_folder_label']
        )
        self.image_folder_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        image_folder_frame = ttk.Frame(self.folders_frame)
        image_folder_frame.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        image_folder_frame.grid_columnconfigure(0, weight=1)
        
        self.image_folder_entry = ttk.Entry(image_folder_frame, textvariable=self.image_folder)
        self.image_folder_entry.grid(row=0, column=0, sticky='ew')
        
        self.browse_image_button = ttk.Button(
            image_folder_frame,
            text="Browse",
            command=self.browse_image_folder
        )
        self.browse_image_button.grid(row=0, column=1, padx=(5,0))

        # Carpeta de salida
        self.output_folder_label = ttk.Label(
            self.folders_frame, 
            text=translations[self.current_language]['output_folder_label']
        )
        self.output_folder_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        output_folder_frame = ttk.Frame(self.folders_frame)
        output_folder_frame.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        output_folder_frame.grid_columnconfigure(0, weight=1)
        
        self.output_folder_entry = ttk.Entry(output_folder_frame, textvariable=self.output_folder)
        self.output_folder_entry.grid(row=0, column=0, sticky='ew')
        
        self.browse_output_button = ttk.Button(
            output_folder_frame,
            text="Browse",
            command=self.browse_output_folder
        )
        self.browse_output_button.grid(row=0, column=1, padx=(5,0))

        # Grupo de Colores (ahora usa dos filas: 2 para el título y 3 para el frame)
        self.create_color_settings()

        # Botón de guardar (ahora en row=4)
        self.save_button = ttk.Button(
            self,
            text=get_text(self.current_language, 'save', 'Save Settings'),
            command=self.save_settings
        )
        self.save_button.grid(row=4, column=0, padx=10, pady=10, sticky='w')

    def save_settings(self):
        try:
            # Obtener valores actuales
            margin_value = self.side_margin.get().strip()
            spacing_value = self.spacing.get().strip()
            image_folder_value = self.image_folder.get().strip()
            output_folder_value = self.output_folder.get().strip()
            
            # Validar y convertir valores numéricos
            margin = int(margin_value)
            spacing = int(spacing_value)
            
            # Guardar valores en la configuración
            set_side_margin(margin)
            set_spacing(spacing)
            set_image_folder(image_folder_value)
            set_output_folder(output_folder_value)
            
            # Guardar configuración de color de Switch
            if hasattr(self, 'color_checkbox_var'):
                set_switch_color_enabled(self.color_checkbox_var.get())
                if self.color_checkbox_var.get():
                    color_value = self.color_input_var.get()
                    if color_value.startswith('#') and len(color_value) == 7:
                        try:
                            int(color_value[1:], 16)
                            set_switch_color(color_value)
                        except ValueError:
                            messagebox.showerror(
                                "Error",
                                translations[self.current_language].get('invalid_color', 'Invalid color code')
                            )
                            return
                    else:
                        messagebox.showerror(
                            "Error",
                            translations[self.current_language].get('invalid_color', 'Invalid color code')
                        )
                        return
            
            # Notificar a los observadores sobre los cambios en las carpetas
            self.notify_folder_change()
            
            messagebox.showinfo(
                "Success",
                translations[self.current_language]['settings_saved']
            )
            
        except ValueError:
            messagebox.showerror(
                "Error",
                translations[self.current_language]['invalid_number']
            )

    def update_language(self, new_language):
        self.current_language = new_language
        self.update_texts()
        self.master.tab(self, text=translations[self.current_language]['settings_tab'])

    def update_texts(self):
        """Actualiza todos los textos según el idioma seleccionado"""
        try:
            # Actualizar textos de las secciones
            if hasattr(self, 'folders_frame'):
                self.folders_frame.config(text=translations[self.current_language]['folders_section'])
            
            if hasattr(self, 'spacing_frame'):
                self.spacing_frame.config(text=translations[self.current_language]['spacing_section'])
            
            # Actualizar labels de carpetas
            if hasattr(self, 'image_folder_label'):
                self.image_folder_label.config(text=translations[self.current_language]['input_folder'])
            
            if hasattr(self, 'output_folder_label'):
                self.output_folder_label.config(text=translations[self.current_language]['output_folder'])
            
            # Actualizar labels de márgenes
            if hasattr(self, 'side_margin_label'):
                self.side_margin_label.config(
                    text=f"{translations[self.current_language]['side_margin']} (default: {default_side_margin}{'px'})"
                )
            
            if hasattr(self, 'spacing_label'):
                self.spacing_label.config(
                    text=f"{translations[self.current_language]['spacing']} (default: {default_spacing}{'px'})"
                )
            
            # Actualizar botón de guardar
            if hasattr(self, 'save_button'):
                self.save_button.config(text=translations[self.current_language]['save'])
            
            # Actualizar textos de la sección de colores
            if hasattr(self, 'color_frame'):
                self.color_frame.config(text=translations[self.current_language]['colors_settings'])
            
            if hasattr(self, 'explanation_label'):
                self.explanation_label.config(text=translations[self.current_language]['colors_settings_tooltip'])
            
            if hasattr(self, 'color_checkbox'):
                self.color_checkbox.config(text=translations[self.current_language]['change_color'])
                
        except Exception as e:
            print(f"Error updating texts: {str(e)}")
            print(f"Current language: {self.current_language}")
            print(f"Widget causing error: {e.__traceback__.tb_frame.f_locals}")

    def browse_image_folder(self):
        folder = filedialog.askdirectory(
            title=translations[self.current_language]['select_image_folder'],
            initialdir=self.image_folder.get() or default_image_folder
        )
        if folder:
            # Reemplazar las barras / por \
            folder = folder.replace('/', '\\')
            self.image_folder.set(folder)

    def browse_output_folder(self):
        folder = filedialog.askdirectory(
            title=translations[self.current_language]['select_output_folder'],
            initialdir=self.output_folder.get() or default_output_folder
        )
        if folder:
            # Reemplazar las barras / por \
            folder = folder.replace('/', '\\')
            self.output_folder.set(folder)

    def create_color_settings(self):
        # Frame para las configuraciones de color
        self.color_frame = ttk.LabelFrame(
            self,
            text=translations[self.current_language]['colors_settings']
        )
        self.color_frame.grid(row=2, column=0, padx=10, pady=5, sticky='ew')
        
        # Label explicativo
        self.explanation_label = ttk.Label(
            self.color_frame,
            text=translations[self.current_language]['colors_settings_tooltip'],
            wraplength=700,
            justify='left',
            foreground='gray'
        )
        self.explanation_label.pack(anchor='w', padx=5, pady=(0,5))
        
        # Frame para el checkbox y su input
        color_checkbox_frame = Frame(self.color_frame)
        color_checkbox_frame.pack(anchor='w', pady=5, fill='x', padx=5)
        
        # Checkbox para cambiar color
        self.color_checkbox = ttk.Checkbutton(
            color_checkbox_frame,
            text=translations[self.current_language]['change_color'] + ': (default ' + default_switch_color + ')',
            variable=self.color_checkbox_var,
            command=self.toggle_color_input
        )
        self.color_checkbox.pack(side='left', padx=(0,10))
        
        # Input para el color
        self.color_input = ttk.Entry(
            color_checkbox_frame,
            width=20,
            textvariable=self.color_input_var
        )
        self.color_input.pack(side='left', padx=(0,5))
        
        # Frame para el botón de color
        self.color_button_frame = Frame(
            color_checkbox_frame,
            borderwidth=1,
            relief='solid'
        )
        self.color_button_frame.pack(side='left')
        
        # Botón que muestra el color
        self.color_button = Label(
            self.color_button_frame,
            width=3,
            height=1,
            bg=self.color_input_var.get(),
            cursor='hand2'
        )
        self.color_button.pack(padx=1, pady=1)
        self.color_button.bind('<Button-1>', lambda e: self.pick_color())
        
        # Configurar el estado inicial del input y botón basado en el checkbox
        if not self.color_checkbox_var.get():
            self.color_input.config(state='disabled')
            self.color_button.unbind('<Button-1>')
            self.color_button.configure(cursor='')
        else:
            self.color_input.config(state='normal')
            self.color_button.bind('<Button-1>', lambda e: self.pick_color())
            self.color_button.configure(cursor='hand2')
        
        # Añadir trace para actualizar el color del botón cuando cambie el input
        self.color_input_var.trace('w', self.validate_hex_color)

    def pick_color(self):
        """Abre el selector de color"""
        if self.color_checkbox_var.get():  # Solo si el checkbox está activo
            color = askcolor(color=self.color_input_var.get(), title="Seleccionar color")
            if color[1]:  # color[1] contiene el valor hexadecimal
                self.color_input_var.set(color[1])

    def validate_hex_color(self, *args):
        """Validar y actualizar el color cuando cambie el input"""
        if not self.color_checkbox_var.get():
            return
        
        color = self.color_input_var.get()
        
        # Verificar si es un color hexadecimal válido
        if color.startswith('#') and len(color) == 7:
            try:
                # Intentar validar el color
                int(color[1:], 16)
                # Si es válido, actualizar el color del botón
                self.color_button.configure(bg=color)
            except ValueError:
                pass
        # Si el color empieza sin #, intentar añadirlo
        elif len(color) == 6:
            try:
                int(color, 16)
                self.color_button.configure(bg=f'#{color}')
                # Actualizar el input con el # (sin trigger el trace de nuevo)
                self.color_input_var.set(f'#{color}')
            except ValueError:
                pass

    def toggle_color_input(self):
        """Habilita o deshabilita el input de color y el botón según el estado del checkbox"""
        if self.color_checkbox_var.get():
            self.color_input.config(state='normal')
            self.color_button.bind('<Button-1>', lambda e: self.pick_color())
            self.color_button.configure(cursor='hand2')
        else:
            self.color_input.config(state='disabled')
            self.color_button.unbind('<Button-1>')
            self.color_button.configure(cursor='')

    def create_margin_settings(self):
        # Frame para las configuraciones de espaciado
        self.spacing_frame = ttk.LabelFrame(
            self,
            text=translations[self.current_language]['spacing_section']
        )
        self.spacing_frame.grid(row=1, column=0, padx=10, pady=5, sticky='ew')
        
        # Side Margin
        self.side_margin_label = ttk.Label(
            self.spacing_frame,
            text=translations[self.current_language]['side_margin']
        )
        self.side_margin_label.grid(row=0, column=0, padx=5, pady=5)
        
        # Spacing
        self.spacing_label = ttk.Label(
            self.spacing_frame,
            text=translations[self.current_language]['spacing']
        )
        self.spacing_label.grid(row=1, column=0, padx=5, pady=5)

    def add_observer(self, observer):
        """Añade un observador para notificar cambios en las carpetas"""
        self.observers.append(observer)

    def notify_folder_change(self):
        """Notifica a los observadores sobre cambios en las carpetas"""
        for observer in self.observers:
            if hasattr(observer, 'update_folders'):
                observer.update_folders(
                    self.image_folder.get(),
                    self.output_folder.get()
                )