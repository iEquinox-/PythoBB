from django.conf.urls import patterns, include, url
from django.contrib import admin

import frame as f

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pythobb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$',f.Pages().Index,name='Index'),
    url(r'^user/(?P<username>\w+)/$',f.Pages().Profile,name='Profile'),
    url(r'^member/login/$',f.Pages().Login,name='Login'),
    url(r'^member/login/doLogin/$',f.Pages().doLogin,name='doLogin'),
    url(r'^member/register/$',f.Pages().Register,name='Register'),
    url(r'^member/register/doRegister/$',f.Pages().doRegister,name='doRegister'),
    url(r'^member/logout/$',f.Pages().doLogout,name='doLogout')
)
