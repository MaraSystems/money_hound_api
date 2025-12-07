from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.config.config import GOOGLE_APPLICATION_CREDENTIALS
from src.lib.store.storage import Storage
from src.lib.utils.logger import get_logger


class GoogleDrive():
    storage = Storage()
    logger = get_logger('GoogleDrive')

    def document_service(self):
        scopes = ['https://www.googleapis.com/auth/documents.readonly']
        creds = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS, scopes=scopes)
        return build('docs', 'v1', credentials=creds, cache_discovery=False)


    def service(self):
        scopes = [
            'https://www.googleapis.com/auth/drive.metadata.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        creds = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS, scopes=scopes)
        return build('drive', 'v3', credentials=creds, cache_discovery=False)
    

    def list_documents(self, folder_id: str):
        service = self.service()
        query = f"'{folder_id}' in parents and trashed = false"
        response = service.files().list(q=query, fields='nextPageToken, files(id, name, mimeType, modifiedTime)').execute()
        return response['files']
    

    def download(self, file_id: str):
        service = self.service()
        metadata = service.files().get(fileId=file_id, fields='name, mimeType, modifiedTime').execute()

        request = service.files().get_media(fileId=file_id)
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        
        done = False
        while not done:
            chunk = downloader.next_chunk()
            status, done = chunk
            if status:
                self.logger.info(f"[Drive Download] {int(status.progress() * 100)}%")

        file_stream.seek(0)
        data = file_stream.read()
        text = self.storage.binary_to_text(data, metadata['name'], metadata['mimeType'])
        return text, metadata
    

    def download_multiple(self, files: list[str], max_workers=5):
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(self.download, fid): fid for fid in files}

            for future in as_completed(future_to_file):
                file_id = future_to_file[future]
                try:
                    text, metadata = future.result()
                    results[file_id] = {'text': text, 'metadata': metadata}
                except Exception as e:
                    self.logger.error(f"Failed to download {file_id}: {e}")
        return results