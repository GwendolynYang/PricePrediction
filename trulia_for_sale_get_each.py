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

def get_forsale_list(zipcode):
    
    #zipcode = '10546'
    forsaleurl = r'https://www.trulia.com/for_sale/'+zipcode+r'_zip/SINGLE-FAMILY_HOME_type/'
    print(forsaleurl)
    
    # set the header as the one not forbidden. 
    headers = {'User-Agent': 'Chrome/56.0.2661.102'}
    zipstats = requests.session().get(forsaleurl,headers=headers)
    print(zipstats)
    soup =  BeautifulSoup(zipstats.text, 'html.parser')
    pagestats = soup.find("h2", class_="h7 typeEmphasize typeLowlight pbs")
    #print(pagestats)
    
    searchNum = int(pagestats.text[1:].strip().split(' ')[0])
    print(searchNum)
    
    # set output constain and report numbers in feature
    pageNum = searchNum//30 + 1
    print(pageNum, 'pages')
    
    forsalelist = []
    # loop for each page of search result
    for i in range(1, pageNum + 1):
    
        sess = requests.session()
        pageurl = forsaleurl+str(i)+ '_p/'
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
                forsalelist.append([address, addresslink, str(zipcode)])
                
            time.sleep(5)
            
        else:
            num_links_lastpage = searchNum - 30*(pageNum-1)
            soupobject = soup2.find_all("a", class_ = "tileLink")
            
            for j in range(0, num_links_lastpage):
                addresslink = soupobject[j*2].get("href")
                address = soupobject[j*2].get("alt")
                forsalelist.append([address, addresslink, str(zipcode)])
            time.sleep(5)
        
    return forsalelist



def price_history_forsale_trulia(url):    
    time.sleep(5)
    sess = requests.session()
    houseurl = 'https://www.trulia.com' + str(url).strip()

    headers = {'User-Agent': 'Chrome/56.0.2661.102'}
    page = sess.get(houseurl, headers = headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    # get Address
    obj = soup.find("span", class_ = "Text__TextBase-sc-1cait9d-0 dhOdUy")
    if obj == None:
        addr = np.nan
    else:
        addr = obj.get_text()
   
    #get city, State, zipcode
    obj2 = soup.find("span", class_ = "HomeSummaryShared__CityStateAddress-vqaylf-0 fyHNRA Text__TextBase-sc-1cait9d-0 hUlhgk")
    if obj2 == None:
        region = np.nan
    else:
        region = obj2.get_text()
    
        
    # get Price History
    priceHistory = []
    tempHist = []
    
    if soup.find_all('tr') == None:
        priceHistory.append([addr, region, np.nan, np.nan, np.nan])
    else:
        for tr in soup.find_all('tr'):    
            tempHist.append([td.text for td in tr.find_all('td')])
        for row in tempHist:
            if len(row)!=3:
                continue
            row.insert(0, region)
            row.insert(0, addr)
            priceHistory.append(row)
            #print(priceHistory[-1])
        
    return priceHistory

   
#zipList  = [ '11021','11020','11030'] #'11024','11023',
zipList = ['07078']#['11040','11530', '11753','11576','11545']#,'11579','11791'] 
for zipcode in zipList:
    forsalelist = get_forsale_list(zipcode)    
    # write links to csv
    urllist = pd.DataFrame(forsalelist, columns = ['address','url','zipcode'])
    urllist.to_csv('../csv/for_sale_'+ zipcode + '.csv', mode='a', encoding = 'utf-8', index = None)
    print('collected all links from ', zipcode)
            
    dfin = urllist.url
    
    colnames = ['address', 'region', 'date', 'price','event']
    dfout = pd.DataFrame(columns = colnames)
    
    outcsvfile = '../csv/for_sale_price_history'+zipcode+'.csv'
    dfout.to_csv(outcsvfile, encoding = 'utf-8', index = None)
            
    count = 0
            
    for url in dfin:
        #print url
        count += 1
        
#        if count <12 : 
#            break
        print(count)
        
        sold_priceHist = price_history_forsale_trulia(url)
        time.sleep(10)
        
        itemdf = pd.DataFrame(sold_priceHist, columns = colnames)
        itemdf.to_csv(outcsvfile, encoding = 'utf-8', mode = 'a', header = False, index = None)
        
    print("Total of", count, "properties price history collected.")
