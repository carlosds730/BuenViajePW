# -*- coding: utf8 -*-
import os
from django.db import models
from sorl.thumbnail import ImageField
from sorl.thumbnail import get_thumbnail
from django.core.validators import email_re
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from tinymce import models as tinymce_models
from django.conf import settings
from date_utils import edit_fecha, edit_fecha_evento

choices = [('principal', 'Principal'),
           ('p_bloque', 'Primer Bloque'),
           ('s_bloque', 'Segundo Bloque')]


# DONE: Rewrite some save method's: Noticia, Eventos, Revista, Publicidad, Blogs

class KeyWord(models.Model):
    class Meta:
        verbose_name = 'Palabra Clave'
        verbose_name_plural = 'Palabras Claves'

    keywords = models.CharField(max_length=200, verbose_name='Palabra claves', help_text='seprados por coma(,)',
                                blank=True, null=True)
    description = models.CharField(max_length=400, verbose_name=u'Descripción para google',
                                   help_text='Lo que va de en los metadatos', blank=True, null=True)
    facebook_msg = models.CharField(max_length=300, verbose_name='Mensaje para facebook',
                                    help_text='Lo que va en og:title metadata', blank=True, null=True)
    twitter_msg = models.CharField(max_length=300, verbose_name='Mensaje para twitter',
                                   help_text='Lo que va en twitter:title metadata', blank=True, null=True)
    facebook_img = ImageField(verbose_name='Foto de facebook', upload_to='facebook', blank=True, null=True)

    is_index = models.BooleanField(default=False, verbose_name='Es principal?',
                                   help_text=u'Marcar si las palabras claves van en la página principal')

    twitter_img = ImageField(verbose_name='Foto de twitter', upload_to='twitter', blank=True, null=True)

    noticia = models.ForeignKey(to='Noticia', verbose_name='Noticia', related_name='keywords',
                                help_text='Palabras claves usadas para las redes sociales', blank=True, null=True)

    evento = models.ForeignKey(to='Eventos', verbose_name='Evento', related_name='keywords',
                               help_text='Palabras claves usadas para las redes sociales', blank=True, null=True)

    seccion_tiempo_libre = models.ForeignKey(to='Seccion_Tiempo_Libre', verbose_name='Tiempo Libre',
                                             related_name='keywords',
                                             help_text='Palabras claves usadas para las redes sociales', blank=True,
                                             null=True)

    seccion_cuba_informacion_destinos = models.ForeignKey(to='Seccion_Cuba_Informacion_Destino',
                                                          verbose_name=u'Seccion Cuba Información Destino',
                                                          related_name='keywords',
                                                          help_text='Palabras claves usadas para las redes sociales',
                                                          blank=True, null=True)

    seccion_cuba_informacion_general = models.ForeignKey(to='Seccion_Cuba_Informacion_General',
                                                         verbose_name=u'Seccion Cuba Información General',
                                                         related_name='keywords',
                                                         help_text='Palabras claves usadas para las redes sociales',
                                                         blank=True, null=True)

    seccion_la_revista = models.ForeignKey(to='Seccion_La_Revista',
                                           verbose_name=u'Seccion La Revista',
                                           related_name='keywords',
                                           help_text='Palabras claves usadas para las redes sociales', blank=True,
                                           null=True)

    # DONE: Redefine the save so there is only one keyword with is_index=True
    def save(self, *args, **kwargs):
        if self.is_index and self.noticia:
            raise ValidationError(
                u'Una palabra clave debe estar asociada a una noticia o a una página principal, pero no a las dos')
        if self.is_index:
            index_keyowrds = KeyWord.objects.filter(is_index=True)
            for key in index_keyowrds:
                key.is_index = False
                key.save()
            self.is_index = True
        super(KeyWord, self).save(args, kwargs)

    def __str__(self):
        return self.keywords


