from __future__ import print_function
from lxml import html, etree
from savetodrive import *
from apiclient import discovery
import httplib2
import requests
import re
import os

DOWNLOAD_FOLDER = '/Users/tahaderouiche/Downloads/mosaiquefmpodcast/'
MOSAIQUE_URL = 'http://www.mosaiquefm.net/fr/3/podcasts/midi-show'


def get_files_on_mosaique_website(url_website):
    """Get the list of podcasts available on mosaiquefm website
    Args:
        url_website (str): url of the mosaiquefm podcast page
    Returns:
        list: list with with urls, guests, and date
        """
    # load the webpage
    page = requests.get(url_website)
    tree = html.fromstring(page.content)

    # List containing information about podcasts to download
    files = []
    # Find lines containing the podcasts url and guests
    mp3_lines = tree.xpath('//ul[@class="sm2-playlist-bd"]/li')
    for m in mp3_lines:
        line = etree.tostring(m, encoding='utf-8')
        link = re.search('http(.*)mp3', line).group(0)
        guests = re.search(r'<b>(.*): (.*)</b>', line).group(2)
        files.append([link, guests])
    # Find lines containing the date
    date_lines = tree.xpath('//div[@class="infosBar"]/span[@class="date"]')
    i = 0
    for t in date_lines:
        line = etree.tostring(t, encoding='utf-8')
        time = re.search(r'fa-edit"/> (.*) 14:00</span>', line).group(1)
        files[i].append(time)
        i += 1
    return files


def download_podcasts_locally(podcasts_available, podcasts_uploaded, location):
    # Downloading files found if not in drive and not downloaded before
    for item in podcasts_available:
        url = item[0]
        filename = unicode(item[2] + " - " + item[1] + '.mp3', 'utf8')
        if filename not in podcasts_uploaded and not os.path.exists(location + filename):
            print(filename + " will be downloaded")
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                # Downloading the file in chunks of 1KB to avoid reading the content at once into memory
                with open(DOWNLOAD_FOLDER + filename, 'wb') as f:
                    print ('Downloading %s ' % filename)
                    for chunk in r.iter_content(1024):
                        f.write(chunk)


def main():
    # Connect to drive and get list of podcasts uploaded
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    folder_id = create_folder(service)
    podcasts_in_drive = get_files_uploaded(service, folder_id)
    # Get list of podcasts available online
    podcasts_online = get_files_on_mosaique_website(MOSAIQUE_URL)
    # # Download new podcasts locally
    download_podcasts_locally(podcasts_online, podcasts_in_drive, DOWNLOAD_FOLDER)
    # Upload files in Google Drive
    upload_podcasts(service, folder_id, DOWNLOAD_FOLDER)




if __name__ == '__main__':
    main()
