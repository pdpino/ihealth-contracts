import re
from unidecode import unidecode

_SEPARATOR_PATTERN = re.compile(r"[\s_\-]+")

def sanitize_string(s):
    s = s.lower()
    s = re.sub(_SEPARATOR_PATTERN, "-", s)
    return unidecode(s)

REQUIRED_COLUMNS = [
    'name',
    'rut',
    'home_address',
    'date_gen',
    'date_start',
    'date_end',
    'amount_num',
    'amount_words',
    'template',
]