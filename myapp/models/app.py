"""Модель App — метаданные приложения.

Содержит класс `App` с полями name, version и author (объект Author).
"""

from typing import Any, Dict
from .author import Author


class App:
    """Модель метаданных приложения.

    Атрибуты
    ---------
    name : str
        Название приложения.
    version : str
        Версия приложения.
    author : Author
        Объект автора приложения.
    """

    def __init__(self, name: str, version: str, author: Author) -> None:
        self.name = name
        self.version = version
        self.author = author

    @property
    def name(self) -> str:
        """Название приложения."""
        return self._name

    @name.setter
    def name(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError("App.name must be a string")
        if not value:
            raise ValueError("App.name must not be empty")
        self._name = value

    @property
    def version(self) -> str:
        """Строка версии приложения."""
        return self._version

    @version.setter
    def version(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError("App.version must be a string")
        self._version = value

    @property
    def author(self) -> Author:
        """Объект Author."""
        return self._author

    @author.setter
    def author(self, value: Any) -> None:
        if not isinstance(value, Author):
            raise TypeError("App.author must be an Author instance")
        self._author = value

    def to_dict(self) -> Dict[str, Any]:
        """Вернуть сериализуемое представление метаданных приложения."""
        return {"name": self.name, "version": self.version, "author": self.author.to_dict()}
