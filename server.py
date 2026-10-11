"""Основной модуль aiohttp-приложения."""

import json

from aiohttp import web
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth import hash_password
from db import Advertisement, Session, User, close_db, init_db
from schema import (
    CreateAdvertisement,
    CreateUser,
    HttpError,
    UpdateAdvertisement,
    UpdateUser,
    validate,
)


# ============================================================
# Контекст жизненного цикла приложения
# ============================================================

async def orm_context(app: web.Application):
    """Инициализирует и закрывает БД при старте/остановке."""
    print("START")
    await init_db()
    yield
    await close_db()
    print("END")


# ============================================================
# Middleware
# ============================================================

@web.middleware
async def session_middleware(
    request: web.Request,
    handler,
) -> web.StreamResponse:
    """Создаёт сессию БД на время обработки запроса."""
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


@web.middleware
async def error_middleware(
    request: web.Request,
    handler,
) -> web.StreamResponse:
    """Перехватывает HttpError и превращает в JSON-ответ."""
    try:
        return await handler(request)
    except HttpError as err:
        return web.json_response(
            {"error": err.message},
            status=err.status_code,
        )


# ============================================================
# Вспомогательная функция для ошибок
# ============================================================

def get_error(
    err_cls: type,
    err_msg,
) -> web.HTTPException:
    """Формирует HTTP-исключение aiohttp с JSON-телом.

    :param err_cls: класс исключения (web.HTTPNotFound и т.п.);
    :param err_msg: сообщение об ошибке;
    :return: экземпляр исключения с JSON-телом.
    """
    return err_cls(
        text=json.dumps({"error": err_msg}),
        content_type="application/json",
    )


# ============================================================
# Представление для пользователей
# ============================================================

class UserView(web.View):
    """CRUD-операции для пользователей."""

    @property
    def user_id(self) -> int:
        """Возвращает id пользователя из URL."""
        return int(self.request.match_info["user_id"])

    @property
    def session(self) -> AsyncSession:
        """Возвращает сессию БД из запроса."""
        return self.request.session

    async def get_user(self) -> User:
        """Возвращает пользователя по id или 404."""
        user = await self.session.get(User, self.user_id)
        if user is None:
            raise get_error(web.HTTPNotFound, "user not found")
        return user

    async def add_user(self, user: User) -> None:
        """Сохраняет пользователя или отдаёт 409."""
        self.session.add(user)
        try:
            await self.session.commit()
        except IntegrityError:
            raise get_error(web.HTTPConflict, "user already exists")

    async def get(self) -> web.Response:
        """GET /users/{id} — получить пользователя."""
        user = await self.get_user()
        return web.json_response(user.dict)

    async def post(self) -> web.Response:
        """POST /users — создать пользователя."""
        json_data = await self.request.json()
        data = validate(json_data, CreateUser)

        user = User(
            name=data["name"],
            password=hash_password(data["password"]),
        )
        await self.add_user(user)
        return web.json_response(user.id_dict)

    async def patch(self) -> web.Response:
        """PATCH /users/{id} — обновить пользователя."""
        json_data = await self.request.json()
        data = validate(json_data, UpdateUser)
        user = await self.get_user()

        if "name" in data:
            user.name = data["name"]
        if "password" in data:
            user.password = hash_password(data["password"])

        await self.add_user(user)
        return web.json_response(user.dict)

    async def delete(self) -> web.Response:
        """DELETE /users/{id} — удалить пользователя."""
        user = await self.get_user()
        await self.session.delete(user)
        await self.session.commit()
        return web.json_response({"message": "deleted"})


# ============================================================
# Представление для объявлений
# ============================================================

class AdvertisementView(web.View):
    """CRUD-операции для объявлений."""

    @property
    def advertisement_id(self) -> int:
        """Возвращает id объявления из URL."""
        return int(self.request.match_info["advertisement_id"])

    @property
    def session(self) -> AsyncSession:
        """Возвращает сессию БД из запроса."""
        return self.request.session

    async def get_advertisement(self) -> Advertisement:
        """Возвращает объявление по id или 404."""
        advertisement = await self.session.get(
            Advertisement,
            self.advertisement_id,
        )
        if advertisement is None:
            raise get_error(web.HTTPNotFound, "advertisement not found")
        return advertisement

    async def add_advertisement(self, advertisement: Advertisement) -> None:
        """Сохраняет объявление или отдаёт 409."""
        self.session.add(advertisement)
        try:
            await self.session.commit()
        except IntegrityError:
            raise get_error(web.HTTPConflict, "advertisement already exists")

    async def get(self) -> web.Response:
        """GET /advertisements/{id} — получить объявление."""
        advertisement = await self.get_advertisement()
        return web.json_response(advertisement.dict)

    async def post(self) -> web.Response:
        """POST /advertisements — создать объявление."""
        json_data = await self.request.json()
        data = validate(json_data, CreateAdvertisement)

        advertisement = Advertisement(
            title=data["title"],
            description=data["description"],
            owner_id=data["owner"],
        )
        await self.add_advertisement(advertisement)
        return web.json_response(advertisement.id_dict)

    async def patch(self) -> web.Response:
        """PATCH /advertisements/{id} — обновить объявление."""
        json_data = await self.request.json()
        data = validate(json_data, UpdateAdvertisement)
        advertisement = await self.get_advertisement()

        if "title" in data:
            advertisement.title = data["title"]
        if "description" in data:
            advertisement.description = data["description"]

        await self.add_advertisement(advertisement)
        return web.json_response(advertisement.dict)

    async def delete(self) -> web.Response:
        """DELETE /advertisements/{id} — удалить объявление."""
        advertisement = await self.get_advertisement()
        await self.session.delete(advertisement)
        await self.session.commit()
        return web.json_response({"message": "deleted"})


# ============================================================
# Регистрация приложения и маршрутов
# ============================================================

app = web.Application()
app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)
app.middlewares.append(error_middleware)

app.add_routes(
    [
        web.post("/users", UserView),
        web.get(r"/users/{user_id:\d+}", UserView),
        web.patch(r"/users/{user_id:\d+}", UserView),
        web.delete(r"/users/{user_id:\d+}", UserView),
        web.post("/advertisements", AdvertisementView),
        web.get(r"/advertisements/{advertisement_id:\d+}", AdvertisementView),
        web.patch(r"/advertisements/{advertisement_id:\d+}", AdvertisementView),
        web.delete(r"/advertisements/{advertisement_id:\d+}", AdvertisementView),
    ]
)


if __name__ == "__main__":
    web.run_app(app, port=8080)