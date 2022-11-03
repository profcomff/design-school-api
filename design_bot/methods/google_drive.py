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


async def create_user_folder(*, first_name: str, middle_name: str, last_name: str) -> str:
    pass


async def upload_text_to_drive(user_folder_id: str, text: str) -> str:
    pass


async def upload_file_to_drive(user_folder_id: str, file_path: str) -> str:
    pass

