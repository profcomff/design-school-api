import random
import string

import aiofiles
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
from design_bot.settings import get_settings

settings = get_settings()

SCOPES = ['https://www.googleapis.com/auth/drive.file', "https://www.googleapis.com/auth/drive.resource"]

gauth = GoogleAuth()
gauth.auth_method = 'service'
gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(settings.GOOGLE_JSON_PATH, SCOPES)
drive = GoogleDrive(gauth)


async def create_user_folder(*, first_name: str, middle_name: str, last_name: str, social_web_id: int) -> str:
    random_string = ''.join(random.choice(string.ascii_letters) for _ in range(12))
    newFolder = drive.CreateFile({'title': f"{first_name}_{middle_name}_{last_name}_{social_web_id}_{random_string}",
                                  "parents": [{"kind": "drive#fileLink", "id": \
                                      settings.PARENT_FOLDER_ID}], "mimeType": "application/vnd.google-apps.folder"})
    newFolder.Upload()
    return newFolder["id"]


async def upload_text_to_drive(*, first_name: str, middle_name: str, last_name: str, social_web_id: str,
                               user_folder_id: str, content: str, lesson_number: int) -> str:
    random_string = ''.join(random.choice(string.ascii_letters) for _ in range(12))
    file = drive.CreateFile({
        'title': f'{first_name}_{middle_name}_{last_name}_{social_web_id}_{lesson_number}_{random_string}.txt',
        "parents": [user_folder_id]})  # Create GoogleDriveFile instance with title 'Hello.txt'.
    file.SetContentString(content)  # Set content of the file from given string.
    file.Upload()
    return file["webViewLink"]


async def upload_file_to_drive(user_folder_id: str, file_path: str) -> str:
    async with aiofiles.open(file_path):
        pass
