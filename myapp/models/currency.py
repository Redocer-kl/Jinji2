"""Модель Currency.

Модель представляет валюту и её текущий курс с проверками типов.
"""

from typing import Any, Dict


class Currency:
    """Сущность валюты с валидацией полей.

    Атрибуты
    ---------
    id : str
        Идентификатор валюты (например, 'R01235').
    num_code : str
        Цифровой код валюты.
    char_code : str
        Символьный код (USD, EUR и т.д.).
    name : str
        Полное название валюты.
    value : float
        Числовой курс, соответствующий полю nominal.
    nominal : int
        Номинал — за сколько единиц валюты указан курс.
    """

    def __init__(
        self,
        id: str,
        num_code: str,
        char_code: str,
        name: str,
        value: float,
        nominal: int = 1,
    ) -> None:
        self.id = id
        self.num_code = num_code
        self.char_code = char_code
        self.name = name
        self.value = value
        self.nominal = nominal

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError("Currency.id must be a string")
        self._id = value

    @property
    def num_code(self) -> str:
        return self._num_code

    @num_code.setter
    def num_code(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError("Currency.num_code must be a string")
        self._num_code = value

    @property
    def char_code(self) -> str:
        return self._char_code

    @char_code.setter
    def char_code(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError("Currency.char_code must be a string")
        self._char_code = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError("Currency.name must be a string")
        self._name = value

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        try:
            value_float = float(value)
        except (TypeError, ValueError):
            raise TypeError("Currency.value must be a number")
        self._value = value_float

    @property
    def nominal(self) -> int:
        return self._nominal

    @nominal.setter
    def nominal(self, value: Any) -> None:
        if not isinstance(value, int):
            raise TypeError("Currency.nominal must be int")
        if value <= 0:
            raise ValueError("Currency.nominal must be positive")
        self._nominal = value

    def to_dict(self) -> Dict[str, Any]:
        """Вернуть сериализуемое представление объекта Currency."""
        return {
            "id": self.id,
            "num_code": self.num_code,
            "char_code": self.char_code,
            "name": self.name,
            "value": self.value,
            "nominal": self.nominal,
        }
