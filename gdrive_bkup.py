from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
import io
import os
from datetime import datetime
from urllib.parse import quote
import re
from loguru import logger

logger.add('gdrive_bkup.log', rotation='10 MB')
# Настройки аутентификации
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = Credentials.from_authorized_user_info(info={
    'client_id': '1060891680186-kkllvigo6e9dsfjpj7osv626gusqnakg.apps.googleusercontent.com',
    'client_secret': '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',
    # 'client_secret': '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', // old secret
    # 'prompt': 'consent',
    'refresh_token': '0AbUR2VMiSIuXAW_KtTcsjT7zyRSjlzSP-ycNGqUB2N2Gf62Yhayv9JPYPs1WZcsl3kYEKA',
    'refresh_token': '1//0cprxnQ3-72brCgYIARAAGAwSNwF-L9IrRSnHBYt2y5KtYm0GA10M1s8J-R1ExTA-fOyEGsqQcAfbdEfyZhlXB-bUMMQm72UYSLs',
})
# creds = Credentials.from_authorized_user_file(filename='credentials.json')

# Создание клиента для работы с Google Drive API
service = build('drive', 'v3', credentials=creds)

# ID папки на Google Drive
folder_ids = {
    # 'zhurnal_opozdaniy': '1fKXIF6oc0MgKdf_XUGc4hey5GBXsFGF8', # deleted
    'kb_docs': '1SJNSHuIQep7fzHg7OVXzLn0tYY6J-VmR',
    'koordinaciya_shkol': '1tu7-FJIdbcPcDybEvYpIp7bRZTy271b5',
    'schools_coord__arthur': '12uk_ItJa28Jc_fWJ6V4I8tgS5lltYsxJ',
    'potok_2023': '1ySHpXNGm4t9BX8y6REDZmXWCuEsqqExT',
    'reg_materials': '1IrfIbNkhsfLOiwG4OuBWh7CfWvnvAjFB',
    'materials_attest': '1kn7isrUZ-EKxD-iRgX_X-3mI6caH0BO3'
}
g_apps_mime_start_str = 'application/vnd.google-apps.'

# Create a dir
date = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
newdir = f'C:\\mySand\\GDriveBkup\\{date}_gdrive_bkup'
print(f'Creating new dir {newdir}')
os.makedirs(newdir)

def sanitize_filename(filename: str) -> str:
    # Replace all characters that are not letters, digits, or underscores with an underscore
    print(f'Sanitizing {filename}')
    # return re.sub(r'[^\w]+', '_', filename)
    return re.sub(r'[:*?"<>|]', '_', filename)

def download_file(file_id, file_name, file_mime='', file_path=''):
    """Функция для скачивания файла с Google Drive"""
    request = service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        # print(f'Download {int(status.progress() * 100)}.')
        print("Download %d%%." % int(status.progress() * 100))
    file.seek(0)
    with open(os.path.join(newdir, file_path, sanitize_filename(file_name)), 'wb') as f:
        f.write(file.read())

def download_g_apps_file(file_id, file_name, file_mime='', file_path=''):
    ext = ''
    if file_mime == 'application/vnd.google-apps.document':
        request = service.files().export_media(fileId=file_id, mimeType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        ext = 'docx'
    elif file_mime == 'application/vnd.google-apps.spreadsheet':
        request = service.files().export_media(fileId=file_id, mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        ext = 'xlsx'
    elif file_mime == 'application/vnd.google-apps.presentation':
        request = service.files().export_media(fileId=file_id, mimeType = 'application/vnd.openxmlformats-officedocument.presentationml.presentation')
        ext = 'pptx'
    elif file_mime == 'application/vnd.google-apps.photo':
        request = service.files().export_media(fileId=file_id, mimeType = 'image/png')
        ext = 'png'
    elif file_mime == 'application/vnd.google-apps.drawings':
        request = service.files().export_media(fileId=file_id, mimeType = 'application/pdf')
        ext = 'pdf'
    elif file_mime == 'application/vnd.google-apps.script':
        request = service.files().export_media(fileId=file_id, mimeType = 'application/vnd.google-apps.script+json')
        ext = 'json'

    fh = io.FileIO(os.path.join(newdir, file_path, sanitize_filename(file_name) + '.' + ext), 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    fh.close()

def download_folder(folder_id, file_path=''):
    """Функция для скачивания папки с Google Drive"""
    results = service.files().list(q=f"'{folder_id}' in parents", fields="nextPageToken, files(id, name, mimeType)").execute()
    # results = service.files().list(q=f"'1fKXIF6oc0MgKdf_XUGc4hey5GBXsFGF8' in parents", fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])
    for item in items:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            # Если это папка - создаем локальную папку и рекурсивно скачиваем содержимое
            sanitized_folder = sanitize_filename(item['name'])
            newdir_to_recurse = os.path.join(file_path, sanitized_folder)
            os.makedirs(newdir_to_recurse, exist_ok=True)
            download_folder(item['id'], file_path=newdir_to_recurse)
        elif g_apps_mime_start_str in item['mimeType']:
            # Если это файл google apps - скачиваем его
            download_g_apps_file(item['id'], item['name'], file_mime=item['mimeType'], file_path=file_path)
        else:
            # Если это обычный файл - скачиваем его
            download_file(item['id'], item['name'], file_mime=item['mimeType'], file_path=file_path)

# Скачивание папки с Google Drive
try:
    download_folder(folder_ids['koordinaciya_shkol'], newdir)
    # download_folder('1zDlWFl2qirsJc7MKrC57hLm5XqESsbHA', newdir)
except Exception as e:
    logger.error('Main error: ', e)
