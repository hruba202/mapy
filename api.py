#api.py – Asynchronní klient pro komunikaci s Mapy.cz REST API přes aiohttp:
#python
import aiohttp

class MapyCzApiClient:
    def __init__(self, api_key: str, session: aiohttp.ClientSession):
        self._api_key = api_key
        self._session = session

    async def async_geocode(self, query: str):
        url = f"https://mapy.cz{query}&apikey={self._api_key}"
        async with self._session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return None
