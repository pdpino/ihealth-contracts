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

def _assert_unique_rut(people_df):
    ruts_count = people_df['rut'].value_counts()
    non_unique = ruts_count[ruts_count > 1]

    assert len(non_unique) == 0, f'Repeated RUTs: {dict(non_unique)}'

def read_people_df(filepath_or_buf):
    people_df = pd.read_excel(filepath_or_buf)
    people_df = people_df.rename(columns=_rename_col)

    _assert_unique_rut(people_df)

    return people_df.reset_index(drop=True)
