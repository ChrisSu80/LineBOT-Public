# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 21:00:38 2021

@author: user
"""

from __future__ import unicode_literals
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import ( MessageEvent, TextMessage, TextSendMessage,
                            LocationAction, LocationMessage, LocationSendMessage,
                            QuickReply, QuickReplyButton, URIAction,
                            ImageSendMessage, ImageMessage, FlexSendMessage,
                            PostbackEvent )
    
from My_Module import Google_API,My_SQL,Methods,Flex_Message,chart


app = Flask(__name__)

# LINE 聊天機器人的基本資料
Channel_access_token='****'
Channel_secret='****'
line_bot_api = LineBotApi(Channel_access_token)
handler = WebhookHandler(Channel_secret)



def access_right(User_ID):    
    access=False
    data=My_SQL.DB.select_profile(User_ID)
    if data:
        if data[0][2]=='admin':
            access=True
    return access



def get_cluster(event):
    if event.message.text == "cluster":
        try:
            reply = '權限不足'
            if access_right(event.source.user_id):
                df=My_SQL.DB.get_df()
                list_Coordinate=df[["Latitude","Longitude"]].values.tolist()
                clusters=Methods.clustering(list_Coordinate)
                df["Cluster"]=clusters
                reply=My_SQL.DB.insert_cluster(df[["Location","Cluster"]].values.tolist())
                My_SQL.DB.append()                                                   
                My_SQL.DB.truncate('calculation') 
            line_bot_api.reply_message(event.reply_token,TextSendMessage(reply)) 
        except Exception as msg:
            print(msg)
        return True
    else:
        return False  


def get_report(event):
    if event.message.text == "report":
        try:
            df=My_SQL.DB.get_df()
            report_url=Google_API.export(df)
            line_bot_api.reply_message(event.reply_token,TextSendMessage(report_url))                                    
        except Exception as msg:
            print(msg)
        return True
    else:
        return False

    
def insert_record(event):    
    if '@' in event.message.text:       
        try:
            timestamp = event.timestamp
            date_time = Methods.Timestamp_Datetime(timestamp)  
            location = event.message.text.strip('@')
            lat,lng,address = Google_API.get_GC(location)
            editor = event.source.user_id
            if lat !=None:
                reply = My_SQL.DB.insert_data(date_time,location,address,lat,lng,editor)
            else:
                reply = '請輸入正確地標或地址'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(reply))
        except Exception as msg:
            print(msg)
        return True
    else:
        return False

    
def batch_record(event):    
    if event.message.text == 'batch':
        try:
            reply = '權限不足'
            if access_right(event.source.user_id):
                timestamp = event.timestamp
                date_time = Methods.Timestamp_Datetime(timestamp)  
                editor = event.source.user_id
                df=Google_API.Batch_import()
                c=0
                for location in df.values.tolist():
                    location=location[0]
                    lat,lng,address = Google_API.get_GC(location)            
                    if lat !=None:
                        My_SQL.DB.insert_data(date_time,location,address,lat,lng,editor)
                        c+=1
                reply = '成功匯入{}筆資料'.format(c)
            line_bot_api.reply_message(event.reply_token,TextSendMessage(reply))
        except Exception as msg:
            print(msg)
        return True
    else:
        return False


def delete_record(event):    
    if 'del' in event.message.text:       
        try:
            reply = '權限不足'
            if access_right(event.source.user_id):                
                Location = event.message.text.strip('del')
                reply = My_SQL.DB.del_data(Location)            
            line_bot_api.reply_message(event.reply_token,TextSendMessage(reply))
        except Exception as msg:
            print(msg)
        return True
    else:
        return False

    
def completed_record(event):    
    if '#' in event.message.text:       
        try:                       
            timestamp = event.timestamp
            Completion = Methods.Timestamp_Datetime(timestamp)
            Labor = event.source.user_id
            Location = event.message.text.strip('#')
            access=clocked(Labor,Completion)
            if access:
                reply = My_SQL.DB.mission_completed(Location,Labor,Completion)
            else:
                reply = '先去打卡喔!'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(reply))
        except Exception as msg:
            print(msg)
        return True
    else:
        return False


def GPS(event):
    if event.message.text == "GPS":
        try:
            line_bot_api.reply_message(
                event.reply_token,TextSendMessage(
                    text='你在哪裡?',quick_reply=QuickReply(
                        items=[QuickReplyButton(action=LocationAction(label="定位"))]
                        )))                   
        except Exception as msg:
            print(msg)
        return True
    else:
        return False


def group(event):
    if "group" in event.message.text:
        try:
            group_name = event.message.text.strip('group')
            data=My_SQL.DB.group_members(group_name)
            if len(data)!=0:
                Text,Url=Google_API.static_map(data)  
                Url=Methods.reurl(Url)
            else:
                Text='Not Exists'
                Url='https://reurl.cc/2b7k7E'
            line_bot_api.reply_message(
                event.reply_token,TextSendMessage(
                    text=Text,quick_reply=QuickReply(
                        items=[QuickReplyButton(action=URIAction(label="Static Map",uri=Url))]
                        )))                   
        except Exception as msg:
            print(msg)
        return True
    else:
        return False


def sign_up(event):    
    if '報到' in event.message.text:       
        try:
            User_Name = event.message.text.strip('報到')
            User_ID = event.source.user_id
            data=My_SQL.DB.select_profile(User_ID)
            if data:
                reply='註冊過囉'
            else:
                reply=My_SQL.DB.registered(User_ID,User_Name)
            line_bot_api.reply_message(event.reply_token,TextSendMessage(reply))
        except Exception as msg:
            print(msg)
        return True
    else:
        return False


def clock(event):
    if event.message.text == '打卡':        
        try:
            user_id = event.source.user_id
            timestamp = event.timestamp
            date_time = Methods.Timestamp_Datetime(timestamp)
            data=My_SQL.DB.select_profile(user_id)            
            
            if data:                
                user_name=data[0][1]
                user_info=data[0][3]
                user_image=data[0][4]   
                                            
                contents = Flex_Message.simulator(user_image,user_name,user_info,date_time)
                                                
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text = '說明文字',
                        contents = contents
                        )
                    )                           
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage('你是誰??先去報到'))                   
        except Exception as msg:
            print(msg)
        return True
    else:
        return False


def update_profile(event):
    if 'INFO' and ':' in event.message.text:
        try:
            reply = '權限不足'
            if access_right(event.source.user_id):
                TEXT = event.message.text.strip('INFO').split(':')
                User_Name = TEXT[0]
                Information = TEXT[1]
                reply=My_SQL.DB.update_info(Information,User_Name)
            line_bot_api.reply_message(event.reply_token,TextSendMessage(reply))
        except Exception as msg:
            print(msg)
        return True
    else:
        return False


def kpi_diagram(event):
    if event.message.text == 'KPI':
        try:
            if access_right(event.source.user_id):                
                dic=My_SQL.DB.profile_dic()
                time_sheet=My_SQL.DB.working_hours()
                record=My_SQL.DB.select_record()
                diagram_url=chart.diagram_link(dic,time_sheet,record,event.timestamp)
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(
                        original_content_url=diagram_url,
                        preview_image_url=diagram_url
                        )
                    )
            else:
                line_bot_api.reply_message(
                    event.reply_token,TextSendMessage('權限不足')
                    )       
        except Exception as msg:
            print(msg)
        return True
    else:
        return False
    

def introduce(event):
    introducting='''
        <使用者功能>
        報到 : '用戶名'報到
        更新大頭貼 : 傳送照片
        上下班打卡 : 打卡        
        最近的任務與天氣 : GPS        
        分組結果 : report
        分布圖 : group'組別'
        新增任務 : @'地址'
        完成任務 : #'地址'
        '''
    introducting2='''
        <管理員功能>
        刪除任務 : del'地址'
        批次匯入 : batch
        https://reurl.cc/qmoEoE
        進行分組 : cluster
        編輯信息 : INFO'用戶名':'信息'
        KPI圖表 : KPI
        '''
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=introducting)
    )
    user_id = event.source.user_id
    if access_right(user_id):
        line_bot_api.push_message(user_id,TextSendMessage(text=introducting2))
    
    return True



def clock_in(user_id,time_is):
    try:
        log=My_SQL.DB.time_sheet(user_id)
        if log:
            if log[0][2]:
                reply=My_SQL.DB.clock_in(user_id,time_is)
            else:
                reply='打過卡了喔!'
        else:
            My_SQL.DB.clock_in(user_id,time_is)
            reply='第一天上班加油喔!'
    except Exception as msg:
        print(msg)
    return reply
        
    
def clock_out(user_id,time_is):
    try:
        log=My_SQL.DB.time_sheet(user_id)
        if log:
            if log[0][2]:
                reply='無上班打卡紀錄'
            else:
                reply=My_SQL.DB.clock_out(user_id,time_is)
        else:
            reply='無紀錄'
    except Exception as msg:
        print(msg)
    return reply


def clocked(user_id,time_is):
    try:
        log=My_SQL.DB.time_sheet(user_id)
        if log:
            if log[0][2]:
                reply=False
            else:
                reply=True
        else:
            reply=False
    except Exception as msg:
        print(msg)
    return reply


##############################################################################


# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def reply_text_message(event):
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        #官方
        reply = False
        
        if not reply:
            reply = sign_up(event)
        if not reply:
            reply = clock(event)
        if not reply:
            reply = update_profile(event)
        if not reply:
            reply = group(event)
        if not reply:
            reply = get_report(event)
        if not reply:
            reply = get_cluster(event)     
        if not reply:
            reply = insert_record(event)  
        if not reply:
            reply = batch_record(event)
        if not reply:
            reply = delete_record(event)
        if not reply:
            reply = completed_record(event)
        if not reply:
            reply = GPS(event) 
        if not reply:
            reply = kpi_diagram(event)        
        if not reply:
            reply = introduce(event)
            

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    #weathermap
    latitude=event.message.latitude
    longitude=event.message.longitude
    img_url=Methods.openweathermap(latitude,longitude)        
    line_bot_api.reply_message(
        event.reply_token,
            ImageSendMessage(
                original_content_url=img_url,
                preview_image_url=img_url))                
    #nearby
    user_id=event.source.user_id 
    lat_d,lat_u,lon_d,lon_u=Methods.select_range(latitude,longitude)
    df=My_SQL.DB.select_nearby(lat_d,lat_u,lon_d,lon_u)    
    Title,Address,Latitude,Longitude,Cluster=Methods.nearest(df,latitude,longitude)
    if Address != None:
        line_bot_api.push_message(user_id,LocationSendMessage(
            title=Title+Cluster, address=Address,latitude=float(Latitude),longitude=float(Longitude)))
    else:
        line_bot_api.push_message(user_id,TextSendMessage(text=Title))
    

@handler.add(MessageEvent, message=ImageMessage)
def upload_image_message(event):
    user_id=event.source.user_id 
    timestamp = event.timestamp
    message_content = line_bot_api.get_message_content(event.message.id)
    try:
        link=Methods.imgur(message_content,timestamp)
        reply=My_SQL.DB.update_image(link,user_id)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(reply))   
    except Exception as msg:
        print(msg)


@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    timestamp = event.timestamp
    time_is = Methods.Timestamp_Datetime(timestamp)
    
    if event.postback.data == 'clock_in':
        reply=clock_in(user_id,time_is)
          
    elif event.postback.data == 'clock_out':
        reply=clock_out(user_id,time_is)
        
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=reply)
        )





if __name__ == "__main__":
    app.run()