import argparse
from urllib.request import urlopen
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description='Fetch spare parts details fro HPE Partsurfer based on serial, product or part number')
parser.add_argument('-s', '--serial', help='search for serial number')
args = parser.parse_args()

flag = 0
text = []
boundaries = {'serial': '<table cellspacing="0" cellpadding="2" rules="all" border="1" id="ctl00_BodyContentPlaceHolder_gridSpareBOM" style="background-color:White;font-size:12px;width:660px;border-collapse:collapse;table-layout:fixed">',
              'product': '<table class="rtf_table">'}

with urlopen('https://partsurfer.hpe.com/Search.aspx?searchText=' + args.serial) as response:
    for line in response:
        line = line.decode().strip()
        if not len(line):
            continue
        if line == boundaries['serial']:
            flag = 1
        if line == '</table>' and flag:
            text.append(line)
            flag = 0
            break
        if flag:
            text.append(line.replace('&nbsp;', ' '))

tree = ET.fromstringlist(text)
ET.indent(tree)
ET.dump(tree)
