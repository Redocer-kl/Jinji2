"""Модель UserCurrency для связи many-to-many между пользователями и валютами.
"""

from typing import Any, Dict


class UserCurrency:
    """Представляет подписку пользователя на валюту.

    Атрибуты
    ---------
    id : int
        Уникальный идентификатор записи подписки.
    user_id : int
        Внешний ключ на таблицу users.
    currency_id : str
        Идентификатор валюты (соответствует currency.id).
    """

    def __init__(self, id: int, user_id: int, currency_id: str) -> None:
        self.id = id
        self.user_id = user_id
        self.currency_id = currency_id

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: Any) -> None:
        if not isinstance(value, int):
            raise TypeError("UserCurrency.id must be int")
        self._id = value

    @property
    def user_id(self) -> int:
        return self._user_id

    @user_id.setter
    def user_id(self, value: Any) -> None:
        if not isinstance(value, int):
            raise TypeError("UserCurrency.user_id must be int")
        self._user_id = value

    @property
    def currency_id(self) -> str:
        return self._currency_id

    @currency_id.setter
    def currency_id(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError("UserCurrency.currency_id must be str")
        self._currency_id = value

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "user_id": self.user_id, "currency_id": self.currency_id}
