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
    # Examples:
    # url(r'^$', 'pythobb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # url(r'^admin/', include(admin.site.urls)),
    indexPage,
    url(r'^user/(?P<username>\w+)/$',f.Pages().Profile,name='Profile'),
    url(r'^member/controlpanel/$',f.Pages().userCP,name='userCP'),
    url(r'^member/modifySettings/$',f.Pages().modifySettings,name='modifySettings'),
    url(r'^member/login/$',f.Pages().Login,name='Login'),
    url(r'^member/login/doLogin/$',f.Pages().doLogin,name='doLogin'),
    url(r'^member/register/$',f.Pages().Register,name='Register'),
    url(r'^member/register/doRegister/$',f.Pages().doRegister,name='doRegister'),
    url(r'^member/logout/$',f.Pages().doLogout,name='doLogout'),
    url(r'^lostcsrf/doToken/$',f.Pages().doToken,name='doToken')
)
