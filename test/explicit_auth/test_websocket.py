#coding:utf8

from channels import Channel
from channels.tests import ChannelTestCase,HttpClient 
from isc_auth.models import Account,Application,User,Device
from initdb import init_db
from isc_auth.tools.auth_tools import app_auth_tools
from test.general_tools import receive_all
from isc_auth.tools.auth_tools import app_auth_tools
import base64
import json



class WebSocketTests(ChannelTestCase):

    def init_db_and_get_data(self):
        init_db()
        account = Account.objects.get(account_name='chris_whu')
        user = User.objects.get(account=account,user_name='xrb')
        device = Device.objects.filter(user=user)[0]

        return account,user,device
    ##
    
    def connect_websocket_return_code(self,client,hostname,identifer):
        path = "/api-%s/%s" %(hostname,identifer)
        client.send_and_consume(u'websocket.connect',path=path)
        msgs = receive_all(client)
        return path,msgs
    ##

    def test_connect_succeed(self):
        acc,user,device = self.init_db_and_get_data()
        device.dKey = app_auth_tools.generate_aes_key()
        device.is_activated = True
        device.save()

        client = HttpClient()
        path,msgs = self.connect_websocket_return_code(client,acc.api_hostname,device.identifer)
        #返回一条信息
        self.assertEqual(len(msgs),1)
        msg = msgs[0]
        key = device.dKey
        decode = app_auth_tools.decrypt(key,base64.b64decode(msg)).split('\0')
        self.assertEqual(len(decode[1]),20)
        self.assertEqual(decode[0],app_auth_tools.CONNECTION_SETUP_PREFIX)
        return path,acc,user,device,client,decode[1]
    ##
    
    def test_connect_failed(self):
        acc,user,device = self.init_db_and_get_data()
        device.dKey = app_auth_tools.generate_aes_key()
        device.save()
        client = HttpClient()
        path,msgs = self.connect_websocket_return_code(client,acc.api_hostname,device.identifer)
        self.assertEqual(msgs[0],{'close':True})
    ##
     
    def test_explicit_auth_succeed(self):
        path,acc,user,device,client,random = self.test_connect_succeed()
        random = random[::-1]
        app_code = base64.b64encode(app_auth_tools.encrypt(device.dKey,"%s\0%s" 
            %(app_auth_tools.CONNECTION_REPLY_PREFIX,random)))
        client.send_and_consume(u'websocket.receive',path=path,
            text= app_code)
        client.consume(u"auth_message.receive")
        msgs = receive_all(client)
    
    

        





        
    


        



    