class Banner(models.Model):
    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'

    titulo = models.CharField(max_length=200, verbose_name='Titulo')

    en_title = models.CharField(max_length=200, verbose_name='Title')

    url = models.URLField(verbose_name='Url', name='url', blank=True, null=True)

    imagen = ImageField(verbose_name='Imagen', upload_to='own')

    def get_small_thumbnail(self, size):
        return get_thumbnail(self.imagen, size, upscale=False)

    def __unicode__(self):
        return self.titulo


# DONE: Add a "Show" field to identify if the publicity should be shown or not.
class Publicidades(models.Model):
    class Meta:
        verbose_name = 'Publicidad'
        verbose_name_plural = 'Publicidades'
        ordering = ['sort_order']

    nombre = models.CharField(max_length=100, verbose_name='Nombre', db_index=True, help_text='Nombre de la publicidad')

    en_name = models.CharField(max_length=100, verbose_name='Name', db_index=True, help_text='Name of publicity')

    url = models.URLField(verbose_name='Url', blank=True, null=True, help_text='Url asociada a la publicidad')

    imagen = ImageField(verbose_name='Imagen', upload_to='own', help_text='Foto de la publicidad')

    sort_order = models.IntegerField(verbose_name='valor para ordernar',
                                     help_text='Valor utilizado para ordenar las publicidades')
    # DONE: Descomentar esto
    show = models.NullBooleanField(verbose_name='Mostrar', default=True,
                                   help_text='Indica si una publicidad es mostrada o no', blank=True, null=True)

    position = models.CharField(verbose_name=u'Posición', choices=choices, max_length=20,
                                help_text=u'Define la posición en que será mostrada en la página principal')

    def get_small_thumbnail(self):
        return get_thumbnail(self.imagen, "250x64", upscale=False).url

    def __unicode__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        settings.NEED_TO_RECALCULATE = True
        super(Publicidades, self).save(*args, **kwargs)
        # views.recalculate_all_data()


class Seccion_La_Revista(models.Model):
    class Meta:
        verbose_name = 'Seccion La Revista'
        verbose_name_plural = 'Seccion La Revista'

    encabezado_revista = tinymce_models.HTMLField(verbose_name="Encabezado de Seccion Revista",
                                                  help_text='Este es el encabezado de la seccion revista')

    en_encabezado_revista = tinymce_models.HTMLField(verbose_name="Encabezado de Seccion Revista en Ingles",
                                                     help_text='Este es el encabezado de la seccion revista en ingles')

    encabezado_seccion = tinymce_models.HTMLField(verbose_name='Encabezado de seccion',
                                                  help_text='Este es el encabezado de la seccion de la seccion de revista')

    en_encabezado_seccion = tinymce_models.HTMLField(verbose_name='Encabezado de seccion en ingles',
                                                     help_text='Este es el encabezado de la seccion de la seccion de revista en ingles')

    def __str__(self):
        return str(self.id)


class Seccion(models.Model):
    class Meta:
        verbose_name = 'Seccion'
        verbose_name_plural = 'Secciones'

    titulo = models.CharField(verbose_name='Titulo', max_length=50, help_text='El titulo de las secciones')

    en_titulo = models.CharField(verbose_name='Titulo en Ingles', max_length=50,
                                 help_text='El titulo de las secciones en ingles')

    descripcion = tinymce_models.HTMLField(verbose_name='Descripcion', help_text='Una descripcion de la seccion')

    en_descripcion = tinymce_models.HTMLField(verbose_name='Descripcion en Ingles',
                                              help_text='Una descripcion de la seccion en ingles')

    image = ImageField(verbose_name='Foto', upload_to='own', help_text='Foto de la sección')

    seccion_la_revista = models.ForeignKey('Seccion_La_Revista', verbose_name='seccion_la_revista',
                                           related_name='secciones', help_text='Seccion asociada a la Seccion Revista')

    def __unicode__(self):
        return self.titulo


