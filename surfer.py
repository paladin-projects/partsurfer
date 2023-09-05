
from urllib.request import urlopen
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import pandas as pd
import sys
kk = sys.argv[1]

with urlopen('https://partsurfermobile.ext.hpe.com/', data=urlencode({'SelectedCountryID': '', 'SearchString': kk}).encode('ascii')) as response:
  page = response.read()

soup = BeautifulSoup(page, 'lxml')

if soup.find('div', class_='message error'):
  print('no info')
else:
  try:
    PN = []
    Desc = []
    names = soup.find('div' , id = 'tab2').find_all('a')
    pnd = soup.find('div' , id = 'tab2').find_all('strong')
    for i in names:
      PN.append(i.text)
    for k in pnd:
      if k.text == 'Description: ':
        Desc.append(k.next_sibling)
    df = pd.DataFrame({'Product name':PN, 'Description':Desc})
    df.to_csv('pp.csv')
  except:
    info = soup.find_all('ul', class_='cols2 compare')
    names = soup.find_all('li', id='inner')
    PN = []
    Desc = []
    prod=[]
    for i in names:
      for k in info:
        s = k.find_all('strong')
        for u in s:
          if u.text == 'Part No: ':
            prod.append(i.text)
            PN.append(u.next_sibling)
          elif u.text == 'Description: ':
            Desc.append(u.next_sibling)
    df = pd.DataFrame({'Product name':prod,'Product number':PN,'Description':Desc})
    df.to_csv('pp.csv')
