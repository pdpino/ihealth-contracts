import re
import pandas as pd

from utils import sanitize_string, REQUIRED_COLUMNS

_COL_MAPPING = {
    'nombre': 'name',
    'nombre-completo': 'name',
    'rut': 'rut',
    'direccion': 'home_address',
    'domicilio': 'home_address',
    'fecha-generado': 'date_gen',
    'fecha-inicio': 'date_start',
    'fecha-termino': 'date_end',
    'monto-numero': 'amount_num',
    'monto-palabras': 'amount_words',
    'template': 'template',
    'plantilla': 'template',
}

assert set(REQUIRED_COLUMNS).issubset(_COL_MAPPING.values()), "Internal error: _COL_MAPPING is not full"

def _rename_col(col):
    s = sanitize_string(col)
    return _COL_MAPPING.get(s, s)

def _assert_required_columns(people_df_with_raw_cols):
    for col in REQUIRED_COLUMNS:
        # Note: there might be duplicated columns
        appearances = [
            raw_column
            for raw_column in people_df_with_raw_cols.columns
            if _rename_col(raw_column) == col
        ]
        if len(appearances) == 0:
            raise ValueError(f'Falta columna {col}')
        if len(appearances) > 1:
            raise ValueError(f'Columnas repetida: {appearances}')

def _assert_unique_rut(people_df):
    ruts_count = people_df['rut'].value_counts()
    non_unique = ruts_count[ruts_count > 1]

    assert len(non_unique) == 0, f'RUTs repetidos: {dict(non_unique)}'

def _assert_unique_name(people_df):
    name_counts = people_df['name'].apply(sanitize_string).value_counts()
    non_unique = name_counts[name_counts > 1]

    assert len(non_unique) == 0, f'Nombre repetidos: {dict(non_unique)}'

def _assert_at_least_one_person(people_df):
    assert len(people_df) >= 1, f'No se encontraron personas'

def read_people_df(filepath_or_buf):
    try:
        people_df = pd.read_excel(filepath_or_buf)
    except ValueError:
        raise ValueError('Formato incorrecto, usar archivo excel')

    _assert_required_columns(people_df)

    people_df = people_df.rename(columns=_rename_col)

    _assert_unique_rut(people_df)
    _assert_unique_name(people_df)
    _assert_at_least_one_person(people_df)

    return people_df.reset_index(drop=True)
