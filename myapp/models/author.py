from typing import Any, Dict


class Author:
    """Модель автора приложения.

    Атрибуты
    ---------
    name : str
        Полное имя автора.
    group : str
        Учебная группа или подразделение.
    """

    def __init__(self, name: str, group: str) -> None:
        """Создать объект Author.

        Параметры
        ---------
        name : str
            ФИО автора; не должно быть пустым.
        group : str
            Номер/название группы.

        Исключения
        ----------
        TypeError
            Если `name` или `group` не строка.
        ValueError
            Если `name` — пустая строка.
        """
        self.name = name
        self.group = group

    @property
    def name(self) -> str:
        """Получить имя автора."""
        return self._name

    @name.setter
    def name(self, value: Any) -> None:
        """Установить и проверить имя автора."""
        if not isinstance(value, str):
            raise TypeError("Author.name must be a string")
        if not value.strip():
            raise ValueError("Author.name must not be empty")
        self._name = value.strip()

    @property
    def group(self) -> str:
        """Получить группу автора."""
        return self._group

    @group.setter
    def group(self, value: Any) -> None:
        """Установить группу автора."""
        if not isinstance(value, str):
            raise TypeError("Author.group must be a string")
        self._group = value.strip()

    def to_dict(self) -> Dict[str, str]:
        """Вернуть сериализуемое представление автора."""
        return {"name": self.name, "group": self.group}
