import aiohttp
import asyncio
from settings import Config

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'

REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'

AUTH_HEADERS = {'Authorization': f'OAuth {Config.DISK_TOKEN}'}

async def upload_file_to_disk(session, file_storage, folder='app:/yacut_uploads'):
    filename = file_storage.filename
    disk_path = f'{folder}/{filename}'

    async with session.get(
        REQUEST_UPLOAD_URL,
        headers=AUTH_HEADERS,
        params={'path': disk_path, 'overwrite': 'True'}
    ) as resp:
        upload_data = await resp.json()
        upload_href = upload_data.get('href')

    file_data = file_storage.read()
    async with session.put(upload_href, data=file_data) as upload_resp:
        if upload_resp.status != 201:
            raise Exception('Ошибка загрузки')
        
    async with session.put(
        f'{API_HOST}{API_VERSION}/disk/resources/publish',
        headers=AUTH_HEADERS,
        params={'path': disk_path}
    ) as publish_resp:
        if publish_resp.status != 200:
            raise Exception('Ошибка публикации')

    async with session.get(
        f'{API_HOST}{API_VERSION}/disk/resources',
        headers=AUTH_HEADERS,
        params={'path': disk_path, 'fields': 'public_url'}
    ) as info_resp:
        file_info = await info_resp.json()
        view_url = file_info.get('public_url')

    async with session.get(
        DOWNLOAD_LINK_URL,
        headers=AUTH_HEADERS,
        params={'path': disk_path}
    ) as download_resp:
        download_data = await download_resp.json()
        direct_url = download_data.get('href')

    return {
        'file_name': filename,
        'view_url': direct_url,  
        'download_url': view_url  
    }

async def upload_multiple_files(files):
    """Асинхронная загрузка нескольких файлов на Яндекс.Диск."""
    async with aiohttp.ClientSession() as session:
        tasks = [upload_file_to_disk(session, file) for file in files]
        results = await asyncio.gather(*tasks)
    return results


