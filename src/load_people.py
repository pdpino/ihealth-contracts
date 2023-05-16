import re
import pandas as pd

_COL_MAPPING = {
    'nombre': 'name',
    'rut': 'rut',
    'direccion': 'home_address',
    'cargo': 'position',
    'fecha-generado': 'date_gen',
    'fecha-inicio': 'date_start',
    'fecha-termino': 'date_end',
    'monto-numero': 'amount_num',
    'monto-palabras': 'amount_words',
    'template': 'template',
}

def _rename_col(col):
    s = col.lower()
    s = re.sub(r'[\s_\-]+', '-', s)
    return _COL_MAPPING.get(s, s)

def read_people_df(filepath_or_buf):
    try:
        people_df = pd.read_excel(filepath_or_buf)
    except ValueError:
        return None
    # TODO: verify columns
    people_df = people_df.rename(columns=_rename_col)
    return people_df
