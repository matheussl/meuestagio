from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^(?P<slug>[^/.]+)/$', views.area, name='area'),
    url(r'^(?P<slug_area>[^\.]+)/(?P<slug>[^\.]+)/$', views.estagio, name='estagio'),
)
