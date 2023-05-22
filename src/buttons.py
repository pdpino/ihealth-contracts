import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

from locales import STRINGS

class InputFilepath:
    def __init__(self,
                 root,
                 button_text=STRINGS['select_file'],
                 callback=None,
                 pathtype="file",
                 initial_value=None):
        self.root = root
        self.callback = callback
        self.pathtype = pathtype

        self.frame = ttk.Labelframe(root)

        ttk.Button(
            self.frame,
            text=button_text,
            command=self.load_file_dialog,
        ).grid(row=1, column=1, sticky=tk.W)
        self.label = ttk.Label(
            self.frame,
            text=STRINGS['empty'] if initial_value is None else initial_value,
        )
        self.label.grid(row=1, column=2, sticky=tk.E)

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

    def load_file_dialog(self):
        if self.pathtype == "folder":
            filepath = filedialog.askdirectory(parent=self.root, mustexist=True)
        else:
            filepath = filedialog.askopenfilename(parent=self.root)

        if not filepath:
            return

        filepath = os.path.abspath(filepath)

        success = self.callback(filepath) if self.callback is not None else False

        if success:
            self.label.configure(text=filepath)
