from tkinter import Tk, Label, Entry, Button, StringVar, messagebox, Checkbutton, BooleanVar, Frame, PhotoImage
from tkinter import ttk
from PIL import Image, ImageTk
import os
import subprocess
import threading
from translations.texts import texts
from components.tooltip import ToolTip
from variables import language_map, sizes, paper_horizontal_sizes, side_margin

# Inicialización de la ventana principal
root = Tk()
current_language = 'en'
root.title('Image Spines Tool v0.3-beta')
favicon_path = './images/favicon.ico'

# Configuración del ícono de la ventana
favicon_image = Image.open(favicon_path)
favicon = ImageTk.PhotoImage(favicon_image)
root.iconphoto(False, favicon)

root.resizable(False, False)

# Tamaño de la ventana y posición centrada
window_width = 600
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x}+{int(y)}")

# Variables
selected_size = StringVar(value=list(sizes.keys())[0])
selected_paper_type = StringVar(value=list(paper_horizontal_sizes.keys())[0])
images_folder = StringVar(value=r"C:\Users\Spines\Desktop\SpinesImages")
output_folder = StringVar(value=r"C:\Users\Spines\Desktop\SpinesImages\Output")
processing_thread = None
processing_cancelled = False

# Funciones de creación de widgets
def create_label_and_entry(parent, label_text, var, row, width=50):
    frame = Frame(parent)
    frame.grid(row=row, column=0, padx=10, pady=5, sticky='w')
    label = Label(frame, text=label_text)
    label.pack(side='left', padx=(0, 10))
    entry = Entry(frame, textvariable=var, width=width)
    entry.pack(side='right')
    return label, entry

def create_label_and_combobox(parent, label_text, var, row, options, width=50):
    frame = Frame(parent)
    frame.grid(row=row, column=0, padx=10, pady=5, sticky='w')
    label = Label(frame, text=label_text)
    label.pack(side='left', padx=(0, 10))
    combobox = ttk.Combobox(frame, textvariable=var, values=options, state='readonly', width=width)
    combobox.pack(side='right')
    return label, combobox

# Funciones de procesamiento de imágenes
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
            break

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

            progress_bar['value'] = (index + 1) / total_images * 100
            root.update_idletasks()

        except Exception as e:
            print(f"Error al procesar la imagen {image_file}: {e}")

    if x_offset > side_margin and not processing_cancelled:
        canva_name = f"{selected_size_name.replace(' ', '_').lower()}_{paper_type.replace(' ', '_').lower()}_output_{canvas_count}.png"
        canvas.save(os.path.join(output_folder_path, canva_name), format="PNG", dpi=(300, 300))

def run_processing():
    global processing_cancelled
    processing_cancelled = False

    process_button.config(state='disabled')
    cancel_button.config(state='normal')
    progress_label.grid(row=7, column=0, padx=10, pady=(5, 0), sticky='w')
    progress_bar.grid(row=8, column=0, padx=10, pady=(0, 5), sticky='ew')

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
        process_button.config(state='normal')
        cancel_button.config(state='disabled')
        hide_progress_elements()
        return

    if not os.path.exists(output_folder_path):
        messagebox.showerror("Error", texts[current_language]['error_output_folder'])
        process_button.config(state='normal')
        cancel_button.config(state='disabled')
        hide_progress_elements()
        return

    process_images(images_folder_path, output_folder_path, new_image_size, selected_size_name, paper_type)

    if processing_cancelled:
        update_label_text(progress_label, texts[current_language]['cancelled_message'])
    else:
        if open_output.get():
            subprocess.Popen(f'explorer "{output_folder_path}"')

        update_label_text(progress_label, texts[current_language]['success_message'])

    process_button.config(state='normal')
    cancel_button.config(state='disabled')
    root.after(5000, hide_progress_elements)

def hide_progress_elements():
    progress_label.grid_forget()
    progress_bar.grid_forget()

def cancel_processing():
    global processing_cancelled
    processing_cancelled = True
    progress_bar.configure(style='red.Horizontal.TProgressbar')
    update_label_text(progress_label, texts[current_language]['cancelled_message'])

