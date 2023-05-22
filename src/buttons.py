import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk


class InputFilepath:
    def __init__(self,
                 root,
                 button_text="Selecciona archivo",
                 callback=None,
                 pathtype="file",
                 initial_value=None):
        self.root = root
        self.callback = callback
        self.pathtype = pathtype

        self.frame = ttk.Labelframe(root) # , text="Archivo/carpeta"

        ttk.Button(
            self.frame,
            text=button_text,
            command=self.load_file_dialog,
        ).grid(row=1, column=1, sticky=tk.W)
        self.label = ttk.Label(
            self.frame,
            text="vacío" if initial_value is None else initial_value,
        )
        self.label.grid(row=1, column=2, sticky=tk.E)

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

    def load_file_dialog(self):
        if self.pathtype == "folder":
            filepath = filedialog.askdirectory(parent=self.root, mustexist=True)
        else:
            filepath = filedialog.askopenfilename(parent=self.root)

        filepath = os.path.abspath(filepath)

        if filepath and self.callback is not None:
            success = self.callback(filepath)
        else:
            success = False

        if success:
            self.label.configure(text=filepath)