class Seccion_Distribucion(models.Model):
    class Meta:
        verbose_name = 'Distribución'
        verbose_name_plural = 'Seccion distribucion'

    # my_field = tinymce_models.HTMLField()

    anho = models.IntegerField(verbose_name='Año', help_text='Año de distribucion', unique=True)

    imagen = ImageField(verbose_name='Foto', upload_to='own', help_text='Foto de la Seccion')

    encabezado = tinymce_models.HTMLField(verbose_name='Encabezado', help_text='Encabezado de la seccion dsitribucion')

    en_encabezado = tinymce_models.HTMLField(verbose_name='Encabezado en ingles',
                                             help_text='Encabezado de la seccion dsitribucion en ingles')

    texto = tinymce_models.HTMLField(verbose_name='Cuerpo', help_text='Cuerpo de la seccion')

    en_texto = tinymce_models.HTMLField(verbose_name='Cuerpo en ingles', help_text='Cuerpo de la seccion en ingles')

    def __str__(self):
        return str(self.anho)


class Seccion_Cuba_Informacion_General(models.Model):
    class Meta:
        verbose_name = 'Seccion de Cuba Informacion General'
        verbose_name_plural = 'Seccion de Cuba Informacion General'

    # DONE: This should be an HTMLField
    texto = tinymce_models.HTMLField(verbose_name='Texto', help_text='Cuerpo de la seccion')

    en_texto = tinymce_models.HTMLField(verbose_name='Texto en Ingles', help_text='Cuerpo de la seccion')

    def __unicode__(self):
        return str(self.id)


class Secciones_Informacion_General(models.Model):
    class Meta:
        verbose_name = 'Secciones de Informacion General'
        verbose_name_plural = 'Secciones de Informacion General'

    titulo = models.CharField(verbose_name='Titulo', max_length=100, help_text='Titulo de la seccion')

    en_titulo = models.CharField(verbose_name='Titulo en ingles', max_length=100,
                                 help_text='Titulo de la seccion en ingles')

    texto = tinymce_models.HTMLField(verbose_name='Texto', help_text='Cuerpo de la seccion')

    en_texto = tinymce_models.HTMLField(verbose_name='Texto en ingles', help_text='Cuerpo de la seccion en ingles')

    informacion_general = models.ForeignKey('Seccion_Cuba_Informacion_General', verbose_name='Informacion General',
                                            related_name='secciones')

    def __unicode__(self):
        return self.titulo


class Seccion_Cuba_Informacion_Destino(models.Model):
    class Meta:
        verbose_name = 'Destino'
        verbose_name_plural = 'Seccion Información por destinos'

    nombre = models.CharField(verbose_name='Nombre', max_length=50, help_text='Nombre de los destinos')

    en_nombre = models.CharField(verbose_name='Nombre en Ingles', max_length=50,
                                 help_text='Nombre de los destinos en Ingles')

    imagen = ImageField(verbose_name='Foto', upload_to='own', help_text='Foto del destino')

    descripcion_corta = models.CharField(verbose_name='Descripcion Corta', max_length=200,
                                         help_text='Una descripcion corta del destino')

    en_descripcion_corta = models.CharField(verbose_name='Descripcion Corta en Ingles', max_length=200,
                                            help_text='Una descripcion corta del destino en Ingles')

    texto = tinymce_models.HTMLField(verbose_name='Descripcion', help_text='Descripcion completa del destino')

    en_texto = tinymce_models.HTMLField(verbose_name='Descripcion en Ingles',
                                        help_text='Descripcion completa del destino en Ingles')

    def get_small_thumbnail(self):
        return get_thumbnail(self.imagen, "225x250").url

    def get_big_thumbnail(self):
        return get_thumbnail(self.imagen, "400x400").url

    def __unicode__(self):
        return self.nombre


