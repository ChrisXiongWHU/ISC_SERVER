import requests
import base64
import time
import hashlib
import json


class SMS_Call_Tool(object):
    url = 'https://api.ucpaas.com/{SoftVersion}/Accounts/{accountSid}/{function}/{operation}?sig={SigParameter}'
    soft_version = '2014-06-30'
    account_sid = '99cf6324d1625cf434ef4a9b893bbcdc'
    message_function = 'Messages'
    call_function = 'Calls'
    message_operation = 'templateSMS'
    call_operation = 'voiceCode'
    token = '37da64eea931655922d0bb474d52edb2'
    authorization = "{id}:{time}"
    sig = "{id}{token}{time}"
    app_id = '4e89b79fee3c440f92ec84607b5a3468'
    templateId = '40166'
    

    def __get_general_aug(self,action_type):
        t = time.strftime("%Y%m%d%H%M%S",time.localtime(time.time()))
        sig = SMS_Call_Tool.sig.format(id=SMS_Call_Tool.account_sid,token=SMS_Call_Tool.token,time=t)
        md5 = hashlib.md5()
        md5.update(sig)
        sig = md5.hexdigest().upper()
        function = ''
        operation = ''
        if action_type == 'sms':
            function = SMS_Call_Tool.message_function
            operation = SMS_Call_Tool.message_operation
        elif action_type == 'call':
            function = SMS_Call_Tool.call_function
            operation = SMS_Call_Tool.call_operation
        else:
            raise TypeError('No such action Type')
   
        url = SMS_Call_Tool.url.format(SoftVersion=SMS_Call_Tool.soft_version,accountSid=SMS_Call_Tool.account_sid,
        function=function,operation=operation,SigParameter=sig)
        
        authorization = SMS_Call_Tool.authorization.format(id=SMS_Call_Tool.account_sid,time=t)
        authorization_64 = base64.b64encode(authorization)
        headers = {
            'Accept':'application/json',
            'Content-Type':'application/json;charset=utf-8',
            'Authorization':authorization_64,
        }
        return url,headers
    
    def __call(self,phone_number,auth_code):
        url,headers = self.__get_general_aug('call')
        data = json.dumps({
            'voiceCode':{
                'appId':SMS_Call_Tool.app_id,
                'verifyCode':auth_code,
                'playTimes':'3',
                'to':phone_number
            }
        })

        resp = requests.post(url=url,data=data,headers=headers)
        return resp


    def __send_sms(self,phone_number,auth_code,wait_time):
        
        url,headers = self.__get_general_aug('sms')
        data = json.dumps({
            'templateSMS':{
                'appId':SMS_Call_Tool.app_id,
                'templateId':SMS_Call_Tool.templateId,
                'to':phone_number,
                'param':"%s,%d" %(auth_code,wait_time)
            }
        })
        resp = requests.post(url=url,data=data,headers=headers)
        return resp
    
    def action(self,phone_number,auth_code,wait_time,action_type):
        if action_type == 'sms':
            resp = self.__send_sms(phone_number,auth_code,wait_time)
        elif action_type == 'call':
            resp = self.__call(phone_number,auth_code)
        print(resp.content)
        # status = self.__parse_response(resp)
        # return status
    # def __parse_response(self,resp):

    #     pass

# s = SMS_Call_Tool()
# # s.action('15927432501','458975',2,'sms')
# s.action('15927432501','458975',2,'call')


# import pyotp
# from datetime import datetime
# key = pyotp.random_base32()
# for_time = datetime.now()
# print time.mktime(for_time.timetuple())
# totp = pyotp.TOTP(key,interval=5)
# print totp.at(datetime.now())
# time.sleep(5)
# print totp.at(datetime.now())



# print totp.now()
# import time
# time.sleep(20)
# print totp.now()


# seed = 100
# random.random()
# for i in range(10):
    
        
    
