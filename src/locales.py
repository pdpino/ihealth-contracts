import json
import os

_LOCALES_FOLDER = os.path.join(os.path.dirname(__file__), 'locales')

class Strings:
    def __init__(self, locale='es'):
        self.strings_by_locale = {}
        self.current_locale = locale

        for filename in os.listdir(_LOCALES_FOLDER):
            if filename.endswith('.json'):
                name = os.path.splitext(filename)[0]

            with open(os.path.join(_LOCALES_FOLDER, filename)) as f:
                strings = json.load(f)

            self.strings_by_locale[name] = strings

    def get(self, key, *args):
        assert isinstance(key, str), f"Internal error: {key} is not str ({type(str)})"

        strings = self.strings_by_locale.get(self.current_locale, {})
        s = strings.get(key, key)

        if len(args) > 0:
            try:
                s = s.format(*args)
            except IndexError:
                raise f"Internal error: cannot format {str(*args)} into {s}"
        return s

    def __getitem__(self, key):
        return self.get(key)

STRINGS = Strings()
