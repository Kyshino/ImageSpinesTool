from tkinter import Tk, Label, Entry, Button, StringVar, messagebox, Checkbutton, BooleanVar, Frame
from tkinter import ttk
from PIL import Image
import os
import subprocess
import threading
from translations.texts import texts
from components.tooltip import ToolTip
from variables import language_map, sizes, paper_horizontal_sizes, side_margin

root = Tk()
current_language = 'en'
root.title('Image Spines Tool v0.2')

# Centra la ventana en la pantalla
window_width = 600
window_height = 300  # Aumenta la altura para el ProgressBar
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x}+{int(y)}")


# Variables para las selecciones
selected_size = StringVar(value=list(sizes.keys())[0])  # Por defecto, primer tamaño
selected_paper_type = StringVar(value=list(paper_horizontal_sizes.keys())[0])  # Por defecto, primer tipo de papel

# Variables para las rutas
images_folder = StringVar(value=r"C:\Users\KyshinoDesktop\Downloads\Spines")
output_folder = StringVar(value=r"C:\Users\KyshinoDesktop\Downloads\Spines\Output")

# Variable para controlar el hilo de procesamiento
processing_thread = None
processing_cancelled = False

# Crea un frame con etiqueta y campo de entrada
def create_label_and_entry(parent, label_text, var, row, width=50):
    frame = Frame(parent)
    frame.grid(row=row, column=0, padx=10, pady=5, sticky='w')
    label = Label(frame, text=label_text)
    label.pack(side='left', padx=(0, 10))
    entry = Entry(frame, textvariable=var, width=width)
    entry.pack(side='right')
    return label, entry

# Crea un frame con etiqueta y Combobox
def create_label_and_combobox(parent, label_text, var, row, options, width=50):
    frame = Frame(parent)
    frame.grid(row=row, column=0, padx=10, pady=5, sticky='w')
    label = Label(frame, text=label_text)
    label.pack(side='left', padx=(0, 10))
    combobox = ttk.Combobox(frame, textvariable=var, values=options, state='readonly', width=width)
    combobox.pack(side='right')
    return label, combobox

