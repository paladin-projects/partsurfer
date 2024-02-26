#!/usr/bin/python3

import asyncio
import sys
import argparse
from httpx import AsyncClient
from bs4 import BeautifulSoup
import csv
import re

parser = argparse.ArgumentParser(description='Fetch spare parts details fro HPE Partsurfer based on serial, product or part number')
group = parser.add_mutually_exclusive_group()
group.add_argument('-s', '--serial', action='store_true', help='search for serial number(s)')
group.add_argument('-p', '--product', action='store_true', help='search for product number(s)')
group.add_argument('-n', '--part', action='store_true', help='search for part number(s)')
parser.add_argument('NUM', nargs='+', help='number(s) to search for')
parser.add_argument('-o', '--output', help='append output to file')
parser.add_argument('-k', '--skip-headers', action='store_true', help='skip headers (useful for appending to existing file')

args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_usage()
    parser.exit(1)

if args.output:
    f = open(args.output, 'a', newline='')
else:
    f = sys.stdout

csv_writer = csv.writer(f)

def parse_serial(bs, n):
    parts = bs.find('table', id='ctl00_BodyContentPlaceHolder_gridSpareBOM').find_all('tr', class_=re.compile('RowStyle|AlternateRowStyle'))
    for i in range(len(parts)):
        part = parts[i].find('span', id=re.compile('ctl\d\d_BodyContentPlaceHolder_gridSpareBOM_ctl\d\d_lblspart\d'))
        desc = parts[i].find('span', id=re.compile('ctl\d\d_BodyContentPlaceHolder_gridSpareBOM_ctl\d\d_lblspartdesc\d'))
        try:
            csv_writer.writerow([n, part.text, desc.text])
        except:
            continue


def parse_product(bs, n):
    parts = bs.find('div', id='ctl00_BodyContentPlaceHolder_dvProdinfo').find_all('tr')
    for i in range(len(parts)):
        part = parts[i].find('a', id=re.compile('ctl\d\d_BodyContentPlaceHolder_rptRoot_ctl\d\d_gvProGeneral_ctl\d\d_lnkPartno'))
        desc = parts[i].find('span', id=re.compile('ctl\d\d_BodyContentPlaceHolder_rptRoot_ctl\d\d_gvProGeneral_ctl\d\d_lbldesc'))
        try:
            csv_writer.writerow([n, part.text, desc.text])
        except:
            continue

def parse_part(bs, n):
    parts = bs.find('table', id='ctl00_BodyContentPlaceHolder_gvGeneral').find_all('tr', class_=re.compile('RowStyle|AlternateRowStyle'))
    for i in range(len(parts)):
        part = parts[i].find('span', id=re.compile('ctl\d\d_BodyContentPlaceHolder_gvGeneral_ctl\d\d_lnkPartno'))
        desc = parts[i].find('span', id=re.compile('ctl\d\d_BodyContentPlaceHolder_gvGeneral_ctl\d\d_lblpartdesc\d'))
        try:
            csv_writer.writerow([part.text, desc.text])
        except:
            continue

async def parse(bs, n):
    if bs.find('div', class_='message error'):
        print('Error for {}'.format(num), file=sys.stderr)
        return
    if args.serial:
        parse_serial(bs, n)
    if args.product:
        parse_product(bs, n)
    if args.part:
        parse_part(bs, n)

def print_headers():
    if args.skip_headers:
        return
    if args.serial:
        csv_writer.writerow(['Serial', 'Part','Description'])
    if args.product:
        csv_writer.writerow(['Product', 'Part','Description'])
    if args.part:
        csv_writer.writerow(['Part','Description'])

async def main():
    print_headers()
    async with AsyncClient(http2=True) as client:
        for num in args.NUM:
            params = {"searchText": num}
            response = await client.get('https://partsurfer.hpe.com/Search.aspx', params=params)
            page = BeautifulSoup(response.text, 'lxml')
            if page:
                await parse(page, num)

if __name__ == "__main__":
    asyncio.run(main())
