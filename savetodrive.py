from __future__ import print_function

import httplib2
import os
from googleapiclient.http import MediaFileUpload
# import logging

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Mosaique Podcast'


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
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """This will upload a file to Google Drive
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    file_metadata = {
        'name': 'blogger.png'
    }
    media = MediaFileUpload('blogger.png',
                            mimetype='image/png',
                            resumable=True)
    request = service.files().create(body=file_metadata, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print ("Uploaded %d%%." % int(status.progress() * 100))
    print ("Upload Complete!")
    print ("File id: %s" % response.get('id'))


if __name__ == '__main__':
    main()