from abc import ABC, abstractmethod


class Parsable(ABC):

    @abstractmethod
    def parse(self, key: str, **kwargs) -> str:
        pass


class ParsingRule(ABC):

    @abstractmethod
    def matches(self, data: dict) -> bool:
        pass

    @abstractmethod
    def parsed_value(self, data: dict) -> Parsable:
        pass

