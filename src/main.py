import operator
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

        # Status bar
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

        self.people_list = ttk.Treeview(
            self.people_checkbox_frame,
            selectmode="extended",
            columns=("rut", "template"),
        )

        scroll_bar = ttk.Scrollbar(self.people_checkbox_frame, orient=tk.VERTICAL, command=self.people_list.yview)
        scroll_bar.grid(row=2, column=1, sticky=(tk.N, tk.S, tk.E))
        self.people_list.configure(yscrollcommand=scroll_bar.set)

        self.people_list.grid(row=2, column=1, sticky=(tk.N, tk.W, tk.S, tk.E))
        self.people_list.heading("#0", text="Nombre", command=lambda: self.sort_people_by('name'))
        self.people_list.heading("rut", text="Rut", command=lambda: self.sort_people_by('rut'))
        self.people_list.heading("template", text="Cargo", command=lambda: self.sort_people_by('template'))

        self.last_sorted_by = (None, None)

        for index, row in self.people_df.iterrows():
            self.people_list.insert(
                '',
                'end',
                row.rut, text=row['name'], values=(row.rut, row.template),
            )

        self.people_list.bind("<<TreeviewSelect>>", self.update_all_checkbox)

    def sort_people_by(self, label):
        index = {
            'name': 1,
            'rut': 2,
            'template': 3,
        }.get(label, 0)

        rows = []
        for item_key in self.people_list.get_children(''):
            item = self.people_list.item(item_key)
            rows.append((item_key, item['text'], *item['values']))

        last_sort_label, last_sort_rev = self.last_sorted_by
        reverse = not last_sort_rev if label == last_sort_label else False
        rows = sorted(rows, key=operator.itemgetter(index), reverse=reverse)

        for index, item_tuple in enumerate(rows):
            item = item_tuple[0]
            self.people_list.move(item, '', index)

        self.last_sorted_by = (label, reverse)

    def press_select_all(self):
        n_selected = len(self.people_list.selection())

        if n_selected == len(self.people_df):
            self.people_list.selection_set(tuple())
            self.selected_all.set(False)
        else:
            self.people_list.selection_set(tuple(self.people_df['rut']))
            self.selected_all.set(True)

    def update_all_checkbox(self, unused_event):
        self.selected_all.set(len(self.people_list.selection()) == len(self.people_df))

    def generate_files(self):
        if self.people_df is None:
            self.show_message("Selecciona un archivo primero", error=True)
            return

        results = []

        parent = 'generated'

        selected = set(self.people_list.selection())
        for index, row in self.people_df.iterrows():
            if row.rut in selected:
                results.append(fill_document(row, parent))

        print(results)
        if len(results) == 0:
            self.show_message("Selecciona alguna persona", error=True)
        else:
            self.show_message(f"{len(results)} convenios generados en carpeta {parent}")



if __name__ == '__main__':
    App().run()
