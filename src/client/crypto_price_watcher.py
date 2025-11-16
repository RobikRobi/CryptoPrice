import asyncio
import httpx
from src.config import CryptoData


async def crypto_price_watcher(interval: int = 5):
    """
    Асинхронный генератор, возвращает новые данные
    ТОЛЬКО когда курс криптовалют меняется.
    """
    previous_data = None

    while True:
        params = {
            "ids": ",".join(CryptoData.COINS),
            "vs_currencies": CryptoData.VS_CURRENCY,
            "include_24hr_change": "true"
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(CryptoData.CR_URL, params=params)
            response.raise_for_status()
            current_data = response.json()

        # Первой итерации нет с чем сравнивать
        if previous_data is None:
            previous_data = current_data
            yield current_data
        else:
            if current_data != previous_data:      # сравниваем всё JSON
                previous_data = current_data
                yield current_data

        await asyncio.sleep(interval)
