from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.contrib import admin

from BuenViajeWebPage import views

admin.autodiscover()

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + patterns('',
                                                                                       # Examples:
                                                                                       # url(r'^$', 'BuenViaje.views.home', name='home'),
                                                                                       # url(r'^BuenViaje/', include('BuenViaje.foo.urls')),
                                                                                       url(r'^old-revistas/?$',
                                                                                           views.old_revistas),
                                                                                       url(r'^email_to_send/?$',
                                                                                           views.notification),
                                                                                       url(r'^contactenos/?$',
                                                                                           views.contactenos),
                                                                                       url(r'^de-cuba/?$',
                                                                                           views.de_cuba),
                                                                                       url(r'^unsubscribe/?$',
                                                                                           views.unsubscribe),
                                                                                       url(
                                                                                           r'^noticia/(?P<slug>[-\w]+)/?$',
                                                                                           views.noticia),
                                                                                       url(r'^noticias/?$',
                                                                                           views.noticias),
                                                                                       url(r'^imagen/(?P<id>\d+)/?$',
                                                                                           views.imagen),
                                                                                       url(
                                                                                           r'^ajax_noticias/(?P<id>\d+)/?$',
                                                                                           views.ajax_noticias),
                                                                                       url(r'^photo/?$', views.photo),
                                                                                       url(r'^proximo-anho/?$',
                                                                                           views.proximo_anho),
                                                                                       url(r'^la-revista/?$',
                                                                                           views.la_revista),
                                                                                       url(r'^distribucion/?$',
                                                                                           views.distribucion),
                                                                                       url(r'^informacion-general/?$',
                                                                                           views.informacion_general),
                                                                                       url(r'^informacion-destinos/?$',
                                                                                           views.informacion_destinos),
                                                                                       url(r'^imagenes/?$',
                                                                                           views.imagenes),
                                                                                       url(r'^tiempo-libre/?$',
                                                                                           views.tiempo_libre),
                                                                                       url(
                                                                                           r'^eventos/(?P<month>\d+)/?$',
                                                                                           views.eventos_month),
                                                                                       url(r'^eventos/?$',
                                                                                           views.eventos),
                                                                                       url(r'^search/?$', views.search),
                                                                                       url(r'^ajax_photo/?$',
                                                                                           views.ajax_photo_upload),
                                                                                       url(r'^subscribe/?$',
                                                                                           views.subscribe),
                                                                                       # Uncomment the admin/doc line below to enable admin documentation:
                                                                                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                                                                                       url(r'^change-language/?$',
                                                                                           views.change_language,
                                                                                           name='change_language'),
                                                                                       # Uncomment the next line to enable the admin:
                                                                                       url(r'^admin/',
                                                                                           include(admin.site.urls)),
                                                                                       (r'^newsletter/',
                                                                                        include('newsletter.urls')),
                                                                                       url(r'^ tinymce/',
                                                                                           include('tinymce.urls')),
                                                                                       url(r'^', views.inicio)
                                                                                       )

urlpatterns += staticfiles_urlpatterns()
