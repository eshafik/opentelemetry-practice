import httpx
from httpx._models import Response


async def post(url: str, data=None, json=None, **kwargs) -> Response:
    async with httpx.AsyncClient() as client:
        print("url", url)
        return await client.post(url, data=data, json=json, **kwargs)


async def patch(url: str, data=None, json=None, **kwargs) -> Response:
    async with httpx.AsyncClient() as client:
        return await client.patch(url, data=data, json=json, **kwargs)


async def delete(url: str, **kwargs) -> Response:
    async with httpx.AsyncClient() as client:
        return await client.delete(url, **kwargs)


async def get(url: str, **kwargs) -> Response:
    async with httpx.AsyncClient() as client:
        return await client.get(url, **kwargs)
