#coding:utf-8

from channels import route
from channels.routing import null_consumer
from .consumers import ws_connect,ws_message,ws_disconnect,auth_message_handle,send_account_info_handle
from explicit_auth.consumers import explicit_auth_message_handle
from tools.auth_tools.app_auth_tools import EXPLICIT_REPLY_COMMAND,REQUIRE_INFO_COMMAND

websocket_path = r"^/api-(?P<api_hostname>[a-zA-Z0-9]+)/(?P<identifer>[a-zA-Z0-9]{20})$"


general_routing = [
    route("websocket.connect",ws_connect,path=websocket_path),
    route("websocket.receive",ws_message,path=websocket_path),
    route("websocket.disconnect",ws_disconnect,path=websocket_path), 
]

custom_routing = [
    #websocket连接建立认证
    route("auth_message.receive",auth_message_handle,path=websocket_path),
    #显示认证
    route("message.receive",explicit_auth_message_handle,path=websocket_path,action=EXPLICIT_REPLY_COMMAND),
    route("message.receive",send_account_info_handle,path=websocket_path,action=REQUIRE_INFO_COMMAND),
    #其余关闭
    route("message.receive",null_consumer),
]


