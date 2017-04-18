from django.conf.urls import include,url
import explicit_auth.views



app_name = 'isc_auth'

url_hostname_identifer = r'^api-(?P<api_hostname>[a-zA-Z1-9]+)/(?P<identifer>[a-zA-Z1-9]{20})/frame/%s/$'
url_hostname = r'^api-(?P<api_hostname>[a-zA-Z1-9]+)/frame/%s/$'

explicit_auth_urlpatterns = [
    url(url_hostname %'auth',explicit_auth.views.auth_pre,name='pre_auth'),
    url(url_hostname %'enroll',explicit_auth.views.enroll,name='enroll'),
    url(url_hostname %'do_enroll',explicit_auth.views.do_enroll,name='do_enroll' ),
    url(url_hostname_identifer %'auth_check_ws',explicit_auth.views.auth_check_ws,name='auth_check_ws'),
    url(url_hostname_identifer %'push_auth',explicit_auth.views.auth,name='push_auth'),
    url(url_hostname_identifer %'auth_redirect',explicit_auth.views.auth_redirect,name='auth_redirect'),    
    url(url_hostname_identifer %'bind_device',explicit_auth.views.bind_device,name='bind_device'),
    url(url_hostname_identifer %'check_bind',explicit_auth.views.check_bind,name='check_bind'), 
    url(url_hostname_identifer %'text_auth',explicit_auth.views.sms_call_auth,name='text_auth'), 
    url(url_hostname_identifer %'app_code_auth',explicit_auth.views.random_code_auth,name='app_code_auth'),     
    # url(r'test_frontend',explicit_auth.views.test_front_end,name="test_frontend"),
]


urlpatterns = [
    url(r'^',include(explicit_auth_urlpatterns)),   
]