class User(models.Model):
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    nombre = models.CharField(verbose_name='Usuario', max_length=50, help_text='Nombre del usuario')

    correo = models.EmailField(verbose_name='Correo', help_text='Correo del usuario', unique=True, null=True,
                               blank=True)

    def __str__(self):
        return unicode(self.nombre)

    def __unicode__(self):
        return unicode(self.nombre)

    def save(self, *args, **kwargs):
        if self.nombre == u'':
            self.nombre = "(Anonymous)"
        if self.correo:
            if not email_re.match(self.correo):
                raise ValidationError(u'%s no es una dirección de correo válida' % self.correo)
        super(User, self).save(*args, **kwargs)


class Seccion_Imagenes_Imagen(models.Model):
    class Meta:
        verbose_name = 'Imagen'
        verbose_name_plural = 'Blog de Imagenes'

    foto = ImageField(verbose_name='Foto', upload_to='public', help_text='Foto')

    fecha_upload = models.DateField(verbose_name='Fecha', help_text='Fecha en la que se subio foto', null=True,
                                    blank=True, default=now())

    fecha = models.CharField(verbose_name='Fecha', max_length=50, help_text='Fecha de la foto. Formato: Año;Mes;Día',
                             null=True, blank=True)

    descripcion = models.TextField(verbose_name='Descripcion', help_text='Descripcion de la foto')

    usuario = models.ForeignKey('User', verbose_name='Usuario', related_name='fotos',
                                help_text='Usuario que sube la foto')

    recibir_notificaciones = models.BooleanField(verbose_name='Recibir Notificaciones',
                                                 help_text='Recibir Notificaciones')

    def get_absolute_url(self):
        return "/imagen/%i/" % self.id

    def __unicode__(self):
        return str(self.foto).split('/')[-1]

    def to_show_sizes(self, size):
        return get_thumbnail(self.foto, size, upscale=False)

    def to_show(self):
        return get_thumbnail(self.foto, 'x200', upscale=False)

    def to_show_big(self):
        return get_thumbnail(self.foto, "700x450", upscale=False)

    def to_show_other_big(self):
        picture = get_thumbnail(self.foto, "600x500", upscale=False)
        return picture.url, picture.width, picture.height

    def to_show_other_way(self):
        picture = self.to_show()
        return picture.url, picture.width, picture.height

    def save(self, *args, **kwargs):
        try:
            pic = self.to_show_big()
        except:
            print('Image not cool')
            raise ValidationError(u'El archivo %s no es correcto' % self.foto)

        if self.foto.size > 2000000:
            print('Image too big')
            raise ValidationError(u'El archivo %s es muy grande' % self.foto)

        super(Seccion_Imagenes_Imagen, self).save(*args, **kwargs)


class Seccion_Tiempo_Libre(models.Model):
    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Seccion Tiempo Libre'

    imagen = ImageField(verbose_name='Foto', upload_to='own', help_text='Foto de la excursion')

    logo = ImageField(verbose_name='Logo', upload_to='own', help_text='Foto del patrocinador')

    titulo = models.CharField(verbose_name='Titulo', max_length=100, help_text='Titulo')

    en_titulo = models.CharField(verbose_name='Titulo en Ingles', max_length=100, help_text='Titulo en Ingles')

    texto = tinymce_models.HTMLField(verbose_name='Descripcion', help_text='Descripcion del evento')

    en_texto = tinymce_models.HTMLField(verbose_name='Descripcion en Ingles',
                                        help_text='Descripcion del evento en Ingles')

    def to_show(self):
        return get_thumbnail(self.imagen, "532x353").url

    def to_show_logo(self):
        return get_thumbnail(self.logo, "40x31").url

    def __unicode__(self):
        return self.titulo


