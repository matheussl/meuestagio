from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^vagas/(?P<slug>[^/.]+)/$', views.area, name='area'),
    url(r'^vagas/(?P<slug_area>[^\.]+)/(?P<slug>[^\.]+)/$', views.estagio, name='estagio'),
)
