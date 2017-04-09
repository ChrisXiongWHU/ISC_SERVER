#coding:utf-8

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

import random
from tools.uniform_tools import createRandomFields
import pyotp



class Account(models.Model):
    '''
    api_hostname唯一，用于标示Account
    '''
    account_email = models.EmailField(unique=True)
    account_name = models.CharField(max_length=30)
    account_phone = models.CharField(max_length=11)
    api_hostname = models.CharField(max_length=8,unique=True)

    @classmethod
    def new_account_hostname(self):
        '''
        返回随机生成的hostname（唯一）
        '''
        api_hostname = createRandomFields(8)
        while len(Account.objects.filter(api_hostname=api_hostname)) > 0:
            api_hostname = createRandomFields(8)
        return {"api_hostname":api_hostname}
        
    def __str__(self):
        return "%s | %s | %s" %(self.account_email,self.account_name,self.api_hostname)


class Application(models.Model):
    '''
    iKey唯一
    '''
    sKey = models.CharField('Secret Key',max_length=40)
    iKey = models.CharField('Integration Key',max_length=20,unique=True)
    name = models.CharField(max_length=30)
    account = models.ForeignKey(Account,on_delete=models.CASCADE)

    def __str__(self):
        return "%s | %s" % (self.name,self.iKey)

    @classmethod
    def new_app(self,api_hostname):
        '''
        返回一个参数字典，包含随机生成的sKey,iKey(唯一)，凭借iKey可唯一确定application
        '''
        sKey = createRandomFields(40)
        iKey = createRandomFields(20)
        while len(Application.objects.filter(iKey=iKey))>0:
            iKey = createRandomFields(20)
        ret = {
            'sKey':sKey,
            'iKey':iKey,
        }
        return ret
        

class User(models.Model):
    '''
    在一个hostname下，user_name唯一
    '''
    user_name = models.CharField(max_length=30)
    user_phone = models.CharField(max_length=11)
    account = models.ForeignKey(Account,on_delete=models.CASCADE)
    
    class Meta():
        unique_together=(("user_name","account"),)

    def __str__(self):                                                                                                         
        return "%s | %s" %(self.user_name,self.account)

class Device(models.Model):
    '''
    一个user，多个设备。设备ID唯一,凭借ID可唯一确定设备
    '''
    identifer = models.CharField(max_length=20)
    is_activated = models.BooleanField(default=False)
    #用于与APP的通信
    dKey = models.CharField('Device Key',max_length=256,null=True)
    seed = models.CharField('Random Seed',max_length=16,null=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    account = models.ForeignKey(Account,on_delete=models.CASCADE)
    

    def __str__(self):                                                                                                         
        return "%s | %s | %s" %(self.identifer,self.is_activated,self.user.user_name)

    @classmethod
    def new_device(self,api_hostname):
        '''
        返回一个参数字典，包含随机生成的identifer(唯一)
        '''
        identifer = createRandomFields(20)
        while len(Device.objects.filter(identifer=identifer))>0:
            identifer = createRandomFields(20)
        ret = {
            'identifer':identifer,
            'seed':pyotp.random_base32()
        }
        return ret

    class Meta():
        unique_together=(("identifer","account"),)
    





