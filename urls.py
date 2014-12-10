from django.conf.urls import patterns, include, url
from django.contrib import admin
import frame as f

try:
	installed = open("/home/equinox/pythobb/pythobb/install","r").read()
	if installed.replace("\n","") == "False":
		import InstallPage as i
		indexPage = url(r'^$',i.PageOut().Init,name='Init')
		urlpatterns + ( url(r'^admin/doConfigure/',i.PageOut().doConfigure,name='doConfigure') )
	else:
		indexPage = url(r'^$',f.Pages().Index,name='Index')
except:
	xPage = url(r'^$',i.PageOut().Init,name='Init')
	urlpatterns + ( url(r'^admin/doConfigure/',i.PageOut().doConfigure,name='doConfigure') )

urlpatterns = patterns('',
    indexPage,
    url(r'^user/(?P<username>\w+)/$',f.Pages().Profile,name='Profile'),
    url(r'^member/controlpanel/$',f.Pages().userCP,name='userCP'),
    url(r'^member/modifySettings/$',f.Pages().modifySettings,name='modifySettings'),
    url(r'^member/login/$',f.Pages().Login,name='Login'),
    url(r'^member/login/doLogin/$',f.Pages().doLogin,name='doLogin'),
    url(r'^member/register/$',f.Pages().Register,name='Register'),
    url(r'^member/register/doRegister/$',f.Pages().doRegister,name='doRegister'),
    url(r'^member/logout/$',f.Pages().doLogout,name='doLogout'),
    url(r'^lostcsrf/doToken/$',f.Pages().doToken,name='doToken'),
    url(r'^forum/(?P<fid>\d+)/$',f.Pages().Forum,name='Forum'),
    url(r'^forum/(?P<fid>\d+)/newthread/$',f.Pages().MakeThread,name='MakeThread'),
    url(r'^forum/(?P<fid>\d+)/newthread/makeThread/$',f.Pages().ProcessNThread,name='ProcessNThread'),
    url(r'^forum/(?P<fid>\d+)/(?P<tid>\d+)/$',f.Pages().Thread,name='Thread'),
    url(r'^forum/(?P<fid>\d+)/(?P<tid>\d+)/makePost/$',f.Pages().MakePost,name='MakePost'),
    url(r'^forum/(?P<fid>\d+)/(?P<tid>\d+)/deletePost/(?P<pid>\d+)/$',f.Pages().DeletePost,name='DeletePost'),
    url(r'^admin/$',f.Pages().Administrator,name='Administrator'),
    url(r'^admin/configure/$',f.Admin().Configure,name='Configure'),
    url(r'^admin/configure/add/$',f.Admin().Add,name='Add'),
    url(r'^admin/delete/category/(?P<cid>\d+)/$',f.Admin().Configure,name='Configure'),
    url(r'^admin/delete/forum/(?P<fid>\d+)/$',f.Admin().Configure,name='Configure'),
    url(r'^admin/ban/user/(?P<userid>\d+)/$',f.Admin().ToggleBan,name='ToggleBan')
)
