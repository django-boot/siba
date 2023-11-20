from siba import SIBA_SETTINGS
from siba.parser import Parsable, ParsingRule


class PluralizedParsable(Parsable):

    def __init__(self, data: dict):
        self.data = data

    def parse(self, key: str, *args, **kwargs) -> str:
        pluralization_count = kwargs.get("p_count", 1)
        if pluralization_count == 0:
            return self.data["none"]
        if pluralization_count == 1:
            return self.data["one"]

        pluralization_settings = SIBA_SETTINGS.get("pluralization", {})

        if (
            pluralization_settings.get("some_enabled", False)
            and 1 < pluralization_count < pluralization_settings.get("some_limit", 4)
        ):
            return self.data["some"]

        return self.data["many"]


class PluralizationParsingRule(ParsingRule):

    def matches(self, data: dict) -> bool:
        if "one" in data and "many" in data:
            return True
        return False

    def parsed_value(self, data: dict) -> Parsable:
        return PluralizedParsable(data)
