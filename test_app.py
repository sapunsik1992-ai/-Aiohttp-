import asyncio

from aiohttp.test_utils import TestClient, TestServer

from server import create_app


async def _client():
    server = TestServer(create_app())
    client = TestClient(server)
    await client.start_server()
    try:
        yield client
    finally:
        await client.close()


def test_index_page():
    async def run():
        async for client in _client():
            response = await client.get('/')
            assert response.status == 200
            text = await response.text()
            assert 'Объявления' in text
            assert 'doCreate' in text
            assert 'doGet' in text
            assert 'doDelete' in text

    asyncio.run(run())


def test_create_and_list_ads():
    async def run():
        async for client in _client():
            response = await client.post('/ads', json={'title': 'Квартира', 'owner': 'Иван'})
            assert response.status == 201
            data = await response.json()
            assert data['title'] == 'Квартира'
            assert data['owner'] == 'Иван'
            assert data['description'] == ''
            assert 'id' in data

            list_response = await client.get('/ads')
            assert list_response.status == 200
            all_ads = await list_response.json()
            assert isinstance(all_ads, list)
            assert any(item['title'] == 'Квартира' for item in all_ads)

    asyncio.run(run())


def test_delete_ad():
    async def run():
        async for client in _client():
            create_response = await client.post('/ads', json={'title': 'Удалить', 'owner': 'Анна'})
            created = await create_response.json()

            delete_response = await client.delete(f"/ads/{created['id']}")
            assert delete_response.status == 200
            assert await delete_response.json() == {'message': 'deleted'}

    asyncio.run(run())
