__author__ = 'Roly'
# -*- coding: utf8 -*-
from django.contrib import admin
from sorl.thumbnail.admin import AdminImageMixin
from django.utils.translation import ugettext

from forms import ImageForm, EventsForm
import models


class KeywordInline(admin.StackedInline):
    models = models.KeyWord
    extra = 1


class NoticiaInline(admin.StackedInline):
    model = models.Noticia
    extra = 1


class ComentarioNoticiasInline(admin.StackedInline):
    model = models.Comentarios
    extra = 1
    fields = ['texto', 'fecha', 'usuario', 'recibir_notificaciones']


class ComentarioImagenInline(AdminImageMixin, admin.StackedInline):
    model = models.Comentarios
    extra = 1
    fields = ['texto', 'fecha', 'usuario', 'recibir_notificaciones']


class SeccionInlines(admin.TabularInline):
    model = models.Seccion
    extra = 3


class SeccionCubaInformacionGeneralInline(admin.StackedInline):
    model = models.Secciones_Informacion_General
    extra = 3


class AdminBanner(AdminImageMixin, admin.ModelAdmin):
    pass


class AdminPublicidades(AdminImageMixin, admin.ModelAdmin):
    list_display = ['nombre', 'sort_order']
    search_fields = ['nombre']


class AdminSeccioLaRevista(admin.ModelAdmin):
    inlines = [SeccionInlines]
    list_display = ['id', 'numero_secciones']

    def numero_secciones(self, obj):
        if obj:
            return len(obj.secciones.all())
        else:
            return '<span>(None)</span>'

    numero_secciones.short_description = 'Número de secciones'


class AdminSeccionDistribucion(AdminImageMixin, admin.ModelAdmin):
    pass


class AdminSeccionCubaInformacionGeneral(admin.ModelAdmin):
    inlines = [SeccionCubaInformacionGeneralInline]
    list_display = ['id', 'numero_secciones']

    def numero_secciones(self, obj):
        if obj:
            return len(obj.secciones.all())
        else:
            return '<span>(None)</span>'

    numero_secciones.short_description = 'Número de secciones'


class AdminSeccionCubaInformaciondestinos(AdminImageMixin, admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']


class AdminSeccionImagen(AdminImageMixin, admin.ModelAdmin):
    form = ImageForm
    inlines = [ComentarioImagenInline]
    list_display = ['__str__', 'fecha_upload', 'admin_usuario', 'numero_coment']
    search_fields = ['foto', 'fecha_upload', 'usuario__nombre']
    list_filter = ['fecha_upload', 'usuario__nombre']

    def numero_coment(self, obj):
        if obj:
            return len(obj.comentarios.all())
        else:
            return '<span>(None)</span>'

    def admin_usuario(self, obj):
        if obj.usuario:
            return '<a href="../user/%s/">%s</a>' % (obj.usuario.id, obj.usuario)
        else:
            return '<span>(None)</span>'

    numero_coment.short_description = 'Número de comentarios'
    admin_usuario.allow_tags = True
    admin_usuario.short_description = 'Usuario'


class AdminSeccionTiempoLibre(AdminImageMixin, admin.ModelAdmin):
    list_display = ['titulo']
    search_fields = ['titulo']


# DONE: Fix this
class AdminEventos(AdminImageMixin, admin.ModelAdmin):
    form = EventsForm
    list_display = ['titulo', 'fecha_inicio', 'fecha_final']
    list_filter = ['fecha_inicio', 'fecha_final', 'presentacion']
    search_fields = ['titulo']
    date_hierarchy = 'fecha_inicio'


class AdminRevista(AdminImageMixin, admin.ModelAdmin):
    list_display = ['numero', 'anho', 'idioma', 'tipo']
    list_filter = ['idioma', 'tipo', 'anho']


class AdminNoticia(AdminImageMixin, admin.ModelAdmin):
    inlines = [ComentarioNoticiasInline, KeywordInline]
    list_filter = ['blog', 'titulo', 'fecha_publicacion']
    list_display = ['titulo', 'fecha_publicacion', 'admin_blog', 'Numero_comentarios']
    search_fields = ['titulo', 'blog__nombre', 'fecha_publicacion']
    prepopulated_fields = {'slug': ('titulo',)}
    date_hierarchy = 'fecha_publicacion'

    def Numero_comentarios(self, obj):
        if obj:
            return len(obj.comentarios.all())
        else:
            return '<span>(None)</span>'

    def admin_blog(self, obj):
        if obj.blog:
            return '<a href="../blog/%s/">%s</a>' % (obj.blog.id, obj.blog)
        else:
            return '<span>(None)</span>'

    Numero_comentarios.short_description = ugettext(u'Número de comentarios')
    admin_blog.short_description = ugettext('blog')
    admin_blog.allow_tags = True
    admin_blog.admin_order_field = 'blog'


class AdminBlog(AdminImageMixin, admin.ModelAdmin):
    inlines = [NoticiaInline]

    list_display = ['nombre', 'numero_news']

    def numero_news(self, obj):
        if obj:
            return len(obj.noticias.all())
        else:
            return '<span>(None)</span>'

    numero_news.short_description = 'Cantidad de entradas'


class AdminUsuario(admin.ModelAdmin):
    list_display = ['nombre', 'correo']
    search_fields = ['nombre', 'correo']


admin.site.register(models.Banner, AdminBanner)
admin.site.register(models.User, AdminUsuario)
admin.site.register(models.Blog, AdminBlog)
admin.site.register(models.Noticia, AdminNoticia)
admin.site.register(models.Revista, AdminRevista)
admin.site.register(models.Eventos, AdminEventos)
admin.site.register(models.Seccion_Tiempo_Libre, AdminSeccionTiempoLibre)
admin.site.register(models.Seccion_Imagenes_Imagen, AdminSeccionImagen)
admin.site.register(models.Seccion_Cuba_Informacion_Destino, AdminSeccionCubaInformaciondestinos)
admin.site.register(models.Seccion_Cuba_Informacion_General, AdminSeccionCubaInformacionGeneral)
admin.site.register(models.Publicidades, AdminPublicidades)
admin.site.register(models.Seccion_La_Revista, AdminSeccioLaRevista)
admin.site.register(models.Seccion_Distribucion, AdminSeccionDistribucion)
