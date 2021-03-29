# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 22:24:39 2021

@author: user
"""

def Timestamp_Datetime(Timestamp):
    import time
    struct_time = time.localtime(Timestamp/1000) 
    timeString = time.strftime("%Y-%m-%d %H:%M:%S", struct_time) 
    return timeString


def openweathermap(lat,lon):
    import requests
    import json
    url='http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid=****&units=metric'.format(lat,lon)
    HEADERS={'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
    weather=requests.get(url,headers=HEADERS)
    json=json.loads(weather.text)
    icon=json['weather'][0]['icon']
    return 'https://openweathermap.org/img/wn/{}@2x.png'.format(icon)


def geo_distance(lat1, lon1, lat2, lon2):
    '''
    origin = (48.1372, 11.5756)  # Munich
    destination = (52.5186, 13.4083)  # Berlin
    round(distance(origin, destination), 1)
    504.2

    Parameters
    ----------
    lat1 : TYPE
        DESCRIPTION.
    lon1 : TYPE
        DESCRIPTION.
    lat2 : TYPE
        DESCRIPTION.
    lon2 : TYPE
        DESCRIPTION.

    Returns
    -------
    d : TYPE
        DESCRIPTION.

    '''   
    import math
    radius = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return d


def sch(list_Coordinate,max_dis=None,k=None):
    import scipy.cluster.hierarchy as sch
    import pandas as pd    
    dis=sch.linkage(list_Coordinate,metric='euclidean',method='ward')    
    if max_dis!=None:
        clusters_dis=sch.fcluster(dis,max_dis,criterion='distance')
        return clusters_dis
    elif k!=None:        
        clusters_k=sch.fcluster(dis,k,criterion='maxclust')
        df=pd.DataFrame(list_Coordinate,columns=("Latitude","Longitude"))    
        df['centers']=clusters_k
        df["Latitude"]=pd.to_numeric(df["Latitude"])
        df["Longitude"]=pd.to_numeric(df["Longitude"])        
        centers=df.groupby('centers').mean().values.tolist() 
        #FLOAT
        return centers


def Grouping_merge(g1,g2):
    if g2=='':
        return str(g1)
    else:
        return str(g1)+'-'+str(g2)


def clustering(list_Coordinate):
    import pandas as pd
    #1. noise removal
    Grouping_1st=sch(list_Coordinate,max_dis=0.25)#27km    
    df_Coordinate=pd.DataFrame(list_Coordinate,columns=("Latitude","Longitude"))
    df_Coordinate['Grouping_1st']=Grouping_1st
    df_Coordinate['Grouping_2nd']=""   
    z=df_Coordinate.groupby('Grouping_1st').size()
    for i in range(len(z.values)):
        if z.values[i] >10:
            condition=df_Coordinate['Grouping_1st']==z.index[i]
            df_groupby=df_Coordinate[condition].copy()
            #2. find centers
            n=((z.values[i])-1)//10+1
            list_group=df_groupby[["Latitude","Longitude"]].values.tolist()
            centers=sch(list_group,k=n)
            #3.hierarchical clustering (limit)
            C=to_decimal(centers)
            P=df_groupby.values.tolist()            
            df_geo_dis=pd.DataFrame()
            for column in range(len(P)):
                for row in range(len(C)):
                    df_geo_dis.loc[column,row]=geo_distance(P[column][0],P[column][1],C[row][0],C[row][1])         
            df_cluster=pd.DataFrame(columns=['Grouping_2nd'])
            col=df_geo_dis.columns.tolist()
            dic={k:0 for k in col}
            while df_geo_dis.index.size>0:    
                r,c=df_geo_dis[col].stack().idxmin()
                df_cluster.loc[r,'Grouping_2nd']=c    
                df_geo_dis=df_geo_dis.drop([r],axis=0)
                dic[c]+=1
                if dic[c]==11:
                    col.remove(c)            
            df_cluster.index=df_groupby.index.tolist()
            df_Coordinate.update(df_cluster)
    df_Coordinate['Grouping_result'] = df_Coordinate.apply(lambda row: Grouping_merge(row['Grouping_1st'], row['Grouping_2nd']), axis=1)
    return df_Coordinate['Grouping_result'].values.tolist()


def nearest(df,latitude,longitude):
    from decimal import Decimal
    lat=Decimal(str(latitude))
    lon=Decimal(str(longitude))
    if df.size != 0:
        df['distance'] = df.apply(lambda row: geo_distance(row['Latitude'], row['Longitude'],lat, lon), axis=1)
        result=df.sort_values('distance').head(1)
        address=result.iloc[0,0]
        latitude=result.iloc[0,1]
        longitude=result.iloc[0,2]
        cluster=result.iloc[0,3]
        cluster=r'({})'.format(cluster)
        if result.iloc[0,4]<10:
            return '你最靠近',address,latitude,longitude,cluster  
        else:
            return '你附近沒有任務',None,None,None,None
    else:
        return '你附近沒有任務',None,None,None,None


def to_decimal(list_centers):
    from decimal import Decimal
    decimal_centers=[]
    for i in list_centers:
        lat=Decimal(str(i[0]))
        lng=Decimal(str(i[1]))
        decimal_centers.append([lat,lng])
    return decimal_centers


def select_range(lat_loc,lon_loc):
    from decimal import Decimal
    lat_u=Decimal(str(lat_loc))+Decimal('0.25')
    lat_d=Decimal(str(lat_loc))-Decimal('0.25')
    lon_u=Decimal(str(lon_loc))+Decimal('0.25')
    lon_d=Decimal(str(lon_loc))-Decimal('0.25')    
    return lat_d,lat_u,lon_d,lon_u


def reurl(original_url):
    import requests
    import json    
    original_url=original_url.replace('\n','').replace(' ','')
    url="https://api.reurl.cc/shorten/"
    HEADERS={'Content-Type': 'application/json',
             'reurl-api-key': '****'}
    DATA={ "url" : original_url, "utm_source" : "FB_AD" }
    response=requests.post(url,headers=HEADERS,json=DATA)
    json=json.loads(response.text)
    short_url=json["short_url"]
    return short_url


def imgur(message_content,timestamp):    
    import pyimgur
    import os
    CLIENT_ID = "****"
    im = pyimgur.Imgur(CLIENT_ID)
    title = "{} Upload".format(timestamp)
    filename='{}.jpg'.format(timestamp)
    with open(filename, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)        
    uploaded_image = im.upload_image(filename, title=title)
    os.remove(filename)     
    return uploaded_image.link