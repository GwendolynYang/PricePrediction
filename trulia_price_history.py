#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 22:54:11 2019

# Scrape price history info from each trulia link
# input csv is the output of "trulia_sold_get_links"

@author: shiningyg
"""
import pandas as pd
import numpy as np
import re
from datetime import datetime
import urllib
import requests
import time
from bs4 import BeautifulSoup

# set local zipcode
zipcode = '07041'

# set header for "requests"
headers = {'User-Agent': 'Chrome/56.0.2661.102'}

def price_history_trulia(url):    
    time.sleep(5)
    sess = requests.session()
    houseurl = 'https://www.trulia.com' + str(url).strip()

    page = sess.get(houseurl, headers = headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    # get Address
    Address = []
    obj = soup.find("span", class_ = "Text__TextBase-sc-1cait9d-0 dhOdUy")
    if obj == None:
        addr = np.nan
    else:
        addr = obj.get_text()
    
    # get Price History
    priceHistory = []
    tempHist = []
    
    if soup.find_all('tr') == None:
        priceHistory.append([addr, np.nan, np.nan, np.nan])
    else:
        for tr in soup.find_all('tr'):    
            tempHist.append([td.text for td in tr.find_all('td')])
        for row in tempHist:
            if len(row)!=3:
                continue
            row.insert(0, addr)
            priceHistory.append(row)
            print(priceHistory[-1])
        
    return priceHistory

dfin = pd.read_csv('/Users/shiningyg/Dropbox/InSight/csv/sold_'+ zipcode + '.csv')['url']

colnames = ['address', 'Date', 'price','event']
dfout = pd.DataFrame(columns = colnames)

outcsvfile = '/Users/shiningyg/Dropbox/InSight/csv/sold_price_history'+zipcode+'.csv'
dfout.to_csv(outcsvfile, encoding = 'utf-8', index = None)
        
count = 0
        
for url in dfin:
    #print url
    count += 1
       
    print(count)
    sold_priceHist = price_history_trulia(url)
    
    
    itemdf = pd.DataFrame(sold_priceHist, columns = colnames)

    itemdf.to_csv(outcsvfile, encoding = 'utf-8', mode = 'a', header = False, index = None)
    
print("Total of", count, "properties price history collected.")