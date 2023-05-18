import re
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

from people import read_people_df
from document import fill_document

class App:
    def __init__(self):
        # UI window
        self.window = tk.Tk()
        self.window.title("Generar convenios") # TODO: move strings out

        self.people_df = None

        mainframe = ttk.Frame(self.window, padding="5")
        mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        # mainframe.columnconfigure(0, weight=1)
        # mainframe.rowconfigure(0, weight=1)

        # Input: people_df
        input_excel_frame = ttk.Labelframe(mainframe, text="Archivo personal")
        input_excel_frame.grid(row=1, column=1)

        ttk.Button(
            input_excel_frame,
            text="Selecciona archivo",
            command=self.load_file_dialog,
        ).grid(row=1, column=1, sticky=tk.W)
        self.people_fname = ttk.Label(
            input_excel_frame,
            text="No has seleccionado archivo", # REVIEW: delete this placeholder?
        )
        self.people_fname.grid(row=1, column=2, sticky=tk.W)

        # Input: people checkboxes
        self.people_checkbox_frame = ttk.Labelframe(mainframe, text="Selecciona personas")
        self.people_checkbox_frame.grid(row=2, column=1)
        # ttk.Label(self.people_checkbox_frame, text="placeholder").grid(row=1, column=1, sticky=tk.W)

        # Submit button
        ttk.Button(mainframe, text="Generar convenios", command=self.generate_files).grid(column=1, row=3, sticky=tk.E)

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def run(self):
        self.window.mainloop()

    def load_file_dialog(self):
        filepath = filedialog.askopenfilename(parent=self.window)

        try:
            self.people_df = read_people_df(filepath)
        except Exception as e:
            # TODO: show error
            print('ERROR: ', e, e.message)
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
                text=row.rut,
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
        results = []

        for index, row in self.people_df.iterrows():
            if self.selected[row.rut].get():
                results.append(fill_document(row))

        print(results)


if __name__ == '__main__':
    App().run()
