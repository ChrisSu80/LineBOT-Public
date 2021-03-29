# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 21:46:02 2021

@author: user
"""


def simulator(user_image,user_name,user_info,date_time):
    
    
    from linebot.models.flex_message import (
        BubbleContainer, ImageComponent, BoxComponent,
        TextComponent, ButtonComponent, SeparatorComponent
        )
    from linebot.models.actions import PostbackAction,URIAction
    
    
    bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url=user_image,
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
                action=URIAction(uri='https://reurl.cc/5oVV4M', label='label')
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    # title
                    TextComponent(text=user_name, weight='bold', size='xl'),
                    # review
                    
                    # info
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Info',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text=user_info,
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5
                                    )
                                ],
                            ),
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Time',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text=date_time,
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5,
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='sm',
                contents=[
                    # separator
                    SeparatorComponent(),
                    # websiteAction
                    ButtonComponent(
                        style='primary',
                        height='sm',
                        action=PostbackAction(label='CLOCK IN', data='clock_in')
                    ),
                    ButtonComponent(
                        style='primary',
                        height='sm',
                        action=PostbackAction(label='CLOCK OUT', data='clock_out')
                    )                    
                ]
            ),
        )
  
    return bubble
    
