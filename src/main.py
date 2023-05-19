import re
import os
import tkinter as tk
import tkinter.font as tk_font
from tkinter import filedialog
from tkinter import ttk

from people import read_people_df
from document import fill_document

# TODO: move strings out

class App:
    def __init__(self):
        # UI window
        self.window = tk.Tk()
        self.window.title("Generar convenios")

        style = ttk.Style()
        body_font = tk_font.Font(size=18)
        labelframe_font = tk_font.Font(size=15)
        style.configure('TLabelframe', padding=5, borderwidth=0)
        style.configure('TLabelframe.Label', font=labelframe_font)
        style.configure('TLabel', font=body_font, padding=10)
        style.configure('TButton', font=body_font, padding=10)
        style.configure('Success.TLabel', foreground="#1c8246")
        style.configure('Error.TLabel', foreground="#df1010")

        self.people_df = None

        self.mainframe = ttk.Frame(self.window, padding="5")
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        # self.mainframe.columnconfigure(0, weight=1)
        # self.mainframe.rowconfigure(0, weight=1)

        # Input: people_df
        input_excel_frame = ttk.Labelframe(self.mainframe, text="Archivo personas")
        input_excel_frame.grid(row=1, column=1)

        ttk.Button(
            input_excel_frame,
            text="Selecciona archivo",
            command=self.load_file_dialog,
        ).grid(row=1, column=1, sticky=tk.W)
        self.people_fname = ttk.Label(
            input_excel_frame,
            text="No has seleccionado archivo",
        )
        self.people_fname.grid(row=1, column=2, sticky=tk.E)

        # Input: people checkboxes
        self.people_checkbox_frame = ttk.Labelframe(self.mainframe, text="Selecciona personas")
        self.people_checkbox_frame.grid(row=2, column=1)

        self.status_str = None
        self.status_label = None

        # Submit button
        ttk.Button(self.mainframe, text="Generar convenios", command=self.generate_files).grid(column=1, row=3, sticky=tk.E)

        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def run(self):
        self.window.mainloop()

    def show_message(self, message, error=False):
        if self.status_str is None or self.status_label is None:
            self.status_str = tk.StringVar()
            self.status_label = ttk.Label(
                self.mainframe,
                textvariable=self.status_str,
            )
            self.status_label.grid(row=4, column=1, rowspan=2)

        self.status_str.set(message)
        self.status_label.configure(style=f'{"Error" if error else "Success"}.TLabel')

    def load_file_dialog(self):
        filepath = filedialog.askopenfilename(parent=self.window)

        try:
            self.people_df = read_people_df(filepath)
            self.show_message(f"Se encontraron {len(self.people_df)} personas en archivo {os.path.basename(filepath)}")
        except Exception as e:
            print(e, type(e))
            self.show_message(str(e), error=True)
            return

        # Update filename
        self.people_fname.configure(text=os.path.basename(filepath))

        # Clear previous selection
        for widget in self.people_checkbox_frame.winfo_children():
            widget.destroy()

        # List people to select
        self.selected_all = tk.BooleanVar()
        ttk.Checkbutton(
            self.people_checkbox_frame,
            text="Todos",
            variable=self.selected_all,
            command=self.press_select_all,
        ).grid(row=1, column=1, sticky=tk.W)

        self.selected = {}
        for index, row in self.people_df.iterrows():
            self.selected[row.rut] = tk.BooleanVar()
            ttk.Checkbutton(
                self.people_checkbox_frame,
                text=row['name'],
                variable=self.selected[row.rut],
                command=self.update_all_checkbox,
            ).grid(row=index+2, column=1, sticky=tk.W)

    def press_select_all(self):
        current_selection = sum(int(v.get()) for v in self.selected.values())
        to_state = current_selection == 0

        self.selected_all.set(to_state)
        for v in self.selected.values():
            v.set(to_state)

    def update_all_checkbox(self):
        are_all_selected = all(v.get() for v in self.selected.values())

        self.selected_all.set(are_all_selected)

    def generate_files(self):
        if self.people_df is None:
            self.show_message("Selecciona un archivo primero", error=True)
            return

        results = []

        parent = 'generated'

        for index, row in self.people_df.iterrows():
            if self.selected[row.rut].get():
                results.append(fill_document(row, parent))

        print(results)
        if len(results) == 0:
            self.show_message("Selecciona alguna persona", error=True)
        else:
            self.show_message(f"{len(results)} convenios generados en carpeta {parent}")



if __name__ == '__main__':
    App().run()
