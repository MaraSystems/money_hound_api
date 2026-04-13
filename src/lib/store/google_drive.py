from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.lib.store.storage import binary_to_text 
from src.lib.utils.config import GOOGLE_APPLICATION_CREDENTIALS
from src.lib.utils.logger import get_logger


logger = get_logger('GoogleDrive')

def document_service(self):
    """Create Google Docs API service client.

    Returns:
        Authenticated Google Docs API service instance
    """
    scopes = ['https://www.googleapis.com/auth/documents.readonly']
    creds = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS, scopes=scopes)
    return build('docs', 'v1', credentials=creds, cache_discovery=False)


def service(self):
    """Create Google Drive API service client.

    Returns:
        Authenticated Google Drive API service instance
    """
    scopes = [
        'https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    creds = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS, scopes=scopes)
    return build('drive', 'v3', credentials=creds, cache_discovery=False)


def list_documents(self, folder_id: str) -> list:
    """List all documents in a Google Drive folder.

    Args:
        folder_id: Google Drive folder ID

    Returns:
        List of file metadata dictionaries
    """
    service = service()
    query = f"'{folder_id}' in parents and trashed = false"
    response = service.files().list(q=query, fields='nextPageToken, files(id, name, mimeType, modifiedTime)').execute()
    return response['files']


async def download(self, file_id: str) -> tuple:
    """Download a file from Google Drive.

    Handles Google Docs editor files by exporting them to native
    formats (PDF for Docs/Slides, XLSX for Sheets).

    Args:
        file_id: Google Drive file ID

    Returns:
        Tuple of (text content, file metadata)
    """
    service = service()
    metadata = service.files().get(fileId=file_id, fields='name, mimeType, modifiedTime').execute()
    original_mime_type = metadata['mimeType']

    if original_mime_type == 'application/vnd.google-apps.document':
        request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
        metadata['mimeType'] = 'application/pdf'
    elif original_mime_type == 'application/vnd.google-apps.spreadsheet':
        request = service.files().export_media(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        metadata['mimeType'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif original_mime_type == 'application/vnd.google-apps.presentation':
        request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
        metadata['mimeType'] = 'application/pdf'
    else:
        request = service.files().get_media(fileId=file_id)

    file_stream = io.BytesIO()
    downloader = MediaIoBaseDownload(file_stream, request)

    done = False
    while not done:
        chunk = downloader.next_chunk()
        status, done = chunk
        if status:
            logger.info(f"[Drive Download] {int(status.progress() * 100)}%")

    file_stream.seek(0)
    data = file_stream.read()
    text = binary_to_text(data, metadata['name'], metadata['mimeType'])
    return text, metadata


def download_multiple(self, files: list[str], max_workers: int = 5) -> dict:
    """Download multiple files concurrently using thread pool.

    Args:
        files: List of Google Drive file IDs
        max_workers: Maximum number of concurrent downloads

    Returns:
        Dictionary mapping file IDs to text and metadata
    """
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(download, fid): fid for fid in files}

        for future in as_completed(future_to_file):
            file_id = future_to_file[future]
            try:
                text, metadata = future.result()
                results[file_id] = {'text': text, 'metadata': metadata}
            except Exception as e:
                logger.error(f"Failed to download {file_id}: {e}")
    return results
