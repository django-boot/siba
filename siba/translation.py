from django.utils import translation
from django.utils.functional import lazy

from siba import SIBA_SETTINGS
from siba.locale import read_locale
from siba.parser import Parsable


class Default(dict):
    def __missing__(self, key):
        missing_variable_handler = SIBA_SETTINGS.get("missing_variable_handler")
        return missing_variable_handler(key)


def inject_variables(value: str, variables: dict):
    if variables is None:
        variables = {}

    return value.format_map(Default(variables))


def translate(key: str, prefix: str = None, locale: str = None, variables: dict = None, **kwargs):
    prefix = SIBA_SETTINGS.get("default_prefix") if prefix is None else prefix
    locale = locale if locale is not None else translation.get_language()
    if locale is None:
        locale = SIBA_SETTINGS.get("default_locale")

    locale_content = read_locale(prefix, locale)

    try:
        unchecked_value = locale_content[key]

        if isinstance(unchecked_value, str):
            str_value = unchecked_value

        elif isinstance(unchecked_value, Parsable):
            parsable: Parsable = unchecked_value
            str_value = parsable.parse(key, **kwargs)

        else:
            raise Exception("Unexpected situation! shouldn't get here!")

        return inject_variables(str_value, variables)

    except KeyError:
        if SIBA_SETTINGS.get("error_on_unknown_key"):
            raise KeyError(
                f"Could not find key '{key}' in prefix '{prefix}' for locale '{locale}'"
            )
        return key


translate_lazy = lazy(translate, str)
