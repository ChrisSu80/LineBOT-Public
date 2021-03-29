# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 21:37:11 2021

@author: user
"""

def google_creds_as_file():
    #linux
    import json,tempfile
    auth={}    
    temp = tempfile.NamedTemporaryFile()   
    temp.write(json.dumps(auth).encode('utf8'))
    temp.flush()
    return temp


def export(df):
    import pygsheets
    try:       
        creds_file = google_creds_as_file()       
        print(creds_file.name)       
        gc = pygsheets.authorize(service_file=creds_file.name)        
        sht_url='https://docs.google.com/spreadsheets/d/1dHAfN6b55GR_MzwlcVis0Yq1RHDGF-JeNfQefPPKnJA/edit#gid=0'
        sht = gc.open_by_url(sht_url)
        wks = sht[0]
        wks.title = "geocoding"
        wks.clear()
        wks.set_dataframe(df, start = "A1",copy_head=False)    
    except Exception as msg:
        print('pygsheets_problem:',msg)
    return 'https://tinyurl.com/3hxjdu7n'


def get_GC(location):
    import googlemaps
    gmaps_key=googlemaps.Client(key='')
    geocode_result=gmaps_key.geocode(location,language='zh-TW')
    try:
        lat=geocode_result[0]['geometry']['location']['lat']
        lon=geocode_result[0]['geometry']['location']['lng']    
        address=geocode_result[0]['formatted_address']
    except:
        lat=None
        lon=None
        address=None
    return lat,lon,address


def Batch_import():
    import pygsheets
    try:       
        creds_file = google_creds_as_file()       
        # print(creds_file.name)      
        gc = pygsheets.authorize(service_file=creds_file.name)        
        sht_url='https://docs.google.com/spreadsheets/d/10CJZHnDKtuo3UJAKklUx_mKuAzWRzon02HSQyXV_yy4/edit?usp=sharing'      
        sht = gc.open_by_url(sht_url)
        wks = sht[0]        
        df = wks.get_as_df(start='A1', index_colum=0, empty_value='',include_tailing_empty=False) # index 從 1 開始
    except Exception as msg:
        print('pygsheets_problem:',msg)
    return df


def static_map(data):
    url='''
    https://maps.googleapis.com/maps/api/staticmap?
    maptype=roadmap
    &size=600x640
    &zoom=13
    &key*
    '''
    text=''
    for i in data:
        url+='&markers={},{}'.format(str(i[1]),str(i[2]))
        text+=i[0]+'\n'
    return text,url
