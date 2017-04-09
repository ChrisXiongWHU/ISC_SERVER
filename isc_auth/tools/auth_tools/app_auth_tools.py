#coding:utf-8


import base64
import random
from Crypto.Cipher import AES
from isc_auth.tools.uniform_tools import createRandomFields
import qrcode
import cStringIO



CONNECTION_SETUP_PREFIX = "SYN"
CONNECTION_REPLY_PREFIX = "ACK"
EXPLICIT_SUCCEED_PREFIX = "SUCCEED"
EXPLICIT_DENIED_PREFIX = "FAILED"
EXPLICIT_AUTH_PREFIX = "AUTH"


EXPLICIT_REPLY_COMMAND = "EXPLICIT"





class AuthFailedError(Exception):
    pass

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
    if random_number != info[-1]:
        raise AuthFailedError()
    if prefix is not None: 
        if info[0] != prefix:
            raise AuthFailedError(info)
    info.pop()
    return info

def generate_captcha(api_hostname,identifer,dKey):
    '''
    生成验证码
    '''
    content = "Auth://{b64_key}-{b64_device_identifier}-{b64_api_hostname}"
    b64_device = base64.b64encode(identifer)
    b64_key = base64.b64encode(dKey)
    b64_api_hostname = base64.b64encode(api_hostname)
    content = content.format(b64_key=b64_key,b64_device_identifier=b64_device,b64_api_hostname=b64_api_hostname)
    qr = qrcode.QRCode(version=1,box_size=3)
    qr.add_data(content)
    img = qr.make_image()
    buffer = cStringIO.StringIO()
    img.save(buffer,format="JPEG")
    return base64.b64encode(buffer.getvalue())

def generate_aes_key():
    '''
    生成256位AES秘钥
    '''
    return createRandomFields(32)


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
    return ciphertext
     
    #解密后，去掉补足的空格用strip() 去掉
def decrypt(key,text):
    cryptor = AES.new(key,AES.MODE_CBC,b'0000000000000000')
    plain_text  = cryptor.decrypt(text)
    return plain_text.rstrip('\0')



    



    




    
