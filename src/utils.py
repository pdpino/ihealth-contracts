import re
from unidecode import unidecode

def sanitize_name(name):
    s = name.lower()
    s = re.sub(r"[\s_\-]+", "-", s)
    return unidecode(s)