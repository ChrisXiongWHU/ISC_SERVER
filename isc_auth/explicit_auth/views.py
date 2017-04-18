#coding:utf-8

from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpRequest,HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.utils import IntegrityError
from django.core.cache import cache

from channels import Group
from channels.asgi import get_channel_layer
from isc_auth.tools.uniform_tools import get_session_from_channels,createRandomFields

from isc_auth.models import Application,Account,User,Device
from isc_auth.tools.auth_tools import app_auth_tools,duoTools,text_mobile_tools


import json,time,random,base64
import pyotp
import time


'''
接受request，request data为tx,parent
对tx进行验证，未通过则返回错误
检测user是否enroll，若未enroll进行enroll操作，否则进行验证或激活操作
'''
@xframe_options_exempt
def auth_pre(request,api_hostname):

    #若找不到对应的account,返回404
    try:
        account = Account.objects.get(api_hostname=api_hostname)
    except Account.DoesNotExist,e:
         return render(request,'explicit_auth/not_found.html')

    #检验参数是否错误，错误均返回403
    tx = request.GET['tx']
    #若sig存在格式错误，返回403
    #sig {'prefix':prefix,
    #'content':(username,iKey,expiretime),
    #'sha_1':加密信息}
    try:
        sig = duoTools.parseDuoSig(tx)
    except duoTools.DuoFormatException,e:
        return render(request,'explicit_auth/dennied.html')
    #若sig中的ikey未注册于apihostname下，返回403
    iKey = sig['content'][1]
    try:
        app = Application.objects.get(iKey=iKey,account__api_hostname=api_hostname)
    except Application.DoesNotExist,e:
        return render(request,'explicit_auth/dennied.html')
    sKey = app.sKey
    #若sig存在信息错误或加密错误，返回403
    if not duoTools.validateParams(sig,sKey):
        return render(request,'explicit_auth/dennied.html')


    #若user未enroll，进行enroll,若user已经enroll，但未激活设备，进行设备激活
    userName = sig['content'][0]
    user = duoTools.checkUserEnrolled(userName,account)

    #保存sig_dict，parent,sKey供enroll和认证使用
    request.session['sig_dict'] = sig
    request.session['parent'] = request.GET['parent']
    request.session['sKey'] = sKey

    if user is None:
        enroll_url = reverse('isc_auth:enroll',args=(api_hostname,))
        return redirect(enroll_url)
    else:
        #保存userphone至session
        user_phone = user.user_phone
        request.session['phone'] = user_phone
        #暂时只考虑一个设备
        device = user.device_set.all()[0]
        #若已激活，进行认证
        if device.is_activated:
            return render(request,'explicit_auth/explicit_auth/frame-auth.html',{
            'api_hostname':api_hostname,
            'identifer':device.identifer,
            'phone':user_phone
        })
        #未激活，则进行激活
        else:
            return render(request,'explicit_auth/explicit_auth/frame.html',{
                'api_hostname':api_hostname,
                'identifer':device.identifer,
                'has_enrolled':"true"
            })
##

'''
用户enroll过程，生成相应的设备（seed，identifer），不包括设备dkey
'''
@xframe_options_exempt
def enroll(request,api_hostname):
    #如果该请求为auth_pre发送
    if request.method == 'GET':
        return render(request,'explicit_auth/explicit_auth/frame.html',{
            'api_hostname':api_hostname,
            'identifer':'0'*20,            
            'has_enrolled':"false"
            })

    #若该请求为提交表单
    elif request.method =='POST':
        phone = request.POST['tel']
        # userName = request.session.get('sig_dict',None)['content'][0]
        # parent = request.session.get('parent',None)
        # account = Account.objects.get(api_hostname=api_hostname)
        request.session['phone'] = phone
        tool = text_mobile_tools.SMS_Call_Tool()
        #生成认证随机码
        pre_choices = '0123456789'
        auth_code = ''
        for i in xrange(6):
            auth_code += random.choice(pre_choices)
        #发送请求      
        wait_time = 2
        tool.action(phone,auth_code,wait_time,'sms')
        request.session['enroll_code'] = auth_code
        return HttpResponse()

        # #防止重复提交表单，捕获实体完整性错误
        # try:
        #     user = User.objects.create(user_name=userName,user_phone=phone,account=account)
        #     device = Device.objects.create(user=user,account=account,**Device.new_device(api_hostname))
        # except IntegrityError,e:
        #     user = User.objects.get(user_name=userName)
        #     device = user.device_set.all()[0]
        # return HttpResponse(device.identifer)
##

def do_enroll(request,api_hostname):
    code = request.POST['code']
    if code != request.session['enroll_code']:
        return HttpResponse(json.dumps({"status":"denied"}))

    userName = request.session.get('sig_dict',None)['content'][0]
    parent = request.session.get('parent',None)
    account = Account.objects.get(api_hostname=api_hostname)
    phone = request.session['phone']
    #防止重复提交表单，捕获实体完整性错误
    try:
        user = User.objects.create(user_name=userName,user_phone=phone,account=account)
        device = Device.objects.create(user=user,account=account,**Device.new_device(api_hostname))
    except IntegrityError,e:
        user = User.objects.get(user_name=userName)
        device = user.device_set.all()[0]
    return HttpResponse(json.dumps({"status":"succeed","identifer":device.identifer}))






'''
绑定设备
'''
@xframe_options_exempt
def bind_device(request,api_hostname,identifer):
    #生成二维码，秘钥并存入数据库。
    dkey = app_auth_tools.generate_aes_key()
    print dkey
    captcha = app_auth_tools.generate_captcha(api_hostname,identifer,dkey)
    #cache有效期设置比等待时间稍小
    cache.set("device-%s-%s_key" %(identifer,api_hostname),dkey,178)
    return HttpResponse(captcha)
