from tkinter import Frame, Label, StringVar, BooleanVar, Checkbutton, messagebox, IntVar, Toplevel
from tkinter import ttk
import os
import subprocess
import threading
from PIL import Image
from components.tooltip import ToolTip
from translations import translations, get_text
from variables import sizes, paper_horizontal_sizes
from utils.widgets import (
    update_label_text
)
from utils.config_manager import (
    get_image_folder,
    get_output_folder,
    get_spacing,
    get_side_margin,
    get_switch_color_enabled,
    get_switch_color
)
from utils.colors_utils import (hex_to_rgba)

class ProcessingTab(Frame):
    def __init__(self, parent, current_language):
        super().__init__(parent)
        self.current_language = current_language
        self.processing_thread = None
        self.processing_cancelled = False
        
        # Configurar solo una columna principal
        self.grid_columnconfigure(1, weight=1)
        
        # Variables
        self.selected_size = StringVar(value=list(sizes.keys())[0])
        self.selected_paper_type = StringVar(value=list(paper_horizontal_sizes.keys())[0])
        self.images_folder = StringVar(value=get_image_folder())
        self.output_folder = StringVar(value=get_output_folder())
        self.open_output = BooleanVar(value=False)
        
        self.setup_variables()
        self.setup_ui()
        parent.add(self, text=translations[self.current_language]['image_processing_tab'])

    def setup_variables(self):
        # Inicializar con los valores de la configuración
        self.input_path = StringVar(value=get_image_folder())
        self.output_path = StringVar(value=get_output_folder())
        self.status = StringVar(value='')
        self.progress = IntVar(value=0)

    def setup_ui(self):
        self.create_folder_inputs()
        self.create_size_selectors()
        self.create_buttons()
        
        # Crear un frame contenedor para los elementos de progreso
        self.progress_frame = Frame(self)
        self.progress_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky='ew')
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        # Pre-crear los elementos de progreso pero mantenerlos ocultos
        self.progress_label = Label(self.progress_frame, text="")
        self.progress_label.grid(row=0, column=0, sticky='w')
        self.progress_label.grid_remove()  # Ocultar pero mantener el espacio
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, length=400, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky='ew')
        self.progress_bar.grid_remove()  # Ocultar pero mantener el espacio
        
        self.update_tooltips()

    def create_folder_inputs(self):
        # Alinear todo a la izquierda
        self.label_image_folder = Label(self, text=translations[self.current_language]['image_folder_label'])
        self.label_image_folder.grid(row=1, column=0, padx=(10,5), pady=5, sticky='w')
        
        self.entry_image_folder = ttk.Entry(self, textvariable=self.images_folder)
        self.entry_image_folder.grid(row=1, column=1, padx=(0,10), pady=5, sticky='ew')
        
        self.label_output_folder = Label(self, text=translations[self.current_language]['output_folder_label'])
        self.label_output_folder.grid(row=2, column=0, padx=(10,5), pady=5, sticky='w')
        
        self.entry_output_folder = ttk.Entry(self, textvariable=self.output_folder)
        self.entry_output_folder.grid(row=2, column=1, padx=(0,10), pady=5, sticky='ew')

    def create_size_selectors(self):
        self.label_select_size = Label(self, text=translations[self.current_language]['select_size_label'])
        self.label_select_size.grid(row=3, column=0, padx=(10,5), pady=5, sticky='w')
        
        self.size_combobox = ttk.Combobox(
            self,
            textvariable=self.selected_size,
            values=list(sizes.keys()),
            state='readonly',
            width=25
        )
        self.size_combobox.grid(row=3, column=1, padx=(0,10), pady=5, sticky='w')
        
        self.label_select_paper = Label(self, text=translations[self.current_language]['select_paper_size_label'])
        self.label_select_paper.grid(row=4, column=0, padx=(10,5), pady=5, sticky='w')
        
        self.paper_combobox = ttk.Combobox(
            self,
            textvariable=self.selected_paper_type,
            values=list(paper_horizontal_sizes.keys()),
            state='readonly',
            width=25
        )
        self.paper_combobox.grid(row=4, column=1, padx=(0,10), pady=5, sticky='w')

    def create_buttons(self):
        # Frame contenedor para los checkboxes y botones
        self.controls_frame = Frame(self)
        self.controls_frame.grid(row=5, column=0, columnspan=2, sticky='ew', padx=10)
        
        # Checkbox para abrir carpeta
        self.checkbutton = ttk.Checkbutton(
            self.controls_frame,
            text=translations[self.current_language]['open_output_check'],
            variable=self.open_output
        )
        self.checkbutton.pack(anchor='w', pady=2)
        
        # Frame para los botones
        self.button_frame = Frame(self.controls_frame)
        self.button_frame.pack(anchor='w', pady=(2,5))
        
        self.process_button = ttk.Button(
            self.button_frame,
            text=translations[self.current_language]['process_button'],
            command=self.run_processing
        )
        self.process_button.pack(side='left', padx=(0,5))
        
        self.cancel_button = ttk.Button(
            self.button_frame,
            text=translations[self.current_language]['cancel_button'],
            command=self.cancel_processing,
            state='disabled'
        )
        self.cancel_button.pack(side='left')

    def get_switch_height(self):
        switch_heights = {
            "Switch PET": 335,
            "Switch without PET": 317
        }
        valor_seleccionado = self.selected_size.get()
        return switch_heights.get(valor_seleccionado, 0)

    def process_images(self, images_folder_path, output_folder_path, new_image_size, selected_size_name, paper_type):
        os.makedirs(output_folder_path, exist_ok=True)
        spacing = get_spacing()
        image_files = [f for f in os.listdir(images_folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        canvas_count = 1
        x_offset = get_side_margin()
        canvas = Image.new("RGBA", paper_horizontal_sizes[paper_type], (255, 255, 255, 255))

        total_images = len(image_files)

        # Verificar si es un tamaño de Switch y si el color personalizado está habilitado
        is_switch_size = 'switch' in selected_size_name.lower()
        switch_color_enabled = get_switch_color_enabled()

        for index, image_file in enumerate(image_files):
            if self.processing_cancelled:
                break

            try:
                img_path = os.path.join(images_folder_path, image_file)
                img = Image.open(img_path).convert("RGBA")
                image_name = os.path.basename(img_path)
                img_resized = img.resize(new_image_size, Image.LANCZOS)

                if is_switch_size and switch_color_enabled:
                    img_resized = self.apply_color_to_header(img_resized, get_switch_color(), self.get_switch_height())

                update_label_text(self.progress_label, translations[self.current_language]['processing'] + " " + image_name)

                if x_offset + new_image_size[0] > paper_horizontal_sizes[paper_type][0] - get_side_margin():
                    canva_name = f"{selected_size_name.replace(' ', '_').lower()}_{paper_type.replace(' ', '_').lower()}_output_{canvas_count}.png"
                    update_label_text(self.progress_label, translations[self.current_language]['creating'] + " " + canva_name)
                    canvas.save(os.path.join(output_folder_path, canva_name), format="PNG", dpi=(300, 300))
                    canvas_count += 1
                    canvas = Image.new("RGBA", paper_horizontal_sizes[paper_type], (255, 255, 255, 255))
                    x_offset = get_side_margin()

                y_position = (paper_horizontal_sizes[paper_type][1] - new_image_size[1]) // 2
                canvas.paste(img_resized, (x_offset, y_position), img_resized)
                x_offset += new_image_size[0] + spacing

                self.progress_bar['value'] = (index + 1) / total_images * 100
                self.update_idletasks()

            except Exception as e:
                print(f"Error al procesar la imagen {image_file}: {e}")

        if x_offset > get_side_margin() and not self.processing_cancelled:
            canva_name = f"{selected_size_name.replace(' ', '_').lower()}_{paper_type.replace(' ', '_').lower()}_output_{canvas_count}.png"
            canvas.save(os.path.join(output_folder_path, canva_name), format="PNG", dpi=(300, 300))

    def run_processing(self):
        self.processing_cancelled = False
        self.process_button.config(state='disabled')
        self.cancel_button.config(state='normal')
        
        # Mostrar los elementos de progreso
        self.progress_label.grid()  # Mostrar label
        self.progress_bar.grid()    # Mostrar barra
        
        self.processing_thread = threading.Thread(target=self.process_images_thread)
        self.processing_thread.start()

    def process_images_thread(self):
        images_folder_path = self.images_folder.get()
        output_folder_path = self.output_folder.get()
        selected_size_name = self.selected_size.get()
        new_image_size = sizes[selected_size_name]
        paper_type = self.selected_paper_type.get()

        if not os.path.exists(images_folder_path):
            messagebox.showerror("Error", translations[self.current_language]['error_image_folder'])
            self.process_button.config(state='normal')
            self.cancel_button.config(state='disabled')
            self.hide_progress_elements()
            return

        if not os.path.exists(output_folder_path):
            messagebox.showerror("Error", translations[self.current_language]['error_output_folder'])
            self.process_button.config(state='normal')
            self.cancel_button.config(state='disabled')
            self.hide_progress_elements()
            return

        self.process_images(images_folder_path, output_folder_path, new_image_size, selected_size_name, paper_type)

        if self.processing_cancelled:
            update_label_text(self.progress_label, translations[self.current_language]['cancelled_message'])
        else:
            if self.open_output.get():
                subprocess.Popen(f'explorer "{output_folder_path}"')
            update_label_text(self.progress_label, translations[self.current_language]['success_message'])

        self.process_button.config(state='normal')
        self.cancel_button.config(state='disabled')
        self.after(5000, self.hide_progress_elements)

    def hide_progress_elements(self):
        self.progress_label.grid_remove()  # Ocultar pero mantener espacio
        self.progress_bar.grid_remove()    # Ocultar pero mantener espacio

    def cancel_processing(self):
        self.processing_cancelled = True
        self.progress_bar.configure(style='red.Horizontal.TProgressbar')
        update_label_text(self.progress_label, translations[self.current_language]['cancelled_message'])

    def update_language(self, new_language):
        self.current_language = new_language
        self.update_texts()
        self.update_tooltips()
        self.master.tab(self, text=translations[self.current_language]['image_processing_tab'])

    def update_tooltips(self):
        ToolTip(self.entry_image_folder, translations[self.current_language]['image_folder_tooltip'] + translations[self.current_language]['available_extensions'])
        ToolTip(self.entry_output_folder, translations[self.current_language]['output_folder_tooltip'])

    def update_texts(self):
        self.label_image_folder.config(text=translations[self.current_language]['image_folder_label'])
        self.label_output_folder.config(text=translations[self.current_language]['output_folder_label'])
        self.label_select_size.config(text=translations[self.current_language]['select_size_label'])
        self.label_select_paper.config(text=translations[self.current_language]['select_paper_size_label'])
        
        self.process_button.config(text=translations[self.current_language]['process_button'])
        self.cancel_button.config(text=translations[self.current_language]['cancel_button'])
        self.checkbutton.config(text=translations[self.current_language]['open_output_check'])
        
        self.size_combobox['values'] = list(sizes.keys())
        self.size_combobox.set(self.selected_size.get())
        self.paper_combobox['values'] = list(paper_horizontal_sizes.keys())
        self.paper_combobox.set(self.selected_paper_type.get())

    def refresh_paths(self):
        """Actualiza los paths con los valores actuales de la configuración"""
        self.images_folder.set(get_image_folder())
        self.output_folder.set(get_output_folder())

    def check_switch_option(self):
        selected = self.selected_size.get().lower()
        if 'switch' in selected:
            self.checkbutton.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky='w')
            self.button_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky='w')
        else:
            self.checkbutton.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky='w')
            self.button_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky='w')

    def update_folders(self, image_folder, output_folder):
        """Actualiza las carpetas cuando cambian en la pestaña de configuración"""
        if hasattr(self, 'images_folder'):
            self.images_folder.set(image_folder)
        
        if hasattr(self, 'output_folder'):
            self.output_folder.set(output_folder)


    def apply_color_to_header(self, img, hex_color, check_height):
        width = img.size[0]
        
        TARGET_COLOR = hex_to_rgba(hex_color)
        
        new_img = img.copy()
        pixels = new_img.load()
        
        for y in range(check_height):
            for x in range(width):
                pixel = pixels[x, y]

                if (pixel[0] > 150 and
                    pixel[0] > pixel[1] * 2 and
                    pixel[0] > pixel[2] * 2):
                    pixels[x, y] = TARGET_COLOR
        
        return new_img