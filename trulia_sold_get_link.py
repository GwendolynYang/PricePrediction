#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 22:48:15 2019
# rewrite code from ctlu22
# https://github.com/ctlu22/selling_time_predictor
@author: shiningyg
"""

import pandas as pd
import numpy as np

import urllib
import requests
import time
import csv

from datetime import datetime
from bs4 import BeautifulSoup

zipcode = '07041'
soldurl = r'https://www.trulia.com/sold/'+zipcode+r'_zip/SINGLE-FAMILY_HOME_type/'

# set the header as the one not forbidden. 
headers = {'User-Agent': 'Chrome/56.0.2661.102'}
zipstats = requests.session().get(soldurl,headers=headers)

soup =  BeautifulSoup(zipstats.text, 'html.parser')
pagestats = soup.find("h2", class_="h7 typeEmphasize typeLowlight pbs")

searchNum = int(pagestats.text[1:].strip().split(' ')[0])
print(searchNum)

pageNum = searchNum//30 + 1
print(pageNum)

soldlist = []
# loop for each page of search result
for i in range(1, pageNum + 1):
    sess = requests.session()
    pageurl = soldurl+str(i)+ '_p/'
    page = sess.get(pageurl,headers=headers)
    soup2 = BeautifulSoup(page.text, 'html.parser')
    print(pageurl)
    
    # 30 results each page if not last page
    if i!= pageNum:
        soupobject = soup2.find_all("a", class_ = "tileLink")
        #print(len(soupobject))       
        for j in range(0, 30):                       
            addresslink = soupobject[j*2].get("href")
            address = soupobject[j*2].get("alt")
            soldlist.append([address, addresslink, str(zipcode)])
            
        time.sleep(5)
        
    else:
        num_links_lastpage = searchNum - 30*(pageNum-1)
        soupobject = soup2.find_all("a", class_ = "tileLink")
        
        for j in range(0, num_links_lastpage):
            addresslink = soupobject[j*2].get("href")
            address = soupobject[j*2].get("alt")
            soldlist.append([address, addresslink, str(zipcode)])
        time.sleep(5)
# write links to csv
urllist = pd.DataFrame(soldlist, columns = ['address','url','zipcode'])
urllist.to_csv('/Users/shiningyg/Dropbox/InSight/csv/sold_'+ zipcode + '.csv', encoding = 'utf-8', index = None)
print('collected all links from ', zipcode)