from __future__ import print_function
import os
from googleapiclient.http import MediaFileUpload


import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Mosaique Podcast'
DOWNLOAD_FOLDER = '/Users/tahaderouiche/Downloads/mosaiquefmpodcast/'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~/Work/Python/mosaiquepodcast/')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def create_folder(service):
    listfolders = service.files().list(q="mimeType='application/vnd.google-apps.folder'"
                                         "and name='Mosaique Podcasts'and trashed=false").execute().get('files', [])
    if listfolders:
        return listfolders[0].get('id')
    else:
        file_metadata = {
            'name': 'Mosaique Podcasts',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        return service.files().create(body=file_metadata, fields='id').execute().get('id')


def get_files_uploaded(service, folder_id):
    l = []
    uploaded_files_set = service.files().list(q="mimeType='audio/mp3' and '"+folder_id+"' in parents and "
                                                "trashed=false").execute().get('files', [])
    for uf in uploaded_files_set:
        l.append(uf.get('name'))
    return l


def upload_podcasts(service, podcasts_folder_id, local_folder):
    """This will upload all files to Google Drive
    """
    for filename in os.listdir(local_folder):
        if filename.endswith(".mp3"):
            print (local_folder+filename)
            file_metadata = {
                'name': filename,
                'parents': [podcasts_folder_id]
            }
            media = MediaFileUpload(local_folder+filename,
                                    mimetype='audio/mp3',
                                    resumable=True)
            request = service.files().create(body=file_metadata, media_body=media)
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print ("Uploaded %d%%." % int(status.progress() * 100))
            print ("Upload Complete!")
            os.remove(local_folder+filename)
