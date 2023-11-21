import os.path
from abc import ABC, abstractmethod
import json
from typing import Optional


class FileLoader(ABC):

    @abstractmethod
    def load(self, filepath, raise_error: bool = True) -> Optional[dict]:
        pass

    @staticmethod
    @abstractmethod
    def for_type() -> str:
        pass


class JsonFileLoader(FileLoader):

    @staticmethod
    def for_type() -> str:
        return "json"

    def load(self, filepath, raise_error: bool = True) -> Optional[dict]:

        if not os.path.exists(filepath) and not raise_error:
            return {}

        with open(filepath, "rb") as file:
            data = json.load(file)

            if type(data) != dict:
                raise ValueError("Expected the data loaded from the file to be in dictionary format (json object).")

            return data


class LoaderStrategy:
    JSON = JsonFileLoader
    # Preparation to support other file formats in the future. ex: yml