provinces = [(u'Pinar del Río', u'Pinar del Río'),
             ('La Habana', 'La Habana'),
             ('Artemisa', 'Artemisa'),
             ('Mayabeque', 'Mayabeque'),
             ('Matanzas', 'Matanzas'),
             ('Villa Clara', 'Villa Clara'),
             ('Cienfuegos', 'Cienfuegos'),
             ('Sancti Spiritus', 'Sancti Spiritus'),
             (u'Ciego de Ávila', u'Ciego de Ávila'),
             (u'Camagüey', u'Camagüey'),
             ('Las Tunas', 'Las Tunas'),
             (u'Holguín', u'Holguín'),
             ('Granma', 'Granma'),
             ('Santiago de Cuba', 'Santiago de Cuba'),
             (u'Guantánamo', u'Guantánamo')]


class Eventos(models.Model):
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['fecha_inicio', 'fecha_final']

    titulo = models.CharField(verbose_name='Titulo', max_length=200, help_text='Titulo del evento')

    en_titulo = models.CharField(verbose_name='Titulo en Ingles', max_length=200,
                                 help_text='Titulo del evento en Ingles')

    imagen = ImageField(verbose_name='Foto', upload_to='own', help_text='Foto promocional del evento', blank=True,
                        null=True)

    fecha_inicio = models.DateField(verbose_name='Fecha de Inicio')

    fecha_final = models.DateField(verbose_name='Fecha de Clausura')

    presentacion = models.BooleanField(verbose_name='Presentacion', default=False,
                                       help_text='Si el evento saldra en la pagina inicial')

    short_texto = models.TextField(verbose_name='Descripcion corta', max_length=200,
                                   help_text='Descripcion corta del evento', blank=True, null=True)

    en_short_texto = models.TextField(verbose_name='Descripcion corta en Ingles', max_length=200,
                                      help_text='Descripcion corta del evento en Ingles', blank=True, null=True)

    texto = tinymce_models.HTMLField(verbose_name='Descripcion', help_text='Descripcion del evento', blank=True,
                                     null=True)

    en_texto = tinymce_models.HTMLField(verbose_name='Descripcion en Ingles',
                                        help_text='Descripcion del evento en Ingles', blank=True, null=True)

    provincia = models.CharField(choices=provinces, max_length=200, verbose_name='Provincias',
                                 help_text='Provincia donde ocurrira el evento')

    sede = models.CharField(verbose_name='Sede', max_length=200, help_text='Sede del evento', blank=True, null=True)

    en_sede = models.CharField(verbose_name='Sede en Ingles', max_length=200, help_text='Sede del evento en Ingles',
                               blank=True, null=True)

    receptivo = models.CharField(verbose_name='Receptivo ', help_text='', max_length=200, blank=True, null=True)

    en_receptivo = models.CharField(verbose_name='Receptivo en Ingles', help_text='', max_length=200, blank=True,
                                    null=True)

    comite = models.CharField(verbose_name='Comite Organizador', help_text='Comite Organizador', max_length=200,
                              blank=True, null=True)

    en_comite = models.CharField(verbose_name='Comite Organizador en Ingles', help_text='Comite Organizador en Ingles',
                                 max_length=200, blank=True, null=True)

    telefono = models.CharField(verbose_name='Télefono', help_text='Télefono', blank=True, max_length=200, null=True)

    fax = models.CharField(verbose_name='Fax', help_text='Fax', blank=True, max_length=200, null=True)

    email = models.CharField(verbose_name='Emails', help_text='Emails, si son varios pongálos separados por coma',
                             max_length=200, blank=True, null=True)

    web = models.CharField(verbose_name='Web', help_text='Web, si son varios pongálos separados por coma',
                           max_length=200, blank=True, null=True)

    def get_fecha_en(self):
        return edit_fecha_evento(self.fecha_inicio, "en") + " to " + edit_fecha_evento(self.fecha_final, "en")

    def get_fecha_es(self):
        return "Del " + edit_fecha_evento(self.fecha_inicio, 'es') + " al " + edit_fecha_evento(self.fecha_final, "es")

    def get_small_thumbnail(self):
        return get_thumbnail(self.imagen, "277x185").url

    def fix_comma_email(self):
        return [x.strip() for x in self.email.strip().split(',')]

    def fix_comma_web(self):
        return [x.strip() for x in self.web.strip().split(',')]

    def get_month(self):
        from views import fix_month

        return fix_month(self.fecha_inicio.month)

    def __unicode__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        settings.NEED_TO_RECALCULATE = True
        # if self.presentacion and not (self.short_texto and self.en_short_texto and self.texto and self.en_texto and self.imagen):
        # raise ValidationError('Si el evento va en la pagina principal tiene que tener descripciones cortas y descripciones en ingles y en español')
        if self.presentacion:
            presentaciones = Eventos.objects.filter(presentacion=True)
            for x in presentaciones:
                x.presentacion = False
                x.save()
        super(Eventos, self).save(*args, **kwargs)
        # views.recalculate_all_data()


