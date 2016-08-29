from lxml import html, etree
import requests
import re

def main():
    page = requests.get('http://www.mosaiquefm.net/fr/3/podcasts/midi-show')
    tree = html.fromstring(page.content)
    l = []
    mp3_lines = tree.xpath('//ul[@class="sm2-playlist-bd"]/li')
    for m in mp3_lines:
        line = etree.tostring(m, encoding='utf-8')
        link = re.search('http(.*)mp3', line).group(0)
        guests = re.search('\<b\>(.*)\<\/b\>', line).group(1)
        l.append([link, guests])

    time_lines = tree.xpath('//div[@class="infosBar"]/span[@class="date"]')
    i = 0
    for t in time_lines:
        line = etree.tostring(t, encoding='utf-8')
        time = re.search('fa-edit\"\/\> (.*)\<\/span\>', line).group(1)
        l[i].append(time)
        i += 1
    for item in l:
         print (item)

if __name__ == '__main__':
    main()





