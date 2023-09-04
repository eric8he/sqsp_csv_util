from __future__ import print_function

import os.path

import csv
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError


PRODUCT_CSV_COLUMNS = ["Product ID [Non Editable]","Variant ID [Non Editable]","Product Type [Non Editable]","Product Page","Product URL","Title","Description","SKU","Option Name 1","Option Value 1","Option Name 2","Option Value 2","Option Name 3","Option Value 3","Option Name 4","Option Value 4","Option Name 5","Option Value 5","Option Name 6","Option Value 6","Price","Sale Price","On Sale","Stock","Categories","Tags","Weight","Length","Width","Height","Visible","Hosted Image URLs"]

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']


creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

# Build the Drive API client
drive_service = build('drive', 'v3', credentials=creds)

# Find the Processed Batches and To Be Processed folders
parent_name = 'API Products'

parent_results = drive_service.files().list(
    q=f"name='{parent_name}' and mimeType='application/vnd.google-apps.folder'",
    spaces='drive',
).execute()

# Check if the api parent folder was found
if 'files' in parent_results:
    parent_folder = parent_results['files'][0]
    parent_id = parent_folder['id']
    print(f"found parent folder: {parent_id}")
else:
    print("parent folder not found.")
    exit()

pb_name = "Processed Batches"
tbp_name = "To Be Processed"

pb_results = drive_service.files().list(
    q=f"'{parent_id}' in parents and name='{pb_name}' and mimeType='application/vnd.google-apps.folder'",
    spaces='drive',
).execute()

# Check if the processed batches folder was found
if 'files' in pb_results:
    pb_folder = pb_results['files'][0]
    print(f"found pb folder: {pb_folder['id']}")
else:
    print("pb folder not found.")
    exit()

tbp_results = drive_service.files().list(
    q=f"'{parent_id}' in parents and name='{tbp_name}' and mimeType='application/vnd.google-apps.folder'",
    spaces='drive',
).execute()

# Check if the to be processed folder was found
if 'files' in tbp_results:
    tbp_folder = tbp_results['files'][0]
    print(f"found tbp folder: {tbp_folder['id']}")
else:
    print("tbp folder not found.")
    exit()

# Get list of folders in to be processed folder
tbp_children = drive_service.files().list(
    q=f"'{pb_folder['id']}' in parents",
    spaces='drive',
).execute()

# Check if there are any folders in the to be processed folder
if 'files' in tbp_children:
    tbp_child_folders = tbp_children['files']
    print(f"found {len(tbp_child_folders)} items to be processed")
else:
    print("no folders to be processed.")
    exit()


print(tbp_child_folders)

request = drive_service.files().export_media(fileId=tbp_child_folders[0]['id'], mimeType='text/plain')
file = io.BytesIO()
downloader = MediaIoBaseDownload(file, request)
done = False
while done is False:
    status, done = downloader.next_chunk()

print(file.getvalue().decode('utf-8'))