##


'''
检查设备是否绑定，不超过120秒
'''
def check_bind(request,api_hostname,identifer):
    channel_layer = get_channel_layer() 
    #每10秒检查一次socket连接,最多不超过180秒
    #300
    for i in xrange(36):
        print i
        group_name = "device-%s-%s" %(identifer,api_hostname)
        device_group_list = channel_layer.group_channels(group_name)
        if len(device_group_list)>0:
            #进行认证,数据库更新
            key = get_session_from_channels(device_group_list,"key")
            device = Device.objects.get(identifer=identifer)
            device.dKey = key
            device.is_activated=True
            device.save()

            content_encrypt = app_auth_tools.encrypt(key,json.dumps({
                "type":"info",
                "data":"test data",
                "seed":device.seed
            }))
            Group(group_name).send({"text":base64.b64encode(content_encrypt)})
            return HttpResponse(content=json.dumps({'status':'ok'}))
        else:
            time.sleep(5)
    #120秒内未发现可用连接
    else:
        bind_url = reverse('isc_auth:bind_device',args=(api_hostname,identifer))
        return HttpResponse(content=json.dumps({'status':'pending'}))
##



@xframe_options_exempt
def auth_redirect(request,api_hostname,identifer):
    return render(request,'explicit_auth/explicit_auth/frame-auth.html',{
        'api_hostname':api_hostname,
        'identifer':identifer,
        'phone':request.session['phone']
    })
##

'''
进行SMS或电话认证
'''
def sms_call_auth(request,api_hostname,identifer):  
    if request.method == 'GET':
        tool = text_mobile_tools.SMS_Call_Tool()
        user = User.objects.get(device__identifer=identifer)
        phone = user.user_phone
        #生成认证随机码
        pre_choices = '0123456789'
        auth_code = ''
        for i in xrange(6):
            auth_code += random.choice(pre_choices)
        #发送请求      
        wait_time = 2
        action_type =   request.GET['type']
        tool.action(phone,auth_code,wait_time,action_type)
        #120秒
        cache.set("device-%s-%s_%s_code" %(identifer,api_hostname,action_type),auth_code,wait_time*60-10)
        return HttpResponse()
    elif request.method == 'POST':
        action_type = request.POST['type']
        auth_code = request.POST['code']
        saved_code = cache.get("device-%s-%s_%s_code" %(identifer,api_hostname,action_type),"")
        return auth_result_common_action(request,auth_code == saved_code)
##


'''
根据认证成功标志位进行相应的操作,非视图函数
'''
def auth_result_common_action(request,is_succeed):
    if is_succeed:
        sigDict = request.session.get('sig_dict',None)
        parent = request.session.get('parent',None)
        sKey = request.session.get('sKey',None)
        responseBody = duoTools.signResponse(sigDict,sKey)
        return HttpResponse(content=json.dumps({
            'status':'ok',
            'data':responseBody,
            'parent':parent
        }))
    else:
        return HttpResponse(content=json.dumps({'status':'denied'}))
##

'''
APP离线认证码认证,interval设置为30分钟
'''
def random_code_auth(request,api_hostname,identifer):
    random_code = request.POST['code']
    seed = Device.objects.get(identifer=identifer).seed
    totp = pyotp.TOTP(key,interval=30)
    #TODO 计算服务器的随机数码
    #TODO 获取标准时间
    server_random_code = totp.at(time.time())
    return auth_result_common_action(request,totp.verify(random_code,time.time(),1))
##

    
  
'''
push认证中检查手机APP websocket是否连接，最多不超过60秒
'''
@xframe_options_exempt
def auth_check_ws(request,api_hostname,identifer):
    
    channel_layer = get_channel_layer()
    device_group_name = "device-%s-%s" %(identifer,api_hostname)
    # 每3秒检查一次socket连接,最多不超过60秒
    for i in xrange(20):
        device_group_list = channel_layer.group_channels(device_group_name)
        if len(device_group_list)>0:
            key = get_session_from_channels(device_group_list,"key")
            data = {"xxx":"xxx"}
            random,code = app_auth_tools.gen_b64_encrypt_explicit_auth_code(key,data)
            cache.set("device-%s-%s_explicit_random" %(identifer,api_hostname),random,118)
            Group(device_group_name).send({"text":code})
            return HttpResponse(content=json.dumps({'status':'ok'}))
        else:
            time.sleep(3)
    # 60秒内未发现可用连接
    else:
        return HttpResponse(content=json.dumps({'status':'pending'}))
##



'''
push认证，检查由channels进行websocket认证参数检查
'''
def auth(request,api_hostname,identifer):
    device_group_name = "device-%s-%s" %(identifer,api_hostname)
    device_group_list = get_channel_layer().group_channels(device_group_name)
    #若连接中断
    if len(device_group_list) == 0:
        return HttpResponse(content=json.dumps({'status':'pending','seq':request.session['seq']}))

    # 每3秒检查一次认证情况,最多不超过60秒
    for i in xrange(20):
        auth_status = cache.get("device-%s-%s_auth" %(identifer,api_hostname),None)
        # 未收到认证信息
        if auth_status is None:
            time.sleep(3)       
        else:
            del cache["device-%s-%s_auth" %(identifer,api_hostname)]
            return auth_result_common_action(request,auth_status)
    # 认证未进行
    else:
        return HttpResponse(content=json.dumps({'status':'pending'}))
##







        



    
        
    


    
    
    
    
