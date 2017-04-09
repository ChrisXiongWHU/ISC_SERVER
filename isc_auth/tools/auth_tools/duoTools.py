#coding:utf-8

from django.db import models
from isc_auth.models import Account,Application,createRandomFields,User
from isc_auth.tools.uniform_tools import createRandomFields


import hashlib,hmac,time,qrcode,cStringIO,base64
from Crypto.Cipher import AES
 


DUO_PREFIX = 'TX'
AUTH_PREFIX = 'AUTH'
EXPIRETIME = 60




class DuoFormatException(Exception):
    pass

def parseDuoSig(sig):
    '''
    拆分sig，返回{'prefix':prefix,
    'content':(username,iKey,expiretime),
    'sha_1':加密信息}
    并检查格式，若格式错误则返回抛出异常
    '''
    s = sig.split('|')
    if len(s)!=3:
        raise DuoFormatException()
    prefix,cookie,sha_1 = s
    try:
        #将cookie解码后转换为Unicode
        import chardet
        s = [c.decode(chardet.detect(c)['encoding'])  \
            for c in base64.b64decode(cookie).split('|')]

    except TypeError,e:
        raise DuoFormatException()
    if len(s) != 3:
        raise DuoFormatException()
    #??
    userName,iKey,expiretime = s
    ret =  {
        'prefix':prefix,
        'content':s,
        'sha_1':sha_1
    }
    return ret

def _hmac_sha1(key, msg):
    ctx = hmac.new(key, msg, hashlib.sha1)
    return ctx.hexdigest()


def validateParams(sigDicts,sKey):
    '''
    验证前缀是否合法，验证加密信息是否正确加密
    '''
    if DUO_PREFIX != sigDicts['prefix']:
        return False
    cookie = '%s|%s' %(DUO_PREFIX,base64.b64encode('|'.join(sigDicts['content'])))
    newSig = _hmac_sha1(sKey.encode('utf-8'),cookie)
    if _hmac_sha1(sKey.encode('utf-8'),newSig) != _hmac_sha1(sKey.encode('utf-8'),sigDicts['sha_1']):
        return False
    return True

def checkUserEnrolled(userName,account):
    '''
    验证user是否已经enroll，若是返回user，否则返回None
    '''
    try:
        user = account.user_set.get(user_name=userName)
    except User.DoesNotExist,e:
        return None
    return user


def signResponse(sigDicts,sKey):
    '''
    返回response的参数值，更新expiretime,prefix
    '''
    sigDicts['content'][-1] = str(int(time.time()) + EXPIRETIME)
    cookie = '%s|%s' % (AUTH_PREFIX,base64.b64encode('|'.join(sigDicts['content'])))
    newSig = _hmac_sha1(sKey.encode('utf-8'),cookie)
    return '%s|%s' %(cookie,newSig)

def _parse_vals(key, val, prefix, ikey):
    ts = int(time.time())
    u_prefix, u_b64, u_sig = val.split('|')
    cookie = '%s|%s' % (u_prefix, u_b64)
    e_key = key.encode('utf-8')
    e_cookie = cookie.encode('utf-8')

    sig = _hmac_sha1(e_key, e_cookie)
    if _hmac_sha1(e_key, sig.encode('utf-8')) != _hmac_sha1(e_key, u_sig.encode('utf-8')):
        return None

    if u_prefix != prefix:
        return None

    decoded = base64.b64decode(u_b64).decode('utf-8')
    user, u_ikey, exp = decoded.split('|')
    print user,u_ikey,exp

    if u_ikey != ikey:
        return None

    if ts >= int(exp):
        print 'time false'
        return None

    return user



def generate_captcha(api_hostname,identifer,dKey):
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









    


    
    