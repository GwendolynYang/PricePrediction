"""
change trulia_sold_get_each

add function get_sqft, get_lotsize, get_description, 
(try get_bed, get_bath)

with full address save to another csv together, seperate with price history

@author: shiningyg
"""

import pandas as pd
import numpy as np
import re

import requests
import time

from bs4 import BeautifulSoup

def get_into_url(url):
    
    time.sleep(5)
    
    sess = requests.session()
    
    houseurl = 'https://www.trulia.com' + str(url).strip()
    headers = {'User-Agent': 'Chrome/56.0.2661.102'}
    page = sess.get(houseurl, headers = headers)
    
    print(houseurl)
    print(page)
    
    soup = BeautifulSoup(page.text, 'html.parser')
    
    return soup

def get_price_history(soup):      
    
    addr = get_address(soup)
    city = get_city(soup)
    
    # collect all Price History
    priceHistory = []
    tempHist = []
    
    if soup.find_all('tr') == None:
        priceHistory.append([addr, city, np.nan, np.nan, np.nan])
    else:
        for tr in soup.find_all('tr'):    
            tempHist.append([td.text for td in tr.find_all('td')])
        for row in tempHist:
            if len(row)!=3:
                continue
            row.insert(0, city)
            row.insert(0, addr)
            priceHistory.append(row)
            #print(priceHistory[-1])
        
    return priceHistory

def get_address(soup):
    
    # get Address
    obj = soup.find("span", class_ = "Text__TextBase-sc-1cait9d-0 dhOdUy")
    if obj == None:
        addr = np.nan
    else:
        addr = obj.get_text()    
    return addr

def get_city(soup): 
    #get city, State, zipcode
    obj = soup.find("span", class_ = "HomeSummaryShared__CityStateAddress-vqaylf-0 fyHNRA Text__TextBase-sc-1cait9d-0 hUlhgk")
    if obj == None:
        city = np.nan
    else:
        city = obj.get_text()
    return city

def get_sqft(soup):
    block = soup.find("div", class_ = "Grid__GridContainer-sc-144isrp-1 lputZN")   
    obj = block.find("div", class_ ="MediaBlock__MediaContent-skmvlj-1 dCsAgE")
#     print(obj.text)
    
    if obj.text.strip().split(' ')[-1] == 'sqft':
        sqft_str = obj.text.strip().split(' ')[0]
        sqft = sqft_str.replace(',', '')
#         print(sqft)
        
        return int(sqft)
    else:
        print('some thing wrong with \'sqft\'. ')
        return 0

def get_lotsize(soup):
    
    objlist = soup.find_all('li', class_ ='FeatureList__FeatureListItem-gaheyh-0 cEspiV')
    
    if objlist == None:
        return 0
    else:
        for obj in objlist:
            items = obj.text.strip().split(' ')
            if items[0:2] == ['Lot', 'Size:']:
                if items[-1] == 'sqft':
                    lotsize = float(items[2].replace(',', ''))
                    
                if items[-1] == 'acres':
                    lotsize = float(items[2]) * 43560
#                 print(lotsize)
                return lotsize

 
    #TODO
def get_description(soup):
    
    obj = soup.find('div', class_ = 'StyledSectionContainer__Container-hjriq0-0 hhmXfQ')
    description = obj.find('p').text
#     print(description)
    
    return description

def get_extended_features(soup):
    
    #priceHistory = get_price_history(soup)
    
    address = get_address(soup)
    city = get_city(soup)
    
    sqft = get_sqft(soup)
    lotsize = get_lotsize(soup)
    description = get_description(soup)
    
    
    row = [address, city, sqft, lotsize, description]
    return(row)
    
    
    
'''
###############################################
# debug parsing with local html
    
page = './html/16 Fairfield Ter, Short Hills, NJ 07078 - Single-Family Home - 47 Photos _ Trulia.html'
headers = {'User-Agent': 'Chrome/56.0.2661.102'}
with open(page) as fp:
    soup = BeautifulSoup(fp, 'html.parser')

feat = get_extended_features(soup)
###############################################

'''


   
#zipList  = [ '11021','11020','11030'] #'11024','11023',
#zipList = ['11545']#['11040','11530', '11753','11576','11545']#,'11579','11791'] 
        
zipList = ['07078']

for zipcode in zipList:
            
    dfin = pd.read_csv('../csv/urllists/sold_' + zipcode + '.csv')['url']
    
#     pricecol = ['address', 'region', 'date', 'price','event']
#     priceout = pd.DataFrame(columns = pricecol)    
#     pricecsvfile = './csv/extend_features/sold_'+zipcode+'.csv'
#     priceout.to_csv(pricecsvfile, encoding = 'utf-8', index = None)
            
    extdcol = ['address', 'region', 'sqft', 'lot size','description']
    extdout = pd.DataFrame(columns = extdcol)        
    extdcsvfile = '../csv/extend_features/sold_extd_'+zipcode+'.csv'
    extdout.to_csv(extdcsvfile, encoding = 'utf-8',  index = None)
        
    count = 0
    sold_priceHist = [] 
    sold_extd_feat = []
    for url in dfin:
        #print url
        count += 1
        
#        if count <49 : 
#            continue
        print(count)
        
        soup = get_into_url(url)       
        
#        sold_priceHist = get_price_history(soup)
        sold_extd_feat = []
        sold_extd_feat.append( get_extended_features(soup))
      
        time.sleep(10)
        
#         pricedf = pd.DataFrame(sold_priceHist, columns = pricecol)
#         pricedf.to_csv(pricecsvfile, encoding = 'utf-8', mode = 'a', header = False, index = None)
        
        extddf = pd.DataFrame(sold_extd_feat, columns = extdcol)
        extddf.to_csv(extdcsvfile, encoding = 'utf-8', mode = 'a', header = False, index = None)
        
    print("Total of", count, "properties price history collected.")