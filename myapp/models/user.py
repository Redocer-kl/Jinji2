"""Модель User.

Содержит класс `User` с проверкой типов для id и name.
"""

from typing import Any, Dict


class User:
    """Сущность пользователя.

    Атрибуты
    ---------
    id : int
        Уникальный идентификатор (положительное целое).
    name : str
        Имя пользователя (не пустая строка).
    """

    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name

    @property
    def id(self) -> int:
        """Геттер id пользователя."""
        return self._id

    @id.setter
    def id(self, value: Any) -> None:
        if not isinstance(value, int):
            raise TypeError("User.id must be int")
        if value <= 0:
            raise ValueError("User.id must be positive")
        self._id = value

    @property
    def name(self) -> str:
        """Геттер имени пользователя."""
        return self._name

    @name.setter
    def name(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError("User.name must be a string")
        if not value.strip():
            raise ValueError("User.name must not be empty")
        self._name = value.strip()

    def to_dict(self) -> Dict[str, Any]:
        """Вернуть сериализуемое представление пользователя."""
        return {"id": self.id, "name": self.name}