class Revista(models.Model):
    class Meta:
        verbose_name_plural = 'Revistas'
        verbose_name = 'Revista'
        ordering = ['numero']

    numero = models.IntegerField(verbose_name='Numero', help_text='Numero de la revista')

    anho = models.IntegerField(verbose_name='Año', help_text='Año de la revista')

    idioma = models.CharField(verbose_name='Idioma', max_length=50, help_text='Idioma de la revista')

    tipo = models.CharField(verbose_name='Tipo de Edición', default='Normal', max_length=20,
                            help_text='Tipos de ediciones')

    imagen = ImageField(verbose_name='Foto', upload_to='own', help_text='Foto de la portada')

    url = models.FileField(verbose_name='PDF', upload_to='revistas', help_text='La revista en formato pdf')

    def get_small_thumbnail(self):
        return get_thumbnail(self.imagen, "184x263", upscale=False).url

    def __str__(self):
        return str(self.numero)

    def save(self, *args, **kwargs):
        settings.NEED_TO_RECALCULATE = True
        super(Revista, self).save(*args, **kwargs)
        # views.recalculate_all_data()


class Blog(models.Model):
    class Meta:
        verbose_name = 'Blog'
        verbose_name_plural = 'Blogs'

    nombre = models.CharField(verbose_name='Nombre', max_length=100, help_text='Nombre del blog')

    en_nombre = models.CharField(verbose_name='Nombre en Ingles', max_length=100, help_text='Nombre del blog en Ingles')

    imagen = ImageField(verbose_name='Foto', upload_to='own', help_text='Foto del blog')

    def __unicode__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        settings.NEED_TO_RECALCULATE = True
        super(Blog, self).save(*args, **kwargs)
        # views.recalculate_all_data()


