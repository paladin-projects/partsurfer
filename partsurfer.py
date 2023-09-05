import argparse
import sys
from urllib.request import urlopen
from urllib.parse import urlencode
from html.parser import HTMLParser
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description='Fetch spare parts details fro HPE Partsurfer based on serial, product or part number', argument_default=argparse.SUPPRESS)
group = parser.add_mutually_exclusive_group()
group.add_argument('-s', '--serial', action='store_true', help='search for serial number(s)')
group.add_argument('-p', '--product', action='store_false', help='search for product number(s)')
group.add_argument('-n', '--part', action='store_false', help='search for part number(s)')
parser.add_argument('NUM', nargs='+', help='number(s) to search for')
args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_usage()
    parser.exit()

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

for serial in args.NUM:
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
