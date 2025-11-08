import aiohttp
import asyncio
from settings import Config

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'

REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'

AUTH_HEADERS = {'Authorization': f'OAuth {Config.DISK_TOKEN}'}


async def upload_file_to_disk(
        session,
        file_storage,
        folder='app:/yacut_uploads'):
    """Загружает один файл на Яндекс.Диск и возвращает ссылки."""
    filename = file_storage.filename
    disk_path = f'{folder}/{filename}'

    async with session.get(
        REQUEST_UPLOAD_URL,
        headers=AUTH_HEADERS,
        params={'path': disk_path, 'overwrite': 'True'}
    ) as resp:
        if resp.status != 200:
            raise Exception(
                f'Ошибка получения URL для загрузки: {
                    resp.status}')
        upload_data = await resp.json()
        upload_href = upload_data.get('href')
        if not upload_href:
            raise Exception(f'Не удалось получить upload_href: {upload_data}')
    file_data = file_storage.read()

    async with session.put(upload_href, data=file_data) as upload_resp:
        if upload_resp.status not in [200, 201, 202]:
            raise Exception(f'Ошибка загрузки файла: {upload_resp.status}')

    async with session.put(
        f'{API_HOST}{API_VERSION}/disk/resources/publish',
        headers=AUTH_HEADERS,
        params={'path': disk_path}
    ) as publish_resp:
        if publish_resp.status != 200:
            print(
                f'Предупреждение: не удалось опубликовать файл: {
                    publish_resp.status}')

    async with session.get(
        DOWNLOAD_LINK_URL,
        headers=AUTH_HEADERS,
        params={'path': disk_path}
    ) as download_resp:
        if download_resp.status != 200:
            raise Exception(f'Ошибка получения ссылки: {download_resp.status}')
        download_data = await download_resp.json()
        direct_url = download_data.get('href')

        if not direct_url:
            raise Exception(
                f'Не удалось получить прямую ссылку: {download_data}')

    return {
        'file_name': filename,
        'view_url': direct_url,
        'download_url': direct_url
    }


async def upload_multiple_files(files):
    """Асинхронная загрузка нескольких файлов на Яндекс.Диск."""
    async with aiohttp.ClientSession() as session:
        tasks = [upload_file_to_disk(session, file) for file in files]
        results = await asyncio.gather(*tasks)
    return results
