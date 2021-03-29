# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 10:39:29 2021

@author: user
"""

def diagram_link(dic,time_sheet,record,timestamp):    
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import os
    import pyimgur      
    
    df=pd.DataFrame(time_sheet,columns=('user','clock_in','clock_out'))
    df['diff']=df['clock_out']-df['clock_in']
    df['diff']=df['diff'].map(lambda x: x.total_seconds())
    df['user']=df['user'].map(lambda x: dic[x])
    seconds=df[['user','diff']].groupby('user').sum().values
    seconds=np.array(seconds).ravel()    
    
    df2=pd.DataFrame(record,columns=('user','pk'))
    df2['user']=df2['user'].map(lambda x: dic[x])    
    pieces=df2.groupby('user').size().values
    
    xtick=df2.groupby('user').size().index.values
    y=pieces/seconds*3600
    plt.rcParams['font.sans-serif'] = ['SimHei']
    my_cmap = plt.get_cmap("winter")
    rescale = lambda y: (y - np.min(y)) / (np.max(y) - np.min(y))
    plt.bar(xtick,y,color=my_cmap(rescale(y)),width=0.5)
    plt.ylabel('Pieces per Hour')
    filename='diagram_{}.jpg'.format(timestamp)
    plt.savefig(filename)    
    
    CLIENT_ID = ""
    im = pyimgur.Imgur(CLIENT_ID)
    uploaded_image = im.upload_image(filename, title='bar chart_{}'.format(timestamp))
    os.remove(filename)
    return uploaded_image.link

