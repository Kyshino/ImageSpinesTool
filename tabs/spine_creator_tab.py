from tkinter import Frame, Label, StringVar, BooleanVar, messagebox, filedialog
from tkinter import ttk
from tkinter.colorchooser import askcolor
from translations import translations, get_text
from variables import TEMPLATES
from spines_creators.switch_spine_creator import SpineCreator
from utils.config_manager import (get_output_folder)

class SpineCreatorTab(Frame):
    def __init__(self, parent, current_language):
        super().__init__(parent)
        self.current_language = current_language
        
        # Configurar el grid del tab
        self.grid_columnconfigure(0, weight=1)
        
        self.setup_variables()
        self.setup_ui()
        parent.add(self, text=translations[self.current_language]['spine_creator_tab'])

    def setup_variables(self):
        # Variables para los selects
        self.platform = StringVar(value="Switch")
        self.pattern = StringVar(value="Vertical")
        self.output_path = StringVar(value=str(get_output_folder()))
        self.text = StringVar()
        self.font_size = StringVar(value="80        ")
        self.text_position = StringVar(value="Middle")
        
        # Variables para los colores
        self.color1_var = StringVar(value="#282828")
        self.color2_var = StringVar(value="#1E1E1E")
        
        # Variable para la fuente
        self.font_path = StringVar()
        
        # Cambiar el nombre de la variable y el valor por defecto
        self.logo_type = StringVar(value="Nintendo")

    def setup_ui(self):
        # Frame principal (cambiado de LabelFrame a Frame normal)
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, padx=10, pady=5, sticky='nsew')
        main_frame.grid_columnconfigure(1, weight=1)

        # Platform
        self.platform_label = ttk.Label(main_frame, text=translations[self.current_language]['platform'])
        self.platform_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        platform_select = ttk.Combobox(main_frame, textvariable=self.platform, state='readonly', width=35)
        platform_select['values'] = ('Switch')
        platform_select.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Pattern
        self.pattern_label = ttk.Label(main_frame, text=translations[self.current_language]['pattern_type'])
        self.pattern_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        pattern_select = ttk.Combobox(main_frame, textvariable=self.pattern, state='readonly', width=35)
        pattern_values = ('vertical', 'diagonal', 'dotted', 'plain')
        pattern_select['values'] = [value.capitalize() for value in pattern_values]
        pattern_select.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        pattern_select.bind('<<ComboboxSelected>>', self.on_pattern_change)

        # Output Path
        self.output_label = ttk.Label(main_frame, text=translations[self.current_language]['output_path'])
        self.output_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        output_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Entry(output_frame, textvariable=self.output_path).grid(row=0, column=0, sticky='ew')
        ttk.Button(output_frame, text="Browse", command=self.browse_output).grid(row=0, column=1, padx=(5,0))

        # Frame para los colores
        self.color1_label = ttk.Label(main_frame, text=translations[self.current_language]['color_1'])
        self.color1_label.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        colors_frame = ttk.Frame(main_frame)
        colors_frame.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        # Color 1 y 2 (modificado para guardar referencias)
        self.color1_entry = ttk.Entry(colors_frame, textvariable=self.color1_var, width=10)
        self.color1_entry.pack(side='left', padx=(0,5))
        self.color1_button, self.color1_frame = self.create_color_button(colors_frame, self.color1_var)
        
        self.color2_label = ttk.Label(colors_frame, text=translations[self.current_language]['color_2'])
        self.color2_label.pack(side='left', padx=(15,5))
        self.color2_entry = ttk.Entry(colors_frame, textvariable=self.color2_var, width=10)
        self.color2_entry.pack(side='left', padx=(0,5))
        self.color2_button, self.color2_frame = self.create_color_button(colors_frame, self.color2_var)

        # Text
        self.text_label = ttk.Label(main_frame, text=translations[self.current_language]['text'])
        self.text_label.grid(row=5, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(main_frame, textvariable=self.text, width=35).grid(row=5, column=1, padx=5, pady=5, sticky='w')

        # Font Path
        self.font_path_label = ttk.Label(main_frame, text=translations[self.current_language]['font_path'])
        self.font_path_label.grid(row=6, column=0, padx=5, pady=5, sticky='w')
        
        # Frame para el input de fuente y el botón browse
        font_frame = ttk.Frame(main_frame)
        font_frame.grid(row=6, column=1, padx=5, pady=5, sticky='ew')
        font_frame.grid_columnconfigure(0, weight=1)

        # Entry para la ruta de la fuente
        ttk.Entry(font_frame, textvariable=self.font_path, width=30).grid(row=0, column=0, sticky='ew')
        ttk.Button(font_frame, text="Browse", command=self.browse_font).grid(row=0, column=1, padx=(5,0))

        # Texto explicativo
        self.font_path_tooltip_label = ttk.Label(
            main_frame, 
            text=translations[self.current_language]['font_path_tooltip'],
            wraplength=400,
            foreground='gray'
        )
        self.font_path_tooltip_label.grid(row=7, column=0, columnspan=2, padx=5, pady=(0,5), sticky='w')

        # Font Size
        self.font_size_label = ttk.Label(main_frame, text=translations[self.current_language]['font_size'])
        self.font_size_label.grid(row=8, column=0, padx=5, pady=5, sticky='w')
        font_sizes = [str(i) for i in range(50, 121, 1)]
        font_select = ttk.Combobox(main_frame, textvariable=self.font_size, values=font_sizes, state='readonly', width=35)
        font_select.grid(row=8, column=1, padx=5, pady=5, sticky='w')

        # Text Position
        self.text_position_label = ttk.Label(main_frame, text=translations[self.current_language]['text_position'])
        self.text_position_label.grid(row=9, column=0, padx=5, pady=5, sticky='w')
        position_select = ttk.Combobox(main_frame, textvariable=self.text_position, state='readonly', width=35)
        position_values = ('top', 'middle', 'bottom')
        position_select['values'] = [value.capitalize() for value in position_values]
        position_select.grid(row=9, column=1, padx=5, pady=5, sticky='w')

        # Logo
        self.logo_label = ttk.Label(main_frame, text=translations[self.current_language]['logo_type'])
        self.logo_label.grid(row=10, column=0, padx=5, pady=5, sticky='w')
        
        logo_select = ttk.Combobox(main_frame, textvariable=self.logo_type, state='readonly', width=35)
        logo_values = ('Without Logo', 'Nintendo', 'Sega', 'Microids', 'NIS', 'ATLUS', 'Devolver', 'Limited Run')
        logo_select['values'] = logo_values
        logo_select.grid(row=10, column=1, padx=5, pady=5, sticky='w')

        # Frame para el botón de guardar y el mensaje de estado
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.grid(row=11, column=0, columnspan=2, padx=5, pady=10, sticky='w')

        # Botón de guardar con nuevo texto
        self.generate_button = ttk.Button(
            self.status_frame,
            text=translations[self.current_language]['generate_spine'],
            command=self.save_settings
        )
        self.generate_button.pack(side='left', padx=5)

        # Label para el mensaje de estado (inicialmente vacío)
        self.status_label = ttk.Label(
            self.status_frame,
            text="",
            foreground='green'
        )
        self.status_label.pack(side='left', padx=5)

    def create_color_button(self, parent, color_var):
        button_frame = Frame(parent, borderwidth=1, relief='solid')
        button_frame.pack(side='left')
        
        color_button = Label(
            button_frame,
            width=3,
            height=1,
            bg=color_var.get(),
            cursor='hand2'
        )
        color_button.pack(padx=1, pady=1)
        
        def pick_color(event=None):
            color = askcolor(color=color_var.get(), title="Seleccionar color")
            if color[1]:
                color_var.set(color[1])
                color_button.configure(bg=color[1])
        
        color_button.bind('<Button-1>', pick_color)
        color_var.trace('w', lambda *args: color_button.configure(bg=color_var.get()))
        
        # Guardamos la función pick_color junto con el botón
        color_button.pick_color = pick_color
        
        return color_button, button_frame

    def browse_output(self):
        folder = filedialog.askdirectory(
            title="Seleccionar carpeta de salida",
            initialdir=self.output_path.get()
        )
        if folder:
            folder = folder.replace('/', '\\')
            self.output_path.set(folder)

    def browse_font(self):
        """Método para buscar archivo de fuente TTF"""
        filetypes = (
            ('TrueType Font', '*.ttf'),
            ('All files', '*.*')
        )
        
        filename = filedialog.askopenfilename(
            title=translations[self.current_language].get('select_font', 'Select Font'),
            filetypes=filetypes,
            initialdir="/"
        )
        
        if filename:
            self.font_path.set(filename)

    def show_temporary_message(self, message, duration=3000):
        """Muestra un mensaje temporal y lo elimina después de la duración especificada"""
        self.status_label.configure(text=translations[self.current_language]['spine_created'])
        self.after(duration, lambda: self.status_label.configure(text=""))

    def save_settings(self):
        settings = {
            'platform': self.platform.get(),
            'pattern': self.pattern.get().lower(),
            'output_path': self.output_path.get(),
            'color1': self.color1_var.get(),
            'color2': self.color2_var.get(),
            'text': self.text.get(),
            'font_path': self.font_path.get() or None,
            'font_size': self.font_size.get(),
            'text_position': self.text_position.get().lower(),
            'logo_type': self.logo_type.get()
        }
        
        try:
            creator = SpineCreator()
            input_path = TEMPLATES[settings['platform'].lower()]
            
            creator.process_image(
                input_path=input_path,
                output_path=settings['output_path'],
                hex_colors=[settings['color1'], settings['color2']],
                pattern_type=settings['pattern'],
                text=settings['text'],
                font_path=settings['font_path'],
                font_size=int(settings['font_size']),
                text_position=settings['text_position'],
                logo_type=settings['logo_type']
            )
            
            self.show_temporary_message(translations[self.current_language]['spine_created'])
        except Exception as e:
            self.status_label.configure(
                text=translations[self.current_language]['spine_error'] + str(e), 
                foreground='red'
            )

    def update_language(self, new_language):
        self.current_language = new_language
        
        # Actualizar todos los textos de los labels
        self.platform_label.config(text=translations[self.current_language]['platform'])
        self.pattern_label.config(text=translations[self.current_language]['pattern_type'])
        self.output_label.config(text=translations[self.current_language]['output_path'])
        self.color1_label.config(text=translations[self.current_language]['color_1'])
        self.color2_label.config(text=translations[self.current_language]['color_2'])
        self.text_label.config(text=translations[self.current_language]['text'])
        self.font_path_label.config(text=translations[self.current_language]['font_path'])
        self.font_path_tooltip_label.config(text=translations[self.current_language]['font_path_tooltip'])
        self.font_size_label.config(text=translations[self.current_language]['font_size'])
        self.text_position_label.config(text=translations[self.current_language]['text_position'])
        self.logo_label.config(text=translations[self.current_language]['logo_type'])
        self.generate_button.config(text=translations[self.current_language]['generate_spine'])

    def on_pattern_change(self, event):
        """Maneja el cambio en el patrón seleccionado"""
        pattern = self.pattern.get().lower()
        if pattern == 'plain':
            # Deshabilitar color 2
            self.color2_entry.config(state='disabled')
            self.color2_button.unbind('<Button-1>')
            self.color2_button.configure(cursor='')
            # Oscurecer el botón para indicar que está deshabilitado
            self.color2_button.configure(bg='gray')
        else:
            # Habilitar color 2
            self.color2_entry.config(state='normal')
            self.color2_button.bind('<Button-1>', self.color2_button.pick_color)
            self.color2_button.configure(cursor='hand2')
            # Restaurar el color original
            self.color2_button.configure(bg=self.color2_var.get())