# DONE: This should have a sort order
class Noticia(models.Model):
    class Meta:
        verbose_name_plural = 'Noticias'
        verbose_name = 'Noticia'
        ordering = ['fecha_publicacion']

    titulo = models.CharField(verbose_name='Título', max_length=100, help_text='Título de la noticia')

    en_titulo = models.CharField(verbose_name='Título en Ingles', max_length=100,
                                 help_text='Título de la noticia en Ingles')

    slug = models.SlugField(verbose_name='Slug', max_length=200, help_text='Este campo no se edita')

    imagen = ImageField(verbose_name='Foto', upload_to='own', help_text='Foto de la noticia', null=True, blank=True)

    short_text = tinymce_models.HTMLField(verbose_name='Descripcion corta', max_length=200,
                                          help_text='Breve descripcion de la noticia')

    en_short_text = tinymce_models.HTMLField(verbose_name='Descripcion corta en Ingles', max_length=200,
                                             help_text='Breve descripcion de la noticia en Ingles')

    texto = tinymce_models.HTMLField(verbose_name='Descripcion', help_text='Descripcion de la noticia')

    en_texto = tinymce_models.HTMLField(verbose_name='Descripcion en Ingles',
                                        help_text='Descripcion de la noticia en Ingles')

    url = models.URLField(verbose_name='Link', help_text='Link de la noticia si esta publicada en otro sitio',
                          blank=True, null=True)

    blog = models.ForeignKey('Blog', verbose_name='Blog', related_name='noticias',
                             help_text='Blog al que pertenece la noticia', blank=True, null=True)

    fecha_publicacion = models.DateField(verbose_name='Fecha de Publicacion',
                                         help_text='Fecha en que se publico la noticia', default=now())

    allow_comments = models.BooleanField(verbose_name='Permitir Comentarios', default=True,
                                         help_text='Si una noticia puede ser comentada')

    position = models.CharField(verbose_name=u'Posición', choices=choices, max_length=20,
                                help_text=u'Define la posición en que será mostrada en la página principal')

    show = models.BooleanField(verbose_name=u'Mostrar', default=True,
                               help_text=u'Define si una noticia será mostrada')
    # DONE: Descomentar esto
    sort_order = models.IntegerField(verbose_name='Valor para ordenar',
                                     help_text='Valor utilizado para ordenar las noticias del mismo dia', blank=True,
                                     null=True)
    related_news = models.ManyToManyField(to='Noticia', verbose_name='Noticias relacionadas', related_name='news',
                                          help_text='Escoger las noticias relacionadas', blank=True, null=True)

    def get_small_thumbnail(self, sizes):
        return get_thumbnail(self.imagen, sizes, upscale=False)

    def get_thumbnail_to_show(self):
        return get_thumbnail(self.imagen, "600x400", upscale=False)

    def get_absolute_url(self):
        return "/noticia/%s/" % self.slug

    def __unicode__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        settings.NEED_TO_RECALCULATE = True
        print(settings.NEED_TO_RECALCULATE)
        super(Noticia, self).save(*args, **kwargs)
        # views.recalculate_all_data()

    def delete(self, using=None):
        settings.NEED_TO_RECALCULATE = True
        print(settings.NEED_TO_RECALCULATE)
        super(Noticia, self).delete()


class Comentarios(models.Model):
    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-fecha']

    texto = models.TextField(verbose_name='Comentario', help_text='Comentario')

    imagen = models.ForeignKey('Seccion_Imagenes_Imagen', verbose_name='Imagen', related_name='comentarios',
                               help_text='Imagen asociada', blank=True, null=True)

    noticia = models.ForeignKey('Noticia', verbose_name='Noticia', related_name='comentarios',
                                help_text='Comentario asociado', blank=True, null=True)

    fecha = models.DateTimeField(verbose_name='Fecha', help_text='Fecha de publicacion')

    usuario = models.ForeignKey('User', verbose_name='usuario', related_name='comentarios',
                                help_text='Usuario que comentó')

    recibir_notificaciones = models.BooleanField(verbose_name='Recibir Notificaciones',
                                                 help_text='Recibir notificaciones')

    def fecha_esp(self):
        return edit_fecha(self.fecha, "es")

    def fecha_en(self):
        return edit_fecha(self.fecha, "en")

    def __unicode__(self):
        return unicode(self.usuario.nombre)


class Extra_Images(models.Model):
    class Meta:
        verbose_name = u'Imágen Extra'
        verbose_name_plural = u'Imágenes Extras'
        ordering = ['sort_order']

    imagen = ImageField(verbose_name='Foto', upload_to='own', help_text='Foto extras de la noticia', null=True,
                        blank=True)

    alt = models.CharField(verbose_name='Descripción de la foto', max_length=100, help_text='Descripción de la foto',
                           null=True, blank=True)

    sort_order = models.IntegerField(verbose_name='Valor para ordenar',
                                     help_text='Valor utilizado para ordenar las fotos', blank=True,
                                     null=True)

    new = models.ForeignKey(to='Noticia', verbose_name='Noticia', related_name='extra_images')
