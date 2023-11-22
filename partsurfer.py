#!/usr/bin/python3
import sys
import argparse
from urllib.request import urlopen
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import csv

parser = argparse.ArgumentParser(description='Fetch spare parts details fro HPE Partsurfer based on serial, product or part number')
group = parser.add_mutually_exclusive_group()
group.add_argument('-s', '--serial', action='store_true', help='search for serial number(s)')
group.add_argument('-p', '--product', action='store_true', help='search for product number(s)')
group.add_argument('-n', '--part', action='store_true', help='search for part number(s)')
parser.add_argument('NUM', nargs='+', help='number(s) to search for')
parser.add_argument('-o', '--output', help='append output to file')
parser.add_argument('-k', '--skip-headers', action='store_true', help='skip headers (useful for appending to existing file')
args = parser.parse_args()

# print(args)
if len(sys.argv) == 1:
    parser.print_usage()
    parser.exit(1)

if args.output:
    f = open(args.output, 'a', newline='')
else:
    f = sys.stdout

csv_writer = csv.writer(f)

for num in args.NUM:
    with urlopen('https://partsurfermobile.ext.hpe.com/', data=urlencode({'SelectedCountryID': '', 'SearchString': num}).encode('ascii')) as response:
        page = BeautifulSoup(response.read(), 'lxml')
        if page.find('div', class_='message error'):
            print('Error for {}'.format(num), file=sys.stderr)
            continue
        if args.serial:
            parts = page.find('div' , id = 'tab2').find_all('a')
            descs = page.find('div' , id = 'tab2').find_all('strong')
            if not args.skip_headers:
                csv_writer.writerow(['Serial','Part','Description'])
                args.skip_headers = True
            i = len(parts) - 1
            while i >= 0:
                if descs[i].text == 'Description: ':
                    csv_writer.writerow([num, parts[i].text, descs[i].next_sibling.text])
                i = i - 1
        if args.product:
            items = page.find_all('ul' , class_='cols2 compare')
            if not args.skip_headers:
                csv_writer.writerow(['Product','Part','Description'])
                args.skip_headers = True
            r = [num]
            for i in items:
                lines = i.find_all('strong')
                for l in lines:
                    if l.text == 'Part No: ':
                        r.append(l.next_sibling)
                    if l.text == 'Description: ':
                        r.append(l.next_sibling)
                        csv_writer.writerow(r)
                        r = [num]
                        break
        if args.part:
            items = page.find_all('div', class_='section')[1].find_all('div', class_='section')
            if not args.skip_headers:
                csv_writer.writerow(['Part','Description'])
                args.skip_headers = True
            r = [num]
            for i in items:
                lines = i.find_all('strong')
                for l in lines:
                    if l.text == 'Part No: ':
                        r.append(l.next_sibling)
                    if l.text == 'Description: ':
                        r.append(l.next_sibling)
                        csv_writer.writerow(r)
                        r = [num]
                        break
