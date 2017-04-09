#coding:utf-8

from channels.sessions import session_for_reply_channel
from channels.asgi import get_channel_layer
from channels import Channel
import json
import random

def createRandomFields(size):
    choice = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789'
    ret = []
    for i in xrange(size):
        ret.append(random.choice(choice))
    return ''.join(ret)


def del_chanell_session(message,*sessions):
    for session in sessions:
        if session in message.channel_session:
            del message.channel_session[session]


def get_session_from_group(group_name,session=None):
    channel_list = get_channel_layer().group_channels(group_name).keys()
    sessions = session_for_reply_channel(channel_list[0])
    if session is not None:
        sessions = sessions.get(session,None)
    return sessions

def get_session_from_channels(channels_list,session=None):
    channel_list = channels_list.keys()
    sessions = session_for_reply_channel(channel_list[0])
    if session is not None:
        sessions = sessions.get(session,None)
    return sessions


def multiplex_auth(message,channel):
    payload = {}
    payload['reply_channel'] = message.content['reply_channel']
    payload['path'] = message.content['path']
    payload['text'] = message.content['text']
    Channel(channel).send(payload)


def multiplex(message,channel):
    try:
        content = json.loads(message.content['text'])
    except:
        message.reply_channel.send({"text":"Your data format should be json"})
        message.reply_channel_send({"close":True})
        return

    action = content.get("action","")
    payload = {}
    payload['reply_channel'] = message.content['reply_channel']
    payload['path'] = message.content['path']
    #content为python字典
    payload['text'] = content
    payload['action'] = action

    Channel(channel).send(payload)

