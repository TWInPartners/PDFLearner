import json
import os
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
import io

class GoogleDriveSync:
    def __init__(self, credentials):
        self.credentials = credentials
        self.service = build('drive', 'v3', credentials=credentials)
        self.folder_name = "PDF_Flashcards"
        self.folder_id = None
        self._ensure_folder_exists()
    
    def _ensure_folder_exists(self):
        """Create or find the flashcards folder in Google Drive"""
        try:
            # Search for existing folder
            results = self.service.files().list(
                q=f"name='{self.folder_name}' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                self.folder_id = folders[0]['id']
            else:
                # Create new folder
                folder_metadata = {
                    'name': self.folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.service.files().create(body=folder_metadata, fields='id').execute()
                self.folder_id = folder.get('id')
                
        except Exception as e:
            raise Exception(f"Error setting up Google Drive folder: {str(e)}")
    
    def save_data(self, data):
        """Save flashcard data to Google Drive"""
        try:
            filename = f"flashcards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Convert data to JSON
            json_data = json.dumps(data, indent=2)
            file_stream = io.BytesIO(json_data.encode('utf-8'))
            
            # Upload file metadata
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id]
            }
            
            # Create media upload object
            media = MediaIoBaseUpload(
                file_stream,
                mimetype='application/json',
                resumable=True
            )
            
            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
            
        except Exception as e:
            raise Exception(f"Error saving data to Google Drive: {str(e)}")
    
    def load_data(self):
        """Load the most recent flashcard data from Google Drive"""
        try:
            # Search for JSON files in the flashcards folder
            results = self.service.files().list(
                q=f"parents='{self.folder_id}' and name contains 'flashcards_' and mimeType='application/json'",
                orderBy="createdTime desc",
                fields="files(id, name, createdTime)"
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                return None
            
            # Get the most recent file
            latest_file = files[0]
            
            # Download file content
            request = self.service.files().get_media(fileId=latest_file['id'])
            file_stream = io.BytesIO()
            downloader = MediaIoBaseDownload(file_stream, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            # Parse JSON data
            file_stream.seek(0)
            data = json.loads(file_stream.getvalue().decode('utf-8'))
            
            return data
            
        except Exception as e:
            raise Exception(f"Error loading data from Google Drive: {str(e)}")
    
    def list_files(self):
        """List all flashcard files in Google Drive"""
        try:
            results = self.service.files().list(
                q=f"parents='{self.folder_id}' and name contains 'flashcards_'",
                orderBy="createdTime desc",
                fields="files(id, name, createdTime, size)"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            raise Exception(f"Error listing files: {str(e)}")
    
    def delete_file(self, file_id):
        """Delete a file from Google Drive"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
            
        except Exception as e:
            raise Exception(f"Error deleting file: {str(e)}")
    
    def get_storage_info(self):
        """Get storage information"""
        try:
            about = self.service.about().get(fields="storageQuota").execute()
            quota = about.get('storageQuota', {})
            
            return {
                'limit': int(quota.get('limit', 0)),
                'usage': int(quota.get('usage', 0)),
                'usage_in_drive': int(quota.get('usageInDrive', 0))
            }
            
        except Exception as e:
            return None
