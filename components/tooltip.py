from tkinter import Toplevel, Label, Frame

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None

        # Eventos para mostrar y ocultar el tooltip
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.widget.bind("<Button-1>", self.hide_tooltip)  # Ocultar al hacer clic

    def show_tooltip(self, event=None):
        if self.tooltip_window is not None:
            return

        # Posición del tooltip
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        # Crear la ventana del tooltip
        self.tooltip_window = Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Crear un marco para añadir bordes redondeados
        frame = Frame(
            self.tooltip_window,
            background="#F5F5F5",  # Fondo gris claro
            borderwidth=1,
            relief="solid",
            padx=5,
            pady=5
        )
        frame.pack()

        # Crear el label con estilos visuales adicionales
        label = Label(
            frame,
            text=self.text,
            background="#F5F5F5",
            foreground="#333333",
            font=("Helvetica", 10, "normal"),
            padx=10,
            pady=5,
            wraplength=200,
            borderwidth=0  # Sin borde para ajustar el marco
        )
        label.pack()

        # Agregar sombra leve
        self.tooltip_window.attributes('-alpha', 0.95)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
