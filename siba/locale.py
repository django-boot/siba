from os import path
from typing import Type

from siba import SIBA_SETTINGS
from siba.loader import FileLoader, LoaderStrategy
from siba.parsing_rules.pluralization import PluralizationParsingRule


PARSING_RULES = [PluralizationParsingRule()]


def format_file_content(content: dict, base_key: str = None, formatted: dict = None) -> dict:
    """
    From plain dictionary of translations we created a dictionary with dotted keys
    If values are supposed to be "decided on" dynamically per each call to translation then we register the parser
    If value is a string we don't check for parsers
    """
    if formatted is None:
        formatted = dict()

    for key, value in content.items():
        if base_key is None:
            ev_key = key
        else:
            ev_key = base_key + SIBA_SETTINGS['key_split_delimiter'] + key
        if isinstance(value, dict):
            matched = False
            for parsing_rule in PARSING_RULES:
                if parsing_rule.matches(value):
                    formatted[ev_key] = parsing_rule.parsed_value(value)
                    matched = True
                    break

            if not matched:
                format_file_content(value, ev_key, formatted)
        elif isinstance(value, str):
            formatted[ev_key] = value
        else:
            raise ValueError(f"Translation data should either be str or dictionary. Got {type(value)}")

    return formatted


__LOCALE_CACHE = {}


def _get_cache_key(prefix: str, locale: str):
    return f"{prefix}-{locale}"


# This function is not be thread-safe. If preload_locales is not explicitly called at application startup
# then this can lead to trying to cache locales multiple times
def read_locale(prefix: str, locale: str, loader_class: Type[FileLoader] = LoaderStrategy.JSON) -> dict:

    # If cache is enable check for the value in cache
    cache_key = _get_cache_key(prefix, locale)
    if SIBA_SETTINGS.get("cache_locales") and cache_key in __LOCALE_CACHE:
        return __LOCALE_CACHE.get(cache_key)

    # Read the file to load values
    loader = loader_class()
    content: dict = loader.load(
        path.join(SIBA_SETTINGS.get("locales_path"), f"{prefix}.{locale}.{loader.for_type()}"),
        SIBA_SETTINGS.get("error_on_missing_locale_file", True)
    )

    formatted_content = format_file_content(content)
    if SIBA_SETTINGS.get("cache_locales"):
        __LOCALE_CACHE[cache_key] = formatted_content

    return formatted_content


def preload_locales(loader_class: Type[FileLoader] = LoaderStrategy.JSON):
    """
    Preloads all locales into memory
    """
    if not SIBA_SETTINGS.get("cache_locales"):
        return

    loader = loader_class()
    for prefix in SIBA_SETTINGS.get("prefixes", []):
        for locale in SIBA_SETTINGS.get("locales", []):
            content = loader.load(
                path.join(SIBA_SETTINGS.get("locales_path"), f"{prefix}.{locale}.{loader_class.for_type()}"),
                False
            )
            if content is None:
                continue

            formatted_content = format_file_content(content)
            __LOCALE_CACHE[_get_cache_key(prefix, locale)] = formatted_content


def clear_cached_locales():
    __LOCALE_CACHE.clear()


def get_cached_locales():
    return __LOCALE_CACHE
