#coding:utf-8
from channels import Group,Channel
from channels.sessions import channel_session
from django.core.cache import cache

import json
from tools.auth_tools import app_auth_tools
from tools.uniform_tools import *
from .models import Device
from django.db.models import Empty


   
@channel_session
def ws_connect(message,api_hostname,identifer):
    message.reply_channel.send({'accept':True})

    #检查cache和数据库
    try:
        key = cache.get("device-%s-%s_key" %(identifer,api_hostname),None) or Device.objects.get(identifer=identifer)
    except Device.DoesNotExist:
        #未开始绑定，且不存在该设备
        message.reply_channel.send({"close":True})
        return
    else:
        #若未开始绑定
        if isinstance(key,Device):
            #若设备未激活,关闭连接
            if not key.is_activated:
                message.reply_channel.send({"close":True})
                return
            else:
                key = key.dKey
 
    random_number,code = app_auth_tools.gen_b64_random_and_code(key,app_auth_tools.CONNECTION_SETUP_PREFIX)

    message.channel_session["key"] = key
    message.channel_session["auth"] = False
    message.channel_session["setup_random"] = random_number

    message.reply_channel.send({'text':code})


@channel_session
def ws_message(message,api_hostname,identifer):
    #若已经过认证（已建立合法通道）
    if message.channel_session['auth']:
        multiplex(message,"message.receive")
    else:
        multiplex_auth(message,"auth_message.receive")


@channel_session
def ws_disconnect(message,api_hostname,identifer):
    Group("device-%s-%s" %(identifer,api_hostname)).discard(message.reply_channel)


def not_find_action(message,api_hostname,identifer):
    pass



@channel_session
def auth_message_handle(message,api_hostname,identifer):
    '''
    用于检测APP回传的加密信息，建立合法通道
    '''
    #test
    message.channel_session['auth'] = True
    message.reply_channel.send({"text":"Auth Passed.The connection established"})
    Group("device-%s-%s" %(identifer,api_hostname)).add(message.reply_channel)
    # key = message.channel_session['key']
    # info = message.content["text"]
    # random = message.channel_session['setup_random']
    # try:
    #     prefix, = app_auth_tools.decrypt_and_validate_info(info,key,random,app_auth_tools.CONNECTION_REPLY_PREFIX)
    # except Exception,e:
    #     message.reply_channel.send({"close":True})
    #     return
    # else:
    #     #认证通过,置session位，并将其加入Group
    #     message.channel_session['auth'] = True
    #     message.reply_channel.send({"text":"Auth Passed.The connection established"})
    #     Group("device-%s-%s" %(identifer,api_hostname)).add(message.reply_channel)


    

        
        