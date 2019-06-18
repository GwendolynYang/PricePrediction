#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 23:20:36 2019

@author: shiningyg
"""

import pandas as pd
import numpy as np

import requests
import time


from bs4 import BeautifulSoup

zipcode = '07039'
soldurl = r'https://www.trulia.com/sold/'+zipcode+r'_zip/SINGLE-FAMILY_HOME_type/'
print(soldurl)

# set the header as the one not forbidden. 
headers = {'User-Agent': 'Chrome/56.0.2661.102'}
zipstats = requests.session().get(soldurl,headers=headers)
print(zipstats)
soup =  BeautifulSoup(zipstats.text, 'html.parser')
pagestats = soup.find("h2", class_="h7 typeEmphasize typeLowlight pbs")
#print(pagestats)

searchNum = int(pagestats.text[1:].strip().split(' ')[0])
print(searchNum)

# set output constain and report numbers in feature
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
            #print(j)
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
urllist.to_csv('/Users/shiningyg/Dropbox/InSight/csv/sold_'+ zipcode + '.csv', mode='a', encoding = 'utf-8', index = None)
print('collected all links from ', zipcode)

def price_history_trulia(url):    
    time.sleep(5)
    sess = requests.session()
    houseurl = 'https://www.trulia.com' + str(url).strip()

    page = sess.get(houseurl, headers = headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    # get Address
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
            #print(priceHistory[-1])
        
    return priceHistory

dfin = urllist.url

colnames = ['address', 'Date', 'price','event']
dfout = pd.DataFrame(columns = colnames)

outcsvfile = '/Users/shiningyg/Dropbox/InSight/csv/sold_price_history'+zipcode+'.csv'
dfout.to_csv(outcsvfile, encoding = 'utf-8', index = None)
        
count = 0
        
for url in dfin:
    #print url
    count += 1
    
    if count < 96: 
        continue
    print(count)
    
    sold_priceHist = price_history_trulia(url)
    time.sleep(20)
    
    itemdf = pd.DataFrame(sold_priceHist, columns = colnames)
    itemdf.to_csv(outcsvfile, encoding = 'utf-8', mode = 'a', header = False, index = None)
    
print("Total of", count, "properties price history collected.")