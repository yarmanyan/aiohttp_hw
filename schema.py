"""Модуль валидации входных данных с помощью Pydantic."""

from typing import Optional, Type

from pydantic import BaseModel, ValidationError


class HttpError(Exception):
    """Исключение для ошибок валидации."""

    def __init__(self, status_code: int, message):
        self.status_code = status_code
        self.message = message


class CreateUser(BaseModel):
    """Схема для создания пользователя."""

    name: str
    password: str


class UpdateUser(BaseModel):
    """Схема для обновления пользователя (все поля необязательные)."""

    name: Optional[str] = None
    password: Optional[str] = None


class CreateAdvertisement(BaseModel):
    """Схема для создания объявления."""

    title: str
    description: str = ""
    owner: int


class UpdateAdvertisement(BaseModel):
    """Схема для обновления объявления (все поля необязательные)."""

    title: Optional[str] = None
    description: Optional[str] = None


def validate(json_data: dict, schema_cls: Type[BaseModel]) -> dict:
    """Валидирует данные по указанной Pydantic-схеме.

    :param json_data: данные из запроса;
    :param schema_cls: класс схемы;
    :return: валидированные данные в виде словаря;
    :raises HttpError: если данные не прошли валидацию.
    """
    try:
        return schema_cls(**json_data).model_dump(exclude_none=True)
    except ValidationError as err:
        errors = err.errors()
        for error in errors:
            error.pop("ctx", None)
        raise HttpError(400, errors)