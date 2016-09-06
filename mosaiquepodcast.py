from lxml import html, etree
import requests
import re
import os

DOWNLOAD_FOLDER = '/Users/tahaderouiche/Downloads/mosaiquefmpodcast/'
MOSAIQUE_URL = 'http://www.mosaiquefm.net/fr/3/podcasts/midi-show'


def main():
    # load the webpage
    page = requests.get(MOSAIQUE_URL)
    tree = html.fromstring(page.content)

    # List containing information about podcasts to download
    list_files = []
    # Find lines containing the podcasts url and guests
    mp3_lines = tree.xpath('//ul[@class="sm2-playlist-bd"]/li')
    for m in mp3_lines:
        line = etree.tostring(m, encoding='utf-8')
        link = re.search('http(.*)mp3', line).group(0)
        guests = re.search(r'<b>(.*): (.*)</b>', line).group(2)
        list_files.append([link, guests])
    # Find lines containing the date
    date_lines = tree.xpath('//div[@class="infosBar"]/span[@class="date"]')
    i = 0
    for t in date_lines:
        line = etree.tostring(t, encoding='utf-8')
        time = re.search(r'fa-edit"/> (.*) 14:00</span>', line).group(1)
        list_files[i].append(time)
        i += 1

    # Downloading files found in the list_files if they are not found
    for item in list_files:
        url = item[0]
        filename = item[2] + " - " + item[1] + '.mp3'
        if not os.path.exists(DOWNLOAD_FOLDER + filename):
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                # Downloading the file in chunks of 1KB to avoid reading the content at once into memory
                with open(DOWNLOAD_FOLDER + filename, 'wb') as f:
                    print ('Downloading ' + ' ' + filename)
                    for chunk in r.iter_content(1024):
                        f.write(chunk)


if __name__ == '__main__':
    main()
