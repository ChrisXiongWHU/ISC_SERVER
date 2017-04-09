#coding:utf-8

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ISC_SERVER.settings")
import django
django.setup()

from isc_auth.models import Account,Application,User,Device


def init_db():
    acc1 = Account.objects.create(account_email="1050358918@qq.com",account_name="chris_whu",account_phone="15927432501", \
    **Account.new_account_hostname())
    acc2 = Account.objects.create(account_email="2389111521@qq.com",account_name="xiong_whu",account_phone="13979233017", \
    **Account.new_account_hostname())

    app1 = Application.objects.create(name='chris_sdk1',account=acc1,**Application.new_app(acc1.api_hostname))
    app2 = Application.objects.create(name='chris_sdk2',account=acc1,**Application.new_app(acc1.api_hostname))
    app3 = Application.objects.create(name='xiong_sdk1',account=acc2,**Application.new_app(acc2.api_hostname))
    app4 = Application.objects.create(name='xiong_sdk2',account=acc2,**Application.new_app(acc2.api_hostname))

    user1 = User.objects.create(user_name="xrb",user_phone="15927432501",account=acc1)
    user2 = User.objects.create(user_name="xrb",user_phone="15927432501",account=acc2)
    user3 = User.objects.create(user_name="xrb_2",user_phone="15927432501",account=acc1)

    device_user1_1 = Device.objects.create(user=user1,account=acc1,**Device.new_device(acc1.api_hostname))
    device_user1_2 = Device.objects.create(user=user1,account=acc1,**Device.new_device(acc1.api_hostname))
    device_user2 = Device.objects.create(user=user2,account=acc2,**Device.new_device(acc2.api_hostname))

def clear_db():
    Account.objects.all().delete()
    Application.objects.all().delete()
    User.objects.all().delete()
    Device.objects.all().delete()



if __name__ == '__main__':
    # clear_db()
    # init_db()
    try:
        Account.objects.get(account_email="aaa")
    except Account.DoesNotExist:
        print 'aaa'
    
    


  