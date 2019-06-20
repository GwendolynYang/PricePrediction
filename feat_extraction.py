#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 00:51:27 2019

@author: shiningyg
"""

# Feature engineering to feed model

import numpy as np
import pandas as pd
import time
import datetime as dt


def get_data(filename):
    
    rawdata = pd.read_csv(filename)

    # clean date and price format
    rawdata['price'] = rawdata['price'].replace('[\$,]', '', regex=True).astype(np.int64)
    if 'Date' in rawdata.columns:
        rawdata['Date'] = pd.to_datetime(rawdata['Date'])
    if 'date' in rawdata.columns:
        rawdata['Date'] = pd.to_datetime(rawdata['date'])

    # drop unuseful event, which contributes no price change
    data = rawdata.drop(rawdata[rawdata.event == 'Pending'].index).reset_index(drop=True)
    data = data.drop(data[data.event == 'Posting Removed'].index ).reset_index(drop=True)
    data = data.drop(data[data.event == 'Pending to Active Status'].index ).reset_index(drop=True)
    
    return data

def get_house_feat_mix(house, feat, median):
    
    #print(house)
    
    # get each feature for feat_mix
    label = get_label(house)
    feat.append(label)

    days, discount = get_days(house)
    feat.append(days) 
    feat.append(discount)

    feat.append(house.price[0])
    
    ratio2median = round(house.price[0]/median, 2)
    feat.append(ratio2median)

    mList, mSold = get_eventMonth(house)
    feat.append(mList)
    feat.append(mSold)

    nList, nPC, nSold = get_eventCount(house)
    feat.append(nList)
    feat.append(nPC)
    feat.append(nSold)
    
    return feat


def get_label(house):
    return 1 if (house.event[0] == 'Sold') else 0

def get_days(house):
    days, disc = 0, 100
    if house.event[0] == 'Sold':
        if house.event.size == 1 or house.event[1] == 'Sold': # no recent listing info. 1 or 2 sold records only.
            return 0, 100       
    for i in range(house.event.size):
        if house.event[i] == 'Listed For Sale':
            if i == 0: # cases of currently listing with out any further updates
                diff = pd.datetime.now() - house.Date[i]
                days = diff.days
                disc = 100               
            else: # cases of sold -> listing and priceReduce -> listing               
                diff = house.Date[0] - house.Date[i]
                disc = round(100 - (house.price[i] - house.price[0])* 100/ house.price[i], 1)# i.e. 90, means 90% of listing price
                days = diff.days
            break  # consider the latest sale event
            
    return days, disc
                

def get_eventMonth(house):
    mList, mSold = 0, 0
    for i in range(house.event.size):
        if house.event[i] == 'Listed For Sale':
            mList = house.Date[i].month
            break
        elif house.event[i] == 'Sold':
            mSold = house.Date[i].month    
    return mList, mSold


def get_eventCount(house):
    yearcut = list(house['Date'].dt.year > 1989)
    nList, nPC, nSold = 0, 0, 0
    for i in range(house.event.size):
        if house.event[i] == 'Listed For Sale':
            if yearcut[i]: 
                nList += 1
        elif house.event[i] == 'Price Change':
            if yearcut[i]:
                nPC += 1
        elif house.event[i] == 'Sold':
            if yearcut[i]:
                nSold += 1
    return nList, nPC, nSold


# compose feat_mix:: feature from both sold and currently listing data
col_mix = ['address', 'sold', 'days', 'discount', 'price', 'Ration2Median', 
           'MonthList', 'MonthSold', 'NumList', 'NumPC', 'NumSold']

# get local median home value data
path = '../csv/MedianHomeValue.csv'
mhv = pd.read_csv(path)
mhv_dict = dict(zip(mhv.zipcode.astype(str), mhv.MedianHomeValue))

for zipcode in mhv_dict:
    
    # this should read from a dictionary
    medianHV = mhv_dict[zipcode] # median house value of this area
    
    #correct zipcode error 
    if len(zipcode) == 4:
        zipcode = '0' + zipcode
        print(zipcode)
    
    #define input filename
    inpath = '../csv/sold_price_history' #'./csv/for_sale_price_history' # 
    filename = inpath+ zipcode + '.csv'
    
    data = get_data(filename)
     
    #define output file
    outpath = '../csv/feat_sold'
    featfile = outpath + zipcode + '.csv'    
    

    # get each address and process each house data
    addr_list = list(data.address.unique())
    feat_mix = []
    for addr in addr_list:

        house = data[data.address == addr].reset_index(drop=True)
        feat = get_house_feat_mix(house, [addr], medianHV)
        #print(feat)
        feat_mix.append(feat)

    obj = pd.DataFrame(feat_mix, columns = col_mix)

    obj.to_csv(featfile, encoding = 'utf-8')