from tkinter import Frame, Label, Entry, Button, ttk

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

def create_button(parent, text, command, row, column=0, padx=10, pady=5, state='normal', sticky='w'):
    button = Button(parent, text=text, command=command, state=state)
    button.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
    return button

def create_progress_elements(parent, initial_text, row_label, row_bar):
    progress_label = Label(parent, text=initial_text)
    progress_bar = ttk.Progressbar(parent, length=400, mode='determinate')
    
    progress_label.grid(row=row_label, column=0, padx=10, pady=(5, 0), sticky='w')
    progress_bar.grid(row=row_bar, column=0, padx=10, pady=(0, 5), sticky='ew')
    
    return progress_label, progress_bar

def update_label_text(label, text):
    label.config(text=text) 