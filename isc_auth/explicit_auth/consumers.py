#coding:utf-8

from channels.sessions import channel_session
from django.core.cache import cache
from isc_auth.tools.auth_tools import app_auth_tools

@channel_session
def explicit_auth_message_handle(message,api_hostname,identifer):
    '''
    处理APP的显示认证回传信息
    '''
    random = cache.get("device-%s-%s_explicit_random" %(identifer,api_hostname),None)
    if random is None:
        message.reply_channel.send({"text":"{'info':'The explicit auth is timeout'}"})
    try:
        prefix, = app_auth_tools.validate_info(message.content["text"]["info"],random)
    except Exception,e:
        raise e
        message.reply_channel.send({"close":True})
    else:
        if prefix == app_auth_tools.EXPLICIT_SUCCEED_PREFIX:
            cache.set("device-%s-%s_auth" %(identifer,api_hostname),True,30)
        elif prefix == app_auth_tools.EXPLICIT_DENIED_PREFIX:
            cache.set("device-%s-%s_auth" %(identifer,api_hostname),False,30)