from tkinter import Frame, Label, StringVar, BooleanVar, Checkbutton, messagebox
from tkinter import ttk
import os
import subprocess
import threading
from PIL import Image
from components.tooltip import ToolTip
from translations.texts import texts
from variables import sizes, paper_horizontal_sizes, side_margin
from utils.widgets import (
    create_label_and_entry,
    create_label_and_combobox,
    create_button,
    create_progress_elements,
    update_label_text
)
from utils.config_manager import get_side_margin

class ProcessingTab(Frame):
    def __init__(self, parent, current_language):
        super().__init__(parent)
        self.current_language = current_language
        self.processing_thread = None
        self.processing_cancelled = False
        
        # Configurar el grid del tab
        self.grid_columnconfigure(0, weight=1)
        
        # Variables
        self.selected_size = StringVar(value=list(sizes.keys())[0])
        self.selected_paper_type = StringVar(value=list(paper_horizontal_sizes.keys())[0])
        self.images_folder = StringVar(value=r"C:\Users\Spines\Desktop\SpinesImages")
        self.output_folder = StringVar(value=r"C:\Users\Spines\Desktop\SpinesImages\Output")
        self.open_output = BooleanVar(value=False)
        
        self.setup_ui()
        parent.add(self, text=texts[self.current_language]['image_processing_tab'])

    def setup_ui(self):
        self.create_folder_inputs()
        self.create_size_selectors()
        self.create_buttons()
        self.create_progress_elements()
        self.update_tooltips()

    def create_folder_inputs(self):
        self.label_image_folder, self.entry_image_folder = create_label_and_entry(
            self,
            texts[self.current_language]['image_folder_label'], 
            self.images_folder, 
            1
        )
        self.label_output_folder, self.entry_output_folder = create_label_and_entry(
            self,
            texts[self.current_language]['output_folder_label'], 
            self.output_folder, 
            2
        )

    def create_size_selectors(self):
        self.label_select_size, self.size_combobox = create_label_and_combobox(
            self,
            texts[self.current_language]['select_size_label'],
            self.selected_size,
            3,
            list(sizes.keys()),
            20
        )
        self.label_select_paper, self.paper_combobox = create_label_and_combobox(
            self,
            texts[self.current_language]['select_paper_size_label'],
            self.selected_paper_type,
            4,
            list(paper_horizontal_sizes.keys()),
            10
        )

    def create_buttons(self):
        self.checkbutton = Checkbutton(
            self, 
            text=texts[self.current_language]['open_output_check'], 
            variable=self.open_output
        )
        self.checkbutton.grid(row=5, column=0, padx=10, pady=5, sticky='w')

        self.process_button = create_button(
            self,
            texts[self.current_language]['process_button'],
            self.run_processing,
            6
        )

        self.cancel_button = create_button(
            self,
            texts[self.current_language]['cancel_button'],
            self.cancel_processing,
            6,
            padx=120,
            state='disabled'
        )

    def create_progress_elements(self):
        self.progress_label = Label(self, text=texts[self.current_language]['processing'])
        self.progress_bar = ttk.Progressbar(self, length=400, mode='determinate')
        # No agregamos los elementos al grid aquí, los mantenemos ocultos inicialmente

    def process_images(self, images_folder_path, output_folder_path, new_image_size, selected_size_name, paper_type):
        os.makedirs(output_folder_path, exist_ok=True)
        spacing = 2
        image_files = [f for f in os.listdir(images_folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        canvas_count = 1
        x_offset = get_side_margin()
        canvas = Image.new("RGBA", paper_horizontal_sizes[paper_type], (255, 255, 255, 255))

        total_images = len(image_files)

        for index, image_file in enumerate(image_files):
            if self.processing_cancelled:
                break

            try:
                img_path = os.path.join(images_folder_path, image_file)
                img = Image.open(img_path).convert("RGBA")
                image_name = os.path.basename(img_path)
                img_resized = img.resize(new_image_size, Image.LANCZOS)
                update_label_text(self.progress_label, texts[self.current_language]['processing'] + " " + image_name)

                if x_offset + new_image_size[0] > paper_horizontal_sizes[paper_type][0] - get_side_margin():
                    canva_name = f"{selected_size_name.replace(' ', '_').lower()}_{paper_type.replace(' ', '_').lower()}_output_{canvas_count}.png"
                    update_label_text(self.progress_label, texts[self.current_language]['creating'] + " " + canva_name)
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
        # Mostramos los elementos de progreso solo cuando comienza el procesamiento
        self.progress_label.grid(row=7, column=0, padx=10, pady=(5, 0), sticky='w')
        self.progress_bar.grid(row=8, column=0, padx=10, pady=(0, 5), sticky='ew')

        self.processing_thread = threading.Thread(target=self.process_images_thread)
        self.processing_thread.start()

    def process_images_thread(self):
        images_folder_path = self.images_folder.get()
        output_folder_path = self.output_folder.get()
        selected_size_name = self.selected_size.get()
        new_image_size = sizes[selected_size_name]
        paper_type = self.selected_paper_type.get()

        if not os.path.exists(images_folder_path):
            messagebox.showerror("Error", texts[self.current_language]['error_image_folder'])
            self.process_button.config(state='normal')
            self.cancel_button.config(state='disabled')
            self.hide_progress_elements()
            return

        if not os.path.exists(output_folder_path):
            messagebox.showerror("Error", texts[self.current_language]['error_output_folder'])
            self.process_button.config(state='normal')
            self.cancel_button.config(state='disabled')
            self.hide_progress_elements()
            return

        self.process_images(images_folder_path, output_folder_path, new_image_size, selected_size_name, paper_type)

        if self.processing_cancelled:
            update_label_text(self.progress_label, texts[self.current_language]['cancelled_message'])
        else:
            if self.open_output.get():
                subprocess.Popen(f'explorer "{output_folder_path}"')
            update_label_text(self.progress_label, texts[self.current_language]['success_message'])

        self.process_button.config(state='normal')
        self.cancel_button.config(state='disabled')
        self.after(5000, self.hide_progress_elements)

    def hide_progress_elements(self):
        self.progress_label.grid_forget()
        self.progress_bar.grid_forget()

    def cancel_processing(self):
        self.processing_cancelled = True
        self.progress_bar.configure(style='red.Horizontal.TProgressbar')
        update_label_text(self.progress_label, texts[self.current_language]['cancelled_message'])

    def update_language(self, new_language):
        self.current_language = new_language
        self.update_texts()
        self.update_tooltips()
        self.master.tab(self, text=texts[self.current_language]['image_processing_tab'])

    def update_tooltips(self):
        ToolTip(self.entry_image_folder, texts[self.current_language]['image_folder_tooltip'] + texts[self.current_language]['available_extensions'])
        ToolTip(self.entry_output_folder, texts[self.current_language]['output_folder_tooltip'])

    def update_texts(self):
        self.label_image_folder.config(text=texts[self.current_language]['image_folder_label'])
        self.label_output_folder.config(text=texts[self.current_language]['output_folder_label'])
        self.label_select_size.config(text=texts[self.current_language]['select_size_label'])
        self.label_select_paper.config(text=texts[self.current_language]['select_paper_size_label'])
        
        self.process_button.config(text=texts[self.current_language]['process_button'])
        self.cancel_button.config(text=texts[self.current_language]['cancel_button'])
        self.checkbutton.config(text=texts[self.current_language]['open_output_check'])
        
        self.size_combobox['values'] = list(sizes.keys())
        self.size_combobox.set(self.selected_size.get())
        self.paper_combobox['values'] = list(paper_horizontal_sizes.keys())
        self.paper_combobox.set(self.selected_paper_type.get())