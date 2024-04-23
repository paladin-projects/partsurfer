#!/usr/bin/python3

import asyncio
import sys
import argparse

from httpx import AsyncClient
from bs4 import BeautifulSoup
import csv
import re


parser = argparse.ArgumentParser(description='Fetch spare parts details from HPE PartSurfer based on serial, product or part number')
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
url = 'https://partsurfer.hpe.com/Search.aspx'


def parse_serial(bs, n):
    try:
        if n.find(":"):
            parts = bs.find('table', id='ctl00_BodyContentPlaceHolder_radProd').find_all('tr')
            for p in parts:
                print(p.text)
        else:
            parts = bs.find('table', id='ctl00_BodyContentPlaceHolder_gridSpareBOM').find_all('tr', class_=re.compile('RowStyle|AlternateRowStyle'))
            for p in parts:
                part = p.find('span', id=re.compile('ctl\d\d_BodyContentPlaceHolder_gridSpareBOM_ctl\d\d_lblspart\d'))
                desc = p.find('span', id=re.compile('ctl\d\d_BodyContentPlaceHolder_gridSpareBOM_ctl\d\d_lblspartdesc\d'))
                try:
                    csv_writer.writerow([n, part.text, desc.text])
                except:
                    continue
    except AttributeError:
        try:
            parts = bs.find('table', id='ctl00_BodyContentPlaceHolder_radProd').find_all('label')
            nums = []
            for p in parts:
                nums.append(p.text)
            print(f"Several products found for serial {n}:\n{nums}", file=sys.stderr)
            sys.exit(1)
        except AttributeError:
            print(f"No results for serial number: {n}", file=sys.stderr)
            sys.exit(1)


def parse_product(bs, n):
    try:
        parts = bs.find('div', id='ctl00_BodyContentPlaceHolder_dvProdinfo').find_all('tr')
        for p in parts:
            part = p.find('a', id=re.compile('ctl\d\d_BodyContentPlaceHolder_rptRoot_ctl\d\d_gvProGeneral_ctl\d\d_lnkPartno'))
            desc = p.find('span', id=re.compile('ctl\d\d_BodyContentPlaceHolder_rptRoot_ctl\d\d_gvProGeneral_ctl\d\d_lbldesc'))
            try:
                csv_writer.writerow([n, part.text, desc.text])
            except:
                continue
    except AttributeError:
        print(f"No results for product number: {n}", file=sys.stderr)
        sys.exit(1)


def parse_part(bs, n):
    try:
        parts = bs.find('table', id='ctl00_BodyContentPlaceHolder_gvGeneral').find_all('tr', class_=re.compile('RowStyle|AlternateRowStyle'))
        for p in parts:
            part = p.find('span', id=re.compile('ctl\d\d_BodyContentPlaceHolder_gvGeneral_ctl\d\d_lnkPartno'))
            desc = p.find('span', id=re.compile('ctl\d\d_BodyContentPlaceHolder_gvGeneral_ctl\d\d_lblpartdesc\d'))
            try:
                csv_writer.writerow([part.text, desc.text])
            except:
                continue
    except AttributeError:
        print(f"No results for part number: {n}", file=sys.stderr)
        sys.exit(1)


def parse(bs, n):
    if bs.find('div', class_='message error'):
        print('Error for {}'.format(n), file=sys.stderr)
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
        csv_writer.writerow(['Serial', 'Part', 'Description'])
    if args.product:
        csv_writer.writerow(['Product', 'Part', 'Description'])
    if args.part:
        csv_writer.writerow(['Part', 'Description'])


async def fetch_parse(c: AsyncClient, n: str):
    # Если это поиск по серийнику, то формат будет Серийник:Продукт. Таким образом все коды будут искаться без проблем,
    # а серийник будет отделяться от номера продукта для 'первого' поиска
    response = await c.get(url, params={"searchText": n.split(":")[0]})

    if response.status_code != 200:
        print(f"Site is not available, status code: {response.status_code}. Prompt number: {n}", file=sys.stderr)
        sys.exit(1)

    page = BeautifulSoup(response.text, 'lxml')

    if page.find('span', class_=re.compile('ctl00_BodyContentPlaceHolder_lblErrorMsg')):
        print("Internal server error occurred", file=sys.stderr)
        sys.exit(1)

    if page:
        parse(page, n)


async def main():
    print_headers()
    async with AsyncClient(http2=True) as client:
        tasks = []
        for num in args.NUM:
            tasks.append(asyncio.ensure_future(fetch_parse(client, num)))
        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
