from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
import io

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/drive']

# Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
flow = InstalledAppFlow.from_client_secrets_file('credentials2.json', SCOPES)
creds = flow.run_local_server(port=0)

# Call the Drive v3 API
service = build('drive', 'v3', credentials=creds)

# Replace the file_id with id of file you want to access
file_id = '1jY5BqsXvMIztXnCuc6EXV2utE0ua02HUpMvOAQlSqbU' 
# request = service.files().get_media(fileId=file_id) # can't download GDocs formats, need to convert b4 downloading
request = service.files().export_media(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') # conv to XLSX

# Replace 'my_download_file' with the path where you want to save your file
fh = io.FileIO('my_downloaded_file', 'wb')
downloader = MediaIoBaseDownload(fh, request)
done = False
while done is False:
    status, done = downloader.next_chunk()
    print("Download %d%%." % int(status.progress() * 100))

fh.close()