def change_language(lang):
    global current_language
    current_language = lang
    update_texts()
    update_tooltips()

def update_tooltips():
    ToolTip(entry_image_folder, texts[current_language]['image_folder_tooltip'] + texts[current_language]['available_extensions'])
    ToolTip(entry_output_folder, texts[current_language]['output_folder_tooltip'])

def update_texts():
    if label_image_folder: 
        label_image_folder.config(text=texts[current_language]['image_folder_label'])
    if label_output_folder:
        label_output_folder.config(text=texts[current_language]['output_folder_label'])
    if label_select_size: 
        label_select_size.config(text=texts[current_language]['select_size_label'])
    if label_select_paper: 
        label_select_paper.config(text=texts[current_language]['select_paper_size_label'])
        
    process_button.config(text=texts[current_language]['process_button'])
    cancel_button.config(text=texts[current_language]['cancel_button'])
    checkbutton.config(text=texts[current_language]['open_output_check'])
    size_combobox['values'] = list(sizes.keys())
    size_combobox.set(selected_size.get())
    paper_combobox['values'] = list(paper_horizontal_sizes.keys())
    paper_combobox.set(selected_paper_type.get())

def on_language_change(event):
    selected_lang = language_selected.get()
    lang_code = language_map[selected_lang]
    change_language(lang_code)

def update_label_text(label, text):
    label.config(text=text)

def add_signature():
    signature = Label(root, text="By Kyshino", font=('Arial', 8), fg='gray', bg=root.cget("bg"))
    signature.place(relx=0.98, rely=0.99, anchor='se')

# Frame para selección de idioma fuera del Notebook
language_frame = Frame(root)
language_frame.grid(row=0, column=0, padx=10, pady=10, sticky='w')

language_selected = StringVar(value="English")
language_label = Label(language_frame, text=texts[current_language]['language_label'])
language_label.pack(side='left', padx=(0, 10))

language_combobox = ttk.Combobox(language_frame, textvariable=language_selected, values=list(language_map.keys()), state='readonly', width=15)
language_combobox.pack(side='left')
language_combobox.bind("<<ComboboxSelected>>", on_language_change)

# Notebook con dos pestañas
notebook = ttk.Notebook(root)
notebook.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

tab_processing = Frame(notebook)
notebook.add(tab_processing, text="Image Processing")

label_image_folder, entry_image_folder = create_label_and_entry(tab_processing, texts[current_language]['image_folder_label'], images_folder, 1)
label_output_folder, entry_output_folder = create_label_and_entry(tab_processing, texts[current_language]['output_folder_label'], output_folder, 2)
label_select_size, size_combobox = create_label_and_combobox(tab_processing, texts[current_language]['select_size_label'], selected_size, 3, list(sizes.keys()), 20)
label_select_paper, paper_combobox = create_label_and_combobox(tab_processing, texts[current_language]['select_paper_size_label'], selected_paper_type, 4, list(paper_horizontal_sizes.keys()), 10)

open_output = BooleanVar(value=False)
checkbutton = Checkbutton(tab_processing, text=texts[current_language]['open_output_check'], variable=open_output)
checkbutton.grid(row=5, column=0, padx=10, pady=5, sticky='w')

process_button = Button(tab_processing, text=texts[current_language]['process_button'], command=run_processing)
process_button.grid(row=6, column=0, padx=10, pady=5, sticky='w')

cancel_button = Button(tab_processing, text=texts[current_language]['cancel_button'], command=cancel_processing, state='disabled')
cancel_button.grid(row=6, column=0, padx=120, pady=5, sticky='w')

progress_label = Label(tab_processing, text=texts[current_language]['processing'])
progress_bar = ttk.Progressbar(tab_processing, length=400, mode='determinate')

# Segunda pestaña "Downloads"
tab_downloads = Frame(notebook)
notebook.add(tab_downloads, text="Downloads")

downloads_label = Label(tab_downloads, text="Downloads Section")
downloads_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

# Tooltips y Firma
update_tooltips()
add_signature()

# Loop principal de Tkinter
root.mainloop()
