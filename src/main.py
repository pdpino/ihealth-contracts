import operator
import os
import tkinter as tk
import tkinter.font as tk_font
from tkinter import ttk

from people import read_people_df
from document import fill_document
from buttons import InputFilepath
from locales import STRINGS
from utils import sanitize_string

def find_first_occurence(folders, target, default_value):
    target = target.lower().strip()

    for folder in folders:
        if target in sanitize_string(folder.lower().strip()):
            return folder
    return default_value


def load_default_folders():
    available_folders = [f for f in os.listdir('.') if os.path.isdir(f)]

    template_folder = find_first_occurence(available_folders, 'plantilla', 'plantillas')
    out_folder = find_first_occurence(available_folders, 'autogenerado', 'autogenerados')

    template_folder = os.path.abspath(template_folder)
    out_folder = os.path.abspath(out_folder)

    return template_folder, out_folder

class App:
    def __init__(self):
        # UI window
        self.window = tk.Tk()
        self.window.title(STRINGS['generate_contracts'])

        style = ttk.Style()
        body_font = tk_font.Font(size=18)
        labelframe_font = tk_font.Font(size=15)
        style.configure('TLabelframe', padding=5, borderwidth=0)
        style.configure('TLabelframe.Label', font=labelframe_font)
        style.configure('TLabel', font=body_font, padding=10)
        style.configure('TButton', font=body_font, padding=10)
        style.configure('Success.TLabel', foreground="#1c8246")
        style.configure('Error.TLabel', foreground="#df1010")

        # State
        self.people_df = None
        self.template_folder, self.out_folder = load_default_folders()

        # Status bar
        self.status_str = None
        self.status_label = None

        self.mainframe = ttk.Frame(self.window, padding="5")
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        # self.mainframe.columnconfigure(0, weight=1)
        # self.mainframe.rowconfigure(0, weight=1)

        buttons_frame = ttk.Labelframe(self.mainframe, text=STRINGS['settings'])
        buttons_frame.grid(row=1, column=1)
        InputFilepath(
            buttons_frame,
            button_text=STRINGS['select_template_folder'],
            callback=self.store_template_folder,
            pathtype="folder",
            initial_value=self.template_folder,
        ).grid(row=1, column=1)

        InputFilepath(
            buttons_frame,
            button_text=STRINGS['select_out_folder'],
            callback=self.store_out_folder,
            pathtype="folder",
            initial_value=self.out_folder,
        ).grid(row=2, column=1)

        InputFilepath(
            buttons_frame,
            button_text=STRINGS['select_people_file'],
            callback=self.load_people_file,
        ).grid(row=3, column=1)

        # Input: people checkboxes
        self.people_checkbox_frame = ttk.Labelframe(self.mainframe, text=STRINGS['choose_people'])
        self.people_checkbox_frame.grid(row=2, column=1)

        # Submit button
        ttk.Button(self.mainframe, text=STRINGS['generate_contracts'], command=self.generate_files).grid(row=3, column=1, sticky=tk.E)

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

    def load_people_file(self, filepath):
        if not os.path.isfile(filepath):
            self.show_message(STRINGS.get('file_not_found', filepath))
            return False

        try:
            self.people_df = read_people_df(filepath)
            self.show_message(STRINGS.get('found_n_people_in_file', len(self.people_df), os.path.basename(filepath)))
        except Exception as e:
            print(e, type(e))
            self.show_message(str(e), error=True)
            return False

        ## Update list
        # Clear previous selection
        for widget in self.people_checkbox_frame.winfo_children():
            widget.destroy()

        # List people to select
        self.selected_all = tk.BooleanVar()
        ttk.Checkbutton(
            self.people_checkbox_frame,
            text=STRINGS['all'],
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
        self.people_list.heading("#0", text=STRINGS['name'], command=lambda: self.sort_people_by('name'))
        self.people_list.heading("rut", text=STRINGS['rut'], command=lambda: self.sort_people_by('rut'))
        self.people_list.heading("template", text=STRINGS['position'], command=lambda: self.sort_people_by('template'))

        self.last_sorted_by = (None, None)

        for index, row in self.people_df.iterrows():
            self.people_list.insert(
                '',
                'end',
                row.rut, text=row['name'], values=(row.rut, row.template),
            )

        self.people_list.bind("<<TreeviewSelect>>", self.update_all_checkbox)

        return True

    def store_out_folder(self, folderpath):
        self.out_folder = folderpath
        return True

    def store_template_folder(self, folderpath):
        if not os.path.exists(folderpath):
            return False
        self.template_folder = folderpath
        return True

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
        if self.template_folder is None:
            self.show_message(STRINGS['select_template_folder'], error=True)
            return
        if self.out_folder is None:
            self.show_message(STRINGS['select_out_folder'], error=True)
            return
        if self.people_df is None:
            self.show_message(STRINGS['select_people_file'], error=True)
            return

        results = []

        selected = set(self.people_list.selection())
        for index, row in self.people_df.iterrows():
            if row.rut in selected:
                results.append(fill_document(
                    row,
                    out_folder=self.out_folder,
                    template_folder=self.template_folder,
                ))

        print(results)
        if len(results) == 0:
            self.show_message(STRINGS['select_person_from_list'], error=True)
        elif all(r.ok for r in results):
            self.show_message(STRINGS.get('n_contracts_generated', len(results)))
        else:
            failures = [f"{r.name} - {r.message}" for r in results if not r.ok]
            failures_listed = '\n'.join(failures)

            self.show_message(STRINGS.get('n_errors_and_details', len(failures), failures_listed), error=True)



if __name__ == '__main__':
    App().run()