# Procesa las imágenes y las guarda en una carpeta de salida
def process_images(images_folder_path, output_folder_path, new_image_size, selected_size_name, paper_type):
    global processing_cancelled
    os.makedirs(output_folder_path, exist_ok=True)
    spacing = 2
    image_files = [f for f in os.listdir(images_folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    canvas_count = 1
    x_offset = side_margin
    canvas = Image.new("RGBA", paper_horizontal_sizes[paper_type], (255, 255, 255, 255))

    total_images = len(image_files)

    for index, image_file in enumerate(image_files):
        if processing_cancelled:
            break  # Salir del bucle si se ha cancelado el proceso

        try:
            img_path = os.path.join(images_folder_path, image_file)
            img = Image.open(img_path).convert("RGBA")
            image_name = os.path.basename(img_path)
            img_resized = img.resize(new_image_size, Image.LANCZOS)
            update_label_text(progress_label, texts[current_language]['processing'] + " " + image_name)

            if x_offset + new_image_size[0] > paper_horizontal_sizes[paper_type][0] - side_margin:
                canva_name = f"{selected_size_name.replace(' ', '_').lower()}_{paper_type.replace(' ', '_').lower()}_output_{canvas_count}.png"
                update_label_text(progress_label, texts[current_language]['creating'] + " " + canva_name)
                canvas.save(os.path.join(output_folder_path, canva_name), format="PNG", dpi=(300, 300))
                canvas_count += 1
                canvas = Image.new("RGBA", paper_horizontal_sizes[paper_type], (255, 255, 255, 255))
                x_offset = side_margin

            y_position = (paper_horizontal_sizes[paper_type][1] - new_image_size[1]) // 2
            canvas.paste(img_resized, (x_offset, y_position), img_resized)
            x_offset += new_image_size[0] + spacing

            # Actualizar el ProgressBar
            progress_bar['value'] = (index + 1) / total_images * 100
            root.update_idletasks()  # Actualiza la interfaz

        except Exception as e:
            print(f"Error al procesar la imagen {image_file}: {e}")

    if x_offset > side_margin and not processing_cancelled:
        # Si no se canceló, guarda el último canvas
        canva_name = f"{selected_size_name.replace(' ', '_').lower()}_{paper_type.replace(' ', '_').lower()}_output_{canvas_count}.png"
        canvas.save(os.path.join(output_folder_path, canva_name), format="PNG", dpi=(300, 300))

# Ejecuta el procesamiento de imágenes en un hilo separado
def run_processing():
    global processing_cancelled
    processing_cancelled = False  # Resetear la bandera de cancelación

    # Deshabilitar el botón de procesamiento mientras se ejecuta
    process_button.config(state='disabled')
    cancel_button.config(state='normal')  # Hacer visible el botón de cancelación
    # Hacer visible el ProgressBar y el label
    progress_label.grid(row=7, column=0, padx=10, pady=(5, 0), sticky='w')  # Añadir espacio arriba
    progress_bar.grid(row=8, column=0, padx=10, pady=(0, 5), sticky='ew')

    # Crear un hilo para el procesamiento
    global processing_thread
    processing_thread = threading.Thread(target=process_images_thread)
    processing_thread.start()

def process_images_thread():
    images_folder_path = images_folder.get()
    output_folder_path = output_folder.get()
    selected_size_name = selected_size.get()
    new_image_size = sizes[selected_size_name]
    paper_type = selected_paper_type.get()

    if not os.path.exists(images_folder_path):
        messagebox.showerror("Error", texts[current_language]['error_image_folder'])
        return

    if not os.path.exists(output_folder_path):
        messagebox.showerror("Error", texts[current_language]['error_output_folder'])
        return

    process_images(images_folder_path, output_folder_path, new_image_size, selected_size_name, paper_type)

    if processing_cancelled:
        update_label_text(progress_label, texts[current_language]['cancelled_message'])
    else:
        if open_output.get():
            subprocess.Popen(f'explorer "{output_folder_path}"')

        # Mostrar mensaje de éxito
        update_label_text(progress_label, texts[current_language]['success_message'])

    # Rehabilitar el botón de procesamiento
    process_button.config(state='normal')
    cancel_button.config(state='disabled')  # Ocultar el botón de cancelación

    # Ocultar el ProgressBar y el label después de 5 segundos
    root.after(5000, hide_progress_elements)

def hide_progress_elements():
    progress_label.grid_forget()
    progress_bar.grid_forget()

# Función para cancelar el procesamiento
def cancel_processing():
    global processing_cancelled
    processing_cancelled = True
    progress_bar.configure(style='red.Horizontal.TProgressbar')
    update_label_text(progress_label, texts[current_language]['cancelled_message'])

# Cambia el idioma de la interfaz
def change_language(lang):
    global current_language
    current_language = lang
    update_texts()
    update_tooltips()

def update_tooltips():
    ToolTip(entry_image_folder, texts[current_language]['image_folder_tooltip'] + texts[current_language]['available_extensions'])
    ToolTip(entry_output_folder, texts[current_language]['output_folder_tooltip'])

# Actualiza los textos de la interfaz según el idioma seleccionado
def update_texts():
    root.title(texts[current_language]['title'])
    
    if label_image_folder: 
        label_image_folder.config(text=texts[current_language]['image_folder_label'])
    if label_output_folder:
        label_output_folder.config(text=texts[current_language]['output_folder_label'])
    if label_select_size: 
        label_select_size.config(text=texts[current_language]['select_size_label'])
    if label_select_paper: 
        label_select_paper.config(text=texts[current_language]['select_paper_size_label'])
        
    process_button.config(text=texts[current_language]['process_button'])
    cancel_button.config(text=texts[current_language]['cancel_button'])  # Agregar botón de cancelación

    checkbutton.config(text=texts[current_language]['open_output_check'])

    size_combobox['values'] = list(sizes.keys())
    size_combobox.set(selected_size.get())

    paper_combobox['values'] = list(paper_horizontal_sizes.keys())
    paper_combobox.set(selected_paper_type.get())

# Función para manejar el cambio de idioma
def on_language_change(event):
    selected_lang = language_selected.get()
    lang_code = language_map[selected_lang]
    change_language(lang_code)

def update_label_text(label, text):
    label.config(text=text)

# Crear un frame para seleccionar el idioma
language_frame = Frame(root)
language_frame.grid(row=0, column=0, padx=10, pady=10, sticky='w')

# Combobox para seleccionar idioma
language_selected = StringVar(value="English")
language_label = Label(language_frame, text=texts[current_language]['language_label'])
language_label.pack(side='left', padx=(0, 10))

language_combobox = ttk.Combobox(language_frame, textvariable=language_selected, values=list(language_map.keys()), state='readonly', width=15)
language_combobox.pack(side='left')
language_combobox.bind("<<ComboboxSelected>>", on_language_change)

# Crea los labels y entradas en el grid
label_image_folder, entry_image_folder = create_label_and_entry(root, texts[current_language]['image_folder_label'], images_folder, 1)
label_output_folder, entry_output_folder = create_label_and_entry(root, texts[current_language]['output_folder_label'], output_folder, 2)

label_select_size, size_combobox = create_label_and_combobox(root, texts[current_language]['select_size_label'], selected_size, 3, list(sizes.keys()), 20)
label_select_paper, paper_combobox = create_label_and_combobox(root, texts[current_language]['select_paper_size_label'], selected_paper_type, 4, list(paper_horizontal_sizes.keys()), 10)

# Checkbutton para abrir la carpeta de salida
open_output = BooleanVar(value=False)
checkbutton = Checkbutton(root, text=texts[current_language]['open_output_check'], variable=open_output)
checkbutton.grid(row=5, column=0, padx=10, pady=5, sticky='w')

# Botón de procesamiento de imágenes
process_button = Button(root, text=texts[current_language]['process_button'], command=run_processing)
process_button.grid(row=6, column=0, padx=10, pady=5, sticky='w')

# Botón para cancelar el procesamiento
cancel_button = Button(root, text=texts[current_language]['cancel_button'], command=cancel_processing, state='disabled')
cancel_button.grid(row=6, column=0, padx=120, pady=5, sticky='w')  # Colocarlo junto al botón de procesar

# Label para el spinner
progress_label = Label(root, text=texts[current_language]['processing'])  # Este label lo usaremos para el spinner
# ProgressBar
progress_bar = ttk.Progressbar(root, length=400, mode='determinate')
update_tooltips()
# Ejecuta el bucle principal
root.mainloop()
