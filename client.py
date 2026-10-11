"""Асинхронный клиент для тестирования REST API."""

import asyncio

import aiohttp

BASE_URL = "http://127.0.0.1:8080"


async def create_user(
    session: aiohttp.ClientSession,
    name: str,
    password: str,
) -> dict:
    """Создаёт пользователя через API."""
    async with session.post(
        f"{BASE_URL}/users",
        json={"name": name, "password": password},
    ) as resp:
        data = await resp.json()
        print(f"CREATE USER: {resp.status} — {data}")
        return data


async def get_user(
    session: aiohttp.ClientSession,
    user_id: int,
) -> dict:
    """Получает пользователя по id."""
    async with session.get(f"{BASE_URL}/users/{user_id}") as resp:
        data = await resp.json()
        print(f"GET USER: {resp.status} — {data}")
        return data


async def create_advertisement(
    session: aiohttp.ClientSession,
    title: str,
    description: str,
    owner: int,
) -> dict:
    """Создаёт объявление через API."""
    async with session.post(
        f"{BASE_URL}/advertisements",
        json={
            "title": title,
            "description": description,
            "owner": owner,
        },
    ) as resp:
        data = await resp.json()
        print(f"CREATE AD: {resp.status} — {data}")
        return data


async def get_advertisement(
    session: aiohttp.ClientSession,
    advertisement_id: int,
) -> dict:
    """Получает объявление по id."""
    async with session.get(
        f"{BASE_URL}/advertisements/{advertisement_id}"
    ) as resp:
        data = await resp.json()
        print(f"GET AD: {resp.status} — {data}")
        return data


async def patch_advertisement(
    session: aiohttp.ClientSession,
    advertisement_id: int,
    **kwargs,
) -> dict:
    """Обновляет объявление."""
    async with session.patch(
        f"{BASE_URL}/advertisements/{advertisement_id}",
        json=kwargs,
    ) as resp:
        data = await resp.json()
        print(f"PATCH AD: {resp.status} — {data}")
        return data


async def delete_advertisement(
    session: aiohttp.ClientSession,
    advertisement_id: int,
) -> dict:
    """Удаляет объявление по id."""
    async with session.delete(
        f"{BASE_URL}/advertisements/{advertisement_id}"
    ) as resp:
        data = await resp.json()
        print(f"DELETE AD: {resp.status} — {data}")
        return data


async def main() -> None:
    """Прогоняет полный сценарий тестирования API."""
    print("=" * 50)
    print("ТЕСТИРОВАНИЕ API")
    print("=" * 50)

    async with aiohttp.ClientSession() as session:
        # 1. Создаём пользователей.
        print("\n--- Создание пользователей ---")
        await create_user(session, "user_1", "1234")
        await create_user(session, "user_2", "1234")

        # 2. Создаём объявления.
        print("\n--- Создание объявлений ---")
        await create_advertisement(
            session,
            "Продам гараж",
            "Недорого, в центре города",
            owner=1,
        )
        await create_advertisement(
            session,
            "Куплю авто",
            "Бюджет до 500 000",
            owner=2,
        )

        # 3. Получаем объявления.
        print("\n--- Получение объявлений ---")
        await get_advertisement(session, 1)
        await get_advertisement(session, 2)

        # 4. Обновляем объявление.
        print("\n--- Обновление объявления ---")
        await patch_advertisement(
            session,
            1,
            title="Продам гараж (срочно)",
        )
        await get_advertisement(session, 1)

        # 5. Удаляем объявление.
        print("\n--- Удаление объявления ---")
        await delete_advertisement(session, 2)
        await get_advertisement(session, 2)

    print("\n" + "=" * 50)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())