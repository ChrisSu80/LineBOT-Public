# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 22:13:56 2021

@author: user
"""
class DB:
    
    host = ''  #ip
    port = 3306  #埠號
    user = ''   #資料庫使用者名稱
    password = ''    #資料庫密碼
    db = ''    #資料庫名
    charset = 'utf8mb4'  #編碼

       
    def get_df():
        import pymysql
        import pandas as pd   
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  #建立遊標物件
            sql_entry = 'select Location,Address,Latitude,Longitude,Cluster from quests ORDER BY Cluster'
            cursor.execute(sql_entry)   
            data = cursor.fetchall()            
            columns=("Location","Address","Latitude","Longitude","Cluster")
            df=pd.DataFrame(data=data,columns=columns)
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  #關掉遊標
            db.close()  #關掉資料庫連線
        return df


    def insert_data(date_time,location,address,lat,lng,editor):
        import pymysql   
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  
            sql_entry = "INSERT IGNORE INTO quests(Date_time,Location,Address,Latitude,Longitude,Editor) VALUES ('%s','%s','%s','%s','%s','%s')" % (date_time,location,address,lat,lng,editor)
            cursor.execute(sql_entry)
            db.commit()                       
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return '{},{}已匯入'.format(lat,lng)


    def truncate(table):
        import pymysql   
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  
            sql_entry = "truncate table %s"%(table)
            cursor.execute(sql_entry)
            db.commit()                       
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return "truncate table {}".format(table) 


    def insert_cluster(Location_Cluster):
        import pymysql   
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  
            args=(Location_Cluster)
            sql_entry = "REPLACE INTO calculation(location,cluster) VALUES (%s,%s)" 
            cursor.executemany(sql_entry, args)
            db.commit()                       
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close() 
        return "分組完成"

    
    def append():
        import pymysql   
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  
            sql_entry = "UPDATE quests INNER JOIN calculation ON quests.Location=calculation.Location SET quests.Cluster=calculation.Cluster WHERE quests.Location=calculation.Location;"
            cursor.execute(sql_entry)
            db.commit()                       
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return "表格更新"
    
    
    def del_data(Location):
        import pymysql   
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  
            sql_entry = "DELETE FROM quests WHERE Location = '%s';"%(Location)
            cursor.execute(sql_entry)
            db.commit()                       
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return '{}已刪除'.format(Location)


    def mission_completed(Location,Labor='self',Completion='2020-03-07 12:00:00'):
        import pymysql   
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()             
            sql_list=["INSERT INTO record (Date_time,Location,Address,Latitude,Longitude,Cluster,Editor) SELECT Date_time,Location,Address,Latitude,Longitude,Cluster,Editor FROM quests where Location = '%s';"%(Location),
                      "UPDATE `record` SET Labor = '%s' , Completion = '%s' WHERE Location = '%s';"%(Labor,Completion,Location),
                      "DELETE FROM quests WHERE Location = '%s';"%(Location)]            
            for sql in sql_list:  
                cursor.execute(sql)
                db.commit()    
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return '{}已完成'.format(Location)
        
    
    def select_nearby(lat_d,lat_u,lon_d,lon_u):
        import pymysql
        import pandas as pd   
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  
            sql_entry = 'SELECT Location,Latitude,Longitude,Cluster FROM quests WHERE Latitude BETWEEN {} AND {} and Longitude BETWEEN {} AND {}'.format(lat_d,lat_u,lon_d,lon_u)
            cursor.execute(sql_entry)   
            data = cursor.fetchall()                      
            df=pd.DataFrame(data=data,columns=('Location','Latitude','Longitude','Cluster'))
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return df
    

    def group_members(cluster):
        import pymysql
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  
            sql_entry = "SELECT Location,Latitude,Longitude FROM quests where Cluster = '%s'"%(cluster)
            cursor.execute(sql_entry)   
            data = cursor.fetchall()                                
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return data
        

    def update_info(Information,User_Name):
        import pymysql
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  
            sql_entry = "update profile SET Information='%s' where User_Name ='%s';"%(Information,User_Name)
            cursor.execute(sql_entry)   
            db.commit() 
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return '信息已更新'  

    
    def update_image(link,user_id):
        import pymysql
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  
            sql_entry = "update profile SET Image='%s' where User_ID ='%s';"%(link,user_id)
            cursor.execute(sql_entry)   
            db.commit() 
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return '圖片已更新'


    def registered(User_ID,User_Name):
        import pymysql
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  
            sql_entry = "INSERT ignore INTO `profile`(User_ID,User_Name,Permissions,Information,Image) VALUES ('%s','%s','%s','%s','%s')" % (User_ID,User_Name,'user','我就爛','https://i.imgur.com/cCwlVBP.png')
            cursor.execute(sql_entry)   
            db.commit()                                          
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return '{},完成報到'.format(User_Name)


    def select_profile(User_ID):
        import pymysql
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  
            sql_entry = "select * from `profile` where User_ID ='%s';" % (User_ID)
            cursor.execute(sql_entry) 
            data = cursor.fetchall()                                
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return data


    
    def time_sheet(user_id):
        import pymysql
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  
            sql_entry = "SELECT * FROM timesheet where user_id='%s' order by  clock_in DESC LIMIT 0 , 1; " % (user_id)
            cursor.execute(sql_entry)  
            data = cursor.fetchall()   
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return data

    def clock_in(user_id,time_is):    
        import pymysql
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  
            sql_entry = "INSERT INTO timesheet(user_id,clock_in) VALUES ('%s','%s')" % (user_id,time_is)
            cursor.execute(sql_entry)   
            db.commit()                                           
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return '完成上班打卡'
    
    def clock_out(user_id,time_is):
        import pymysql
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  
            sql_entry = "UPDATE timesheet SET clock_out= '%s' WHERE user_id = '%s' and clock_out IS NULL;" % (time_is,user_id)
            cursor.execute(sql_entry)   
            db.commit()                                    
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return '完成下班打卡'



    def working_hours():
        import pymysql
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  
            sql_entry = "SELECT user_id,clock_in,clock_out FROM timesheet"
            cursor.execute(sql_entry)  
            data = cursor.fetchall()   
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return data
    

    def profile_dic():
        import pymysql
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor()  
            sql_entry = "select User_ID,User_Name from `profile` "
            cursor.execute(sql_entry) 
            data = cursor.fetchall()
            dic={}
            for i in data:
                dic.update({i[0]:i[1]})                                                
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return dic    


    def select_record():
        import pymysql
        try:
            db = pymysql.connect(host=DB.host, port=DB.port, user=DB.user, password=DB.password, db=DB.db, charset=DB.charset)
            cursor = db.cursor() 
            sql_entry = "SELECT Labor,PK FROM record"
            cursor.execute(sql_entry)  
            data = cursor.fetchall()   
        except Exception as msg:
            print(msg)
        finally:
            cursor.close()  
            db.close()  
        return data






