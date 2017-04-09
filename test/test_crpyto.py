#coding:utf8

import base64
import chardet
from Crypto.Cipher import AES
import math
import random


choice = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789'


def createRandomFields(size):
    ret = []
    for i in xrange(size):
        ret.append(random.choice(choice))
    return ''.join(ret)


def encrypt(key,text):
    cryptor = AES.new(key,AES.MODE_CBC,b'0000000000000000')
    #这里密钥key 长度必须为16（AES-128）,
    #24（AES-192）,或者32 （AES-256）Bytes 长度
    #目前AES-128 足够目前使用
    length = 16
    count = len(text)
    if count < length:
        add = (length-count)
        #\0 backspace
        text = text + ('\0' * add)
    elif count > length:
        add = (length-(count % length))
        text = text + ('\0' * add)
    ciphertext = cryptor.encrypt(text)
    #因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
    #所以这里统一把加密后的字符串转化为16进制字符串
    return ciphertext
     
    #解密后，去掉补足的空格用strip() 去掉
def decrypt(key,text):
    cryptor = AES.new(key,AES.MODE_CBC,b'0000000000000000')
    plain_text  = cryptor.decrypt(text)
    return plain_text.rstrip('\0')


def de(key,text):
    text = base64.b64decode(text)
    d = decrypt(key,text)
    return d.split('\0')


def auth_text_gen(key,text):
    '''
    生成app端的连接认证回传消息
    '''
    a = de(key,text)
    content = 'ACK\0'
    a = encrypt(key,content+a[-1][::-1])
    a = base64.b64encode(a)
    print '%s'%(a)
    return a



def explicit_text_gen(key,text):
    '''
    生成app端显示认证请求
    '''
    a = de(key,text)
    content = 'SUCCEED\0'
    a = encrypt(key,content+a[-1][::-1])
    a = base64.b64encode(a)
    print '{"action":"EXPLICIT","info":"%s"}'%(a)
    return a

def gen_b64_random_and_code(key,prefix,data=None):
    '''
    生成服务器认证码（BASE64）
    '''
    random_number = createRandomFields(20)
    cookie = prefix
    if data is not None:
        cookie += "\0%s" %(data)    
    cookie += "\0%s" %(random_number)   
    e = encrypt(key,cookie)
    return random_number,base64.b64encode(e)

def decrypt_and_validate_info(e,key,random_number,prefix=None):
    '''
    解密客户端回传信息，检验其随机数及前缀合法性，并返回除验证随机数以外的内容
    '''
    info = decrypt(key,base64.b64decode(e)).split('\0')
    random_number = random_number[::-1]
    # if random_number != info[-1]:
    #     raise AuthFailedError()
    # if prefix is not None:
    #     if info[0] != prefix:
    #         raise AuthFailedError(info)
    info.pop()
    return info

key = 'VXandQKqNs89y78bHj3DbHHmQsaHlkvH'

auth_text = 'q+BJZ17Z73EO5J6c83xdt4yqcbX90nORiFdc+bLcusg='
# data_text = 'h1gWAD95y8fakI3Q2p7HnknUp4QUjOZ5CNm8tdhHyv5wMx4XdboCHWvxxWC0hKDcXut2Geqk+uC4YfcPvUjB1Q=='
explicit_text = 'LejfdhQQSIzHHeeR51Og0Ff2frDDET/J5DPx32ZENTomxkkMGnmsK9bWfg1liGMZ'

# random_number,code = gen_b64_random_and_code(key,"SYN")
# print random_number

auth_text_gen(key,auth_text)
# print  de(key,data_text)


explicit_text_gen(key,explicit_text)


# c = de(key,code)

# decrypt_and_validate_info("qemZvJdDIk07tUk9dOOfI6HoJFoZx7U9w/ScvKAsjZY=",key,'000')
# print app_text

# print de(key,app_text)

# import ntplib
# from time import ctime
# from pprint import pprint
# c = ntplib.NTPClient()
# r = c.request('0.cn.pool.ntp.org',version=3)
# pprint(r.__dict__)

identifer = 'RwHGKXONuEOb1Vome5Bf'
api_hostname = 'DHA4ufjn'






