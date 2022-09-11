import argparse
from urllib.request import urlopen
from urllib.parse import urlencode
from html.parser import HTMLParser
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description='Fetch spare parts details fro HPE Partsurfer based on serial, product or part number')
parser.add_argument('-s', '--serial', nargs='+', help='search for serial number')
args = parser.parse_args()

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        global count
        if tag == 'div' and count > 0:
            count = count + 1
        if tag == 'div' and ('id', 'tab2') in attrs:
            count = 1

    def handle_endtag(self, tag):
        global count
        if tag == 'div' and count > 0:
            count = count - 1

parser = MyHTMLParser()

for serial in args.serial:
    count = 0
    text = []
    with urlopen('https://partsurfermobile.ext.hpe.com/', data=urlencode({'SelectedCountryID': '', 'SearchString': serial}).encode('ascii')) as response:
    #with urlopen('file:index.html.1') as response:
        for line in response:
            line = line.decode().strip()
            if not len(line):
                continue
            parser.feed(str(line))
            if count > 0:
                text.append(line.replace('&','&amp;'))
        text.append('</div>')
    for row in ET.fromstringlist(text).iter('ul'):
        a = row.find('li[1]')
        b = a.find('a')
        if b != None:
            print(b.text, end='\t')
        b = a.find('strong')
        if b != None:
            print(b.tail)
