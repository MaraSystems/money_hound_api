import base64
import mimetypes
import os
import re
import io
from typing import List, Optional
from uuid import uuid4
from pypdf import PdfReader
from docx import Document
import csv
import pandas as pd

from src.config.config import UPLOAD_PATH, ENV


class Storage():
    def parse_data_url(self, data_url: str):
        match = re.match(r"data:(?P<mime>[\w/-]+);base64,(?P<data>.+)", data_url)
        if not match:
            return None, None
        return match.group("mime"), match.group("data")



    def upload(self, files: List[str], path: str, prefix='file'):
        uploaded = []
        path = os.path.join(f'{UPLOAD_PATH}_{ENV}', path)
        os.makedirs(path, exist_ok=True)

        for file in files:
            mime, b64_data = self.parse_data_url(file)

            if mime and base64:
                decoded = base64.b64decode(b64_data)
                ext = mimetypes.guess_extension(mime) or 'bin'

                filename = f'{prefix}_{uuid4().hex}{ext}'
                filepath = os.path.join(path, filename)

                with open(filepath, 'wb') as f:
                    f.write(decoded)

                uploaded.append(filepath)
                continue

            uploaded.append(file)
        return uploaded
    
    
    def binary_to_text(self, data: bytes, name: str, mime_type: Optional[str] = None):
        """Split binary"""

        try:
            if mime_type == 'application/pdf':
                pdf_reader = PdfReader(io.BytesIO(data))
                text = "\n\n".join(page.extract_text() or ""for page in pdf_reader.pages)
                return text.strip()
            
            elif mime_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
                doc = Document(io.BytesIO(data))
                text = "\n\n".join(p.text or ""for p in doc.paragraphs)
                return text.strip()
            
            elif mime_type == 'text/csv':
                decoded = data.decode('utf-8', errors='ignore')
                reader = csv.reader(io.BytesIO(decoded))
                text = "\n\n".join([', '.join(row) for row in reader])
                return text.strip()
            
            elif mime_type in ["text/plain", "text/markdown"]:
                text = data.decode('utf-8', errors='ignore')
                return text.strip()
            
            elif mime_type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
                try:
                    xls = pd.read_excel(io.BytesIO(data))
                    text = xls.to_csv(index=False)
                    return text.strip()
                except Exception as e:
                    return f"[Excel parse failed: {e}]"
                
            else:
                return f"[Unsuppored file type: {mime_type}]"
            
        except Exception as e:
            return f"[Error parsing {name}: {e}]"