# Generate ANID paperwork

## Installation

`pip install python-docx pandas openpyxl Unidecode pyinstaller`

* do not install via conda, pyinstaller packaging may not work
* Future: num2words

### Check tkinter is installed:

`python -m tkinter`

## Running

`python src/main.py`

## Deploy

* Generate executable: `python -m PyInstaller convenios.spec`
* Run:
  * Linux: `./dist/convenios`
  * Windows: execute `dist\convenios.exe`
