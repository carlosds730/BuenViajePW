# -*- coding:utf8 -*-

from threading import Thread
import json
import os
import string
import datetime
from django.db.models import Count
from django.utils.timezone import now
from django.utils.timezone import get_current_timezone
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import Context
from django.template.loader import get_template
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.mail import get_connection
from django.core.mail import send_mail
from django.conf import settings
from newsletter import models as md_newsletter

import models


def fix_coma(value):
    return [x.strip() for x in value.strip().split(',')]


def fix_month(x, trigger=False):
    if trigger:
        if x.lower() == 'enero':
            return 1, 'Enero', 'January'
        elif x.lower() == 'febrero':
            return 2, 'Febrero', 'February'
        elif x.lower() == 'marzo':
            return 3, 'Marzo', 'March'
        elif x.lower() == 'abril':
            return 4, 'Abril', 'April'
        elif x.lower() == 'mayo':
            return 5, 'Mayo', 'May'
        elif x.lower() == 'junio':
            return 6, 'Junio', 'June'
        elif x.lower() == 'julio':
            return 7, 'Julio', 'July'
        elif x.lower() == 'agosto':
            return 8, 'Agosto', 'August'
        elif x.lower() == 'septiembre':
            return 9, 'Septiembre', 'September'
        elif x.lower() == 'octubre':
            return 10, 'Octubre', 'October'
        elif x.lower() == 'noviembre':
            return 11, 'Noviembre', 'November'
        else:
            return 12, 'Diciembre', 'December'
    if x == 1:
        return 1, 'Enero', 'January'
    elif x == 2:
        return 2, 'Febrero', 'February'
    elif x == 3:
        return 3, 'Marzo', 'March'
    elif x == 4:
        return 4, 'Abril', 'April'
    elif x == 5:
        return 5, 'Mayo', 'May'
    elif x == 6:
        return 6, 'Junio', 'June'
    elif x == 7:
        return 7, 'Julio', 'July'
    elif x == 8:
        return 8, 'Agosto', 'August'
    elif x == 9:
        return 9, 'Septiembre', 'September'
    elif x == 10:
        return 10, 'Octubre', 'October'
    elif x == 11:
        return 11, 'Noviembre', 'November'
    else:
        return 12, 'Diciembre', 'December'


def fix_months(collection):
    res = []
    for x in collection:
        res.append(fix_month(x))
    return res


def calculate_all_data():
    newsletter = md_newsletter.Newsletter.objects.only("pk", "title")
    # newsletter = [(x.pk, x.title) for x in md_newsletter.Newsletter.objects.all()]
    bvatw = models.Blog.objects.get(nombre='Buen Viaje por el Mundo').pk
    blogs = models.Blog.objects.exclude(pk__exact=bvatw).order_by("-pk")
    blog_0 = blogs[0]
    blog_0_noticia = blog_0.noticias.order_by("-fecha_publicacion")[0]

    blog_1 = blogs[1]
    blog_1_noticia = blog_1.noticias.order_by("-fecha_publicacion")[0]

    main = models.Publicidades.objects.filter(show=True, position='principal').order_by("sort_order")
    first = models.Publicidades.objects.filter(show=True, position='p_bloque').order_by("sort_order")
    second = models.Publicidades.objects.filter(show=True, position='s_bloque').order_by("sort_order")

    noticias = [(x.titulo, x.en_titulo, x.get_small_thumbnail("25x20").url, x.get_absolute_url()) for x in
                models.Noticia.objects.filter(blog=None).order_by("-fecha_publicacion")[0:5]]

    return {
        'newsletter': newsletter,
        'blog_0': blog_0,
        'blog_0_noticia': blog_0_noticia,
        'blog_0_noticia_url': blog_0_noticia.get_absolute_url(),
        'blog_0_noticia_small_img': blog_0_noticia.get_small_thumbnail("90x72").url,
        'blog_1': blog_1,
        'blog_1_noticia': blog_1_noticia,
        'blog_1_noticia_url': blog_1_noticia.get_absolute_url(),
        'blog_1_noticia_small_img': blog_1_noticia.get_small_thumbnail("90x72").url,
        'main': main,
        'first': first,
        'second': second,
        'last_revista': models.Revista.objects.order_by('-anho', '-numero')[0],
        'noticias': noticias,
        'mes': fix_month((now() + datetime.timedelta(days=7)).month),
    }


def home_data_spanish():
    news_to_publish = models.Noticia.objects.filter(blog=None, position='principal').order_by("-fecha_publicacion",
                                                                                              "sort_order")
    main_news = [(main_news.titulo, main_news.short_text, main_news.get_small_thumbnail("264x185").url,
                  main_news.get_absolute_url(), main_news.id) for main_news in news_to_publish]

    first = [(x.titulo, x.short_text, x.get_small_thumbnail("120x90").url, x.get_absolute_url(), x.id) for x in
             models.Noticia.objects.filter(blog=None, position='p_bloque').order_by("-fecha_publicacion",
                                                                                    "sort_order")]
    second = [(x.titulo, x.get_small_thumbnail("120x90").url, x.get_absolute_url(), x.id) for x in
              models.Noticia.objects.filter(blog=None, position='s_bloque', show=True).order_by("-fecha_publicacion",
                                                                                                "sort_order")]
    main_event = models.Eventos.objects.get(presentacion=True)
    main_event = (
        main_event.titulo, main_event.short_texto, main_event.texto, main_event.get_small_thumbnail(), main_event.id)

    bvatw = models.Blog.objects.get(nombre='Buen Viaje por el Mundo').noticias.order_by("-pk")[0]
    bvatw = (
        bvatw.titulo, bvatw.short_text, bvatw.texto, bvatw.get_small_thumbnail("277x185"), bvatw.get_absolute_url())

    return {
        'noticias_principales': main_news,
        'primer_bloque': first,
        'segundo_bloque_1': second[:3],
        'segundo_bloque_2': second[3:6],
        'evento_principal': main_event,
        'buen_viaj_mundo': bvatw
    }


def home_data_english():
    news_to_publish = models.Noticia.objects.filter(blog=None, position='principal').order_by("-fecha_publicacion",
                                                                                              "sort_order")
    main_news = [(main_news.en_titulo, main_news.en_short_text, main_news.get_small_thumbnail("264x185").url,
                  main_news.get_absolute_url(), main_news.id) for main_news in news_to_publish]
    first = [(x.en_titulo, x.en_short_text, x.get_small_thumbnail("120x90").url, x.get_absolute_url(), x.id) for x in
             models.Noticia.objects.filter(blog=None, position='p_bloque').order_by("-fecha_publicacion",
                                                                                    "sort_order")]

    second = [(x.en_titulo, x.get_small_thumbnail("120x90").url, x.get_absolute_url(), x.id) for x in
              models.Noticia.objects.filter(blog=None, position='s_bloque', show=True).order_by("-fecha_publicacion",
                                                                                                "sort_order")]
    main_event = models.Eventos.objects.get(presentacion=True)
    main_event = (
        main_event.en_titulo, main_event.en_short_texto, main_event.en_texto, main_event.get_small_thumbnail())

    bvatw = models.Blog.objects.get(nombre='Buen Viaje por el Mundo').noticias.order_by("-pk")[0]
    bvatw = (bvatw.en_titulo, bvatw.en_short_text, bvatw.en_texto, bvatw.get_small_thumbnail("277x185"),
             bvatw.get_absolute_url())

    return {
        'noticias_principales': main_news,
        'primer_bloque': first,
        'segundo_bloque_1': second[:3],
        'segundo_bloque_2': second[3:6],
        'evento_principal': main_event,
        'buen_viaj_mundo': bvatw,
    }


# data = calculate_all_data()

# news_data_es = home_data_spanish()

# news_data_en = home_data_english()


def recalculate_all_data():
    print("calling me")
    global data, news_data_en, news_data_es
    data = calculate_all_data()
    news_data_es = home_data_spanish()
    news_data_en = home_data_english()


def inicio(request):
    if settings.NEED_TO_RECALCULATE:
        recalculate_all_data()
        settings.NEED_TO_RECALCULATE = False

    pics = [(x.to_show(), x.id, x.to_show_other_big(), x.usuario.nombre, x.descripcion, len(x.comentarios.all())) for x
            in models.Seccion_Imagenes_Imagen.objects.annotate(num_com=Count('comentarios')).order_by('-num_com')[0:4]]
    try:
        if request.COOKIES['language'] == 'es':
            try:
                keyword = models.KeyWord.objects.get(is_index=True)
            except models.KeyWord.DoesNotExist:
                keyword = None

            a = {'language': 'es',
                 'keyword': keyword,
                 'pics': pics
                 }
            a.update(data)
            a.update(news_data_es)

            return render(request, 'new_inicio.html', a)
        else:
            try:
                keyword = models.KeyWord.objects.get(is_index=True)
            except models.KeyWord.DoesNotExist:
                keyword = None
            a = {'language': 'en',
                 'keyword': keyword,
                 'pics': pics
                 }
            a.update(data)
            a.update(news_data_en)
            to_return = render(request, 'new_inicio_en.html', a)

            HttpResponse.set_cookie(to_return, key="buenviaje_idioma", value="en")
            return to_return
    except KeyError:
        try:
            keyword = models.KeyWord.objects.get(is_index=True)
        except models.KeyWord.DoesNotExist:
            keyword = None

        a = {'language': 'es',
             'keyword': keyword,
             'pics': pics
             }
        a.update(data)
        a.update(news_data_es)

        to_return = render(request, 'new_inicio.html', a)

        HttpResponse.set_cookie(to_return, key="language", value="es")
        return to_return


def la_revista(request):
    if settings.NEED_TO_RECALCULATE:
        recalculate_all_data()
        settings.NEED_TO_RECALCULATE = False

    if request.method == 'GET':
        revistas = models.Seccion_La_Revista.objects.all()
        revista = revistas[len(revistas) - 1]
        n = now()
        try:
            dist = models.Seccion_Distribucion.objects.get(anho=n.year)
        except models.Seccion_Distribucion.DoesNotExist:
            dist = models.Seccion_Distribucion.objects.get(anho=2015)
        try:
            if request.GET['language'] == 'es':
                secciones = [(x.titulo, x.descripcion, x.pk, x.image) for x in revista.secciones.all()]
                d = {
                    'language': 'es',
                    'encabezado': revista.encabezado_revista,
                    'encabezado_seccion': revista.encabezado_seccion,
                    'encabezado_distribucion': dist.encabezado,
                    'anho': dist.anho,
                    'imagen': dist.imagen.url,
                    'texto': dist.texto,
                    'secciones': secciones,
                }
                d.update(data)
                return render(request, 'seccion_la_revista.html', d)
            else:
                secciones = [(x.en_titulo, x.en_descripcion, x.pk, x.image) for x in revista.secciones.all()]
                d = {
                    'language': 'en',
                    'encabezado': revista.en_encabezado_revista,
                    'encabezado_seccion': revista.en_encabezado_seccion,
                    'encabezado_distribucion': dist.en_encabezado,
                    'anho': dist.anho,
                    'imagen': dist.imagen.url,
                    'texto': dist.en_texto,
                    'secciones': secciones
                }
                d.update(data)
                return render(request, 'seccion_la_revista_en.html',
                              d)
        except KeyError:
            secciones = [(x.titulo, x.descripcion, x.pk, x.image) for x in revista.secciones.all()]
            d = {
                'language': 'es',
                'encabezado': revista.encabezado_revista,
                'encabezado_seccion': revista.encabezado_seccion,
                'encabezado_distribucion': dist.encabezado,
                'anho': dist.anho,
                'imagen': dist.imagen.url,
                'texto': dist.texto,
                'secciones': secciones,
            }
            d.update(data)
            return render(request, 'seccion_la_revista.html', d)


def distribucion(request):
    if settings.NEED_TO_RECALCULATE:
        recalculate_all_data()
        settings.NEED_TO_RECALCULATE = False

    if request.method == 'GET':
        n = now()
        try:
            dist = models.Seccion_Distribucion.objects.get(anho=n.year)
        except models.Seccion_Distribucion.DoesNotExist:
            dist = models.Seccion_Distribucion.objects.get(anho=2015)
        try:
            if request.COOKIES['language'] == 'es':
                d = {
                    'language': 'es',
                    'anho': dist.anho,
                    'imagen': dist.imagen.url,
                    'texto': dist.texto,
                    'encabezado': dist.encabezado
                }
                d.update(data)
                return render(request, 'distribucion.html',
                              d)
            else:
                d = {
                    'language': 'en',
                    'anho': dist.anho,
                    'imagen': dist.imagen.url,
                    'texto': dist.en_texto,
                    'encabezado': dist.en_encabezado
                }
                d.update(data)
                return render(request, 'distribucion_en.html',
                              d)
        except KeyError:
            d = {
                'language': 'es',
                'anho': dist.anho,
                'imagen': dist.imagen.url,
                'texto': dist.texto,
                'encabezado': dist.encabezado
            }
            d.update(data)
            return render(request, 'distribucion.html',
                          d)


def informacion_general(request):
    if settings.NEED_TO_RECALCULATE:
        recalculate_all_data()
        settings.NEED_TO_RECALCULATE = False

    if request.method == 'GET':
        infos = models.Seccion_Cuba_Informacion_General.objects.all()
        info = infos[len(infos) - 1]
        try:
            if request.COOKIES['language'] == 'es':
                secciones = [(x.titulo, x.texto, x.pk) for x in info.secciones.all()]
                d = {
                    'language': 'es',
                    'titulo': info.texto,
                    'keyword': get_keyword(info),
                    'secciones': secciones
                }
                d.update(data)
                return render(request, 'informacion_general.html',
                              d)
            else:
                secciones = [(x.en_titulo, x.en_texto, x.pk) for x in info.secciones.all()]
                d = {
                    'language': 'en',
                    'titulo': info.en_texto,
                    'keyword': get_keyword(info),
                    'secciones': secciones
                }
                d.update(data)
                return render(request, 'informacion_general_en.html', d)
        except KeyError:
            secciones = [(x.titulo, x.texto, x.pk) for x in info.secciones.all()]
            d = {
                'language': 'es',
                'keyword': get_keyword(info),
                'titulo': info.texto,
                'secciones': secciones
            }
            d.update(data)
            return render(request, 'informacion_general.html', d)


def informacion_destinos(request):
    if settings.NEED_TO_RECALCULATE:
        recalculate_all_data()
        settings.NEED_TO_RECALCULATE = False

    if request.method == 'GET':
        try:
            if request.COOKIES['language'] == 'es':
                destinos = [
                    (x.nombre, x.get_small_thumbnail(), x.descripcion_corta, x.texto, x.id, x.get_big_thumbnail()) for x
                    in models.Seccion_Cuba_Informacion_Destino.objects.all()]
                d = {
                    'language': 'es',
                    'keyword': get_keywords(models.Seccion_Cuba_Informacion_Destino.objects.all()),
                    'destinos': destinos
                }
                d.update(data)
                return render(request, 'informacion_destinos.html', d)
            else:
                destinos = [(x.en_nombre, x.get_small_thumbnail(), x.en_descripcion_corta, x.en_texto, x.id,
                             x.get_big_thumbnail()) for x in models.Seccion_Cuba_Informacion_Destino.objects.all()]
                d = {
                    'language': 'en',
                    'keyword': get_keywords(models.Seccion_Cuba_Informacion_Destino.objects.all()),
                    'destinos': destinos
                }
                d.update(data)
                return render(request, 'informacion_destinos_en.html', d)
        except KeyError:
            destinos = [(x.nombre, x.imagen.url, x.descripcion_corta, x.texto, x.id, x.get_big_thumbnail()) for x in
                        models.Seccion_Cuba_Informacion_Destino.objects.all()]
            d = {
                'language': 'es',
                'keyword': get_keywords(models.Seccion_Cuba_Informacion_Destino.objects.all()),
                'destinos': destinos
            }
            d.update(data)
            return render(request, 'informacion_destinos.html', d)


# DONE: If there is nothing in filter it breaks down.
def imagenes(request):
    if request.is_ajax():
        images = []
        change = 0
        message = ""
        if request.POST['filter'] == 'fecha_down':
            images = [(x.to_show_other_way(), len(x.comentarios.all()), x.id, x.to_show_other_big(), x.usuario.nombre,
                       x.descripcion) for x in models.Seccion_Imagenes_Imagen.objects.all().order_by('-pk')]
            if request.POST['language'] == 'es':
                message = "Imágenes ordenadas por fecha (primero las más recientes)"
            else:
                message = "Images ordered according to date (the most recent first)"
        elif request.POST['filter'] == 'fecha_up':
            images = [(x.to_show_other_way(), len(x.comentarios.all()), x.id, x.to_show_other_big(), x.usuario.nombre,
                       x.descripcion) for x in models.Seccion_Imagenes_Imagen.objects.all().order_by('pk')]
            if request.POST['language'] == 'es':
                message = "Imágenes ordenadas por fecha (primero las más antiguas)"
            else:
                message = "Images ordered according to date (the most oldest first)"
        elif request.POST['filter'] == 'comentario':
            images = [(x.to_show_other_way(), len(x.comentarios.all()), x.id, x.to_show_other_big(), x.usuario.nombre,
                       x.descripcion) for x in models.Seccion_Imagenes_Imagen.objects.all()]
            images.sort(key=lambda y: y[1], reverse=True)
            if request.POST['language'] == 'es':
                message = "Imágenes ordenadas por cantidad de comentarios"
            else:
                message = "Images ordered according to amount of comments"

        elif request.POST['filter'] == 'user':
            user = request.POST['user']
            if user:
                images = [(x.to_show_other_way(), len(x.comentarios.all()), x.id, x.to_show_other_big(),
                           x.usuario.nombre, x.descripcion) for x in
                          models.Seccion_Imagenes_Imagen.objects.filter(usuario__nombre__iexact=user)]
                if len(images) == 0:
                    if request.POST['language'] == 'es':
                        message = u"No hay fotos subidas por <strong>" + user + u"</strong>"
                    else:
                        message = u"There are no pictures uploaded by <strong>" + user + u"</strong>"
                else:
                    if request.POST['language'] == 'es':
                        message = u"Imágenes subidas por <strong>" + user + u"</strong> (" + str(
                            len(images)) + u' imagénes)'
                    else:
                        message = u"Images uploaded by <strong>" + user + u"</strong> (" + str(
                            len(images)) + u' images)'
            else:
                pass

        elif request.POST['filter'] == 'load':
            try:
                images = [(x.to_show_other_way(), len(x.comentarios.all()), x.id, x.to_show_other_big(),
                           x.usuario.nombre, x.descripcion) for x in
                          models.Seccion_Imagenes_Imagen.objects.annotate(com_count=Count('comentarios')).order_by(
                              '-com_count')[5:]]
            except IndexError:
                images = []
        elif request.POST['filter'] == 'update':
            try:
                ex_last_pk = int(request.POST['last_pk'])
                last_pk = models.Seccion_Imagenes_Imagen.objects.order_by('-pk')[0].pk
                if ex_last_pk != last_pk:
                    images = [(x.to_show_other_way(), len(x.comentarios.all()), x.id, x.to_show_other_big(),
                               x.usuario.nombre, x.descripcion) for x in
                              models.Seccion_Imagenes_Imagen.objects.annotate(com_count=Count('comentarios')).order_by(
                                  '-com_count')]
                    change = 1
                    return HttpResponse(
                        json.dumps({'images': images, 'change': change, 'last_pk': last_pk}, encoding="utf-8"), 'json')
            except KeyError:
                pass
        return HttpResponse(json.dumps({'images': images, 'change': change, 'message': message}, encoding="utf-8"),
                            'json')
    elif request.method == 'GET':
        if settings.NEED_TO_RECALCULATE:
            recalculate_all_data()
            settings.NEED_TO_RECALCULATE = False

        images = [(x.to_show(), len(x.comentarios.all()), x.id, x.to_show_other_big(), x.usuario.nombre, x.descripcion)
                  for x in models.Seccion_Imagenes_Imagen.objects.all()]
        last_pk = models.Seccion_Imagenes_Imagen.objects.order_by('-pk')[0].pk
        images.sort(key=lambda y: y[1], reverse=True)
        # WARNING: Do not change x[1] otherwise the page breaks down!
        res = [(x[0], x[2], x[3], x[4], x[5], x[1]) for x in images[:5]]
        try:
            if request.COOKIES['language'] == 'es':
                d = {
                    'language': 'es',
                    'images': res,
                    'last_pk': last_pk
                }
                d.update(data)
                return render(request, 'imagenes.html', d)
            else:
                d = {
                    'language': 'en',
                    'images': res,
                    'last_pk': last_pk
                }
                d.update(data)
                return render(request, 'imagenes_en.html', d)
        except KeyError:
            d = {
                'language': 'es',
                'images': res
            }
            d.update(data)
            return render(request, 'imagenes.html', d)


# DONE: Prepare this to send notifications emails
def imagen(request, id):
    if request.method == 'GET':
        if settings.NEED_TO_RECALCULATE:
            recalculate_all_data()
            settings.NEED_TO_RECALCULATE = False

        if "width" in request.GET:
            ancho = request.GET['width']
            alto = request.GET['height']

            ancho = int(ancho) - 120

            if int(alto) > 450:
                alto = str(450)

            imagen_small = models.Seccion_Imagenes_Imagen.objects.get(pk=int(id)).to_show_sizes(
                str(ancho) + "x" + alto).url
            imagen = models.Seccion_Imagenes_Imagen.objects.get(pk=int(id))
            d = {
                'image': imagen,
                'imagen_url': imagen_small,
                'id': imagen.id,
                'number_comentarios': len(imagen.comentarios.all()),
            }
            d.update(data)
        else:
            imagen = models.Seccion_Imagenes_Imagen.objects.get(pk=int(id))
            d = {
                'image': imagen,
                'imagen_url': imagen.to_show_big().url,
                'id': imagen.id,
                'number_comentarios': len(imagen.comentarios.all()),
            }
            d.update(data)

        d.update(data)

        try:
            if request.COOKIES['language'] == 'es':
                a = {
                    'language': 'es',
                }
                d.update(a)
                return render(request, 'imagen.html', d)
            else:
                a = {
                    'language': 'en',
                }
                d.update(a)
                return render(request, 'imagen_en.html', d)
        except KeyError:
            a = {
                'language': 'es',
            }
        d.update(a)
        return render(request, 'imagen.html', d)
    elif request.is_ajax():
        if "texto" in request.POST:
            # Being inside here means the page is sending a comment
            nombre = request.POST['nombre']
            correo = request.POST['email']
            texto = request.POST['texto']

            news = models.Seccion_Imagenes_Imagen.objects.get(pk=int(id))

            if correo:
                try:
                    usuario, _ = models.User.objects.get_or_create(correo=correo)
                    usuario.nombre = nombre
                    usuario.save()
                except ValidationError:
                    return HttpResponse(json.dumps({'error': 'mail'}, encoding="utf-8"), 'json')
            else:
                usuario = models.User.objects.create(nombre=nombre)

            if "noti" in request.POST:
                comentario = models.Comentarios.objects.create(usuario=usuario, recibir_notificaciones=True,
                                                               fecha=now(), imagen=news, texto=texto)
            else:
                comentario = models.Comentarios.objects.create(usuario=usuario, recibir_notificaciones=False,
                                                               fecha=now(), imagen=news, texto=texto)
            comentario.save()

            pk_coment = int(request.POST['pk_last_comment'])

            new_comments = models.Comentarios.objects.filter(imagen__pk=int(id), id__gt=int(pk_coment)).order_by(
                'fecha')
            try:
                if request.POST['language'] == 'es':
                    dicc = [(x.usuario.nombre, x.texto, x.id, edit_fecha(x.fecha, 'es')) for x in new_comments.all()]
                else:
                    dicc = [(x.usuario.nombre, x.texto, x.id, edit_fecha(x.fecha, 'en')) for x in new_comments.all()]
            except KeyError:
                dicc = [(x.usuario.nombre, x.texto, x.id, edit_fecha(x.fecha, 'es')) for x in new_comments.all()]

            a = HttpResponse(json.dumps({'comentarios': dicc}, encoding="utf-8"), 'json')
            if usuario.nombre and usuario.nombre != u'' and usuario.nombre != "(Anonymous)":
                HttpResponse.set_cookie(a, key="buenviaje_usuario", value=usuario.nombre)
            else:
                HttpResponse.delete_cookie(a, key="buenviaje_usuario")
            if usuario.correo:
                HttpResponse.set_cookie(a, key="buenviaje_correo", value=usuario.correo)
            else:
                HttpResponse.delete_cookie(a, key="buenviaje_correo")

            if "noti" in request.POST:
                HttpResponse.set_cookie(a, key="buenviaje_notify", value="true")
            else:
                HttpResponse.delete_cookie(a, key="buenviaje_notify")
                for com in models.Comentarios.objects.filter(imagen__pk=int(id), usuario=usuario):
                    com.recibir_notificaciones = False
                    com.save()
                img = models.Seccion_Imagenes_Imagen.objects.get(pk=int(id))
                if img.usuario == usuario:
                    if "noti" in request.POST:
                        img.recibir_notificaciones = True
                    else:
                        img.recibir_notificaciones = False
                    img.save()

            if 'buenviaje_idioma' in request.COOKIES:
                t = Thread(target=send_mails, args=(news, comentario.pk, request.COOKIES['buenviaje_idioma']))
            else:
                t = Thread(target=send_mails, args=(news, comentario.pk, "es"))
            t.start()

            return a
        else:
            pk_coment = request.POST['pk_last_comment']
            if "old" in request.POST:
                # The page wants the old comments
                new_comments = models.Comentarios.objects.filter(imagen__pk=id, id__lt=int(pk_coment)).order_by(
                    '-fecha')
            else:
                # The page wants the new comments
                new_comments = models.Comentarios.objects.filter(imagen__pk=id, id__gt=int(pk_coment)).order_by('fecha')

            # DONE: Fix the to send the datetime in a string which should be language sensitive, i.e. It should says: "El 4 de abril de 2015 a las 7:10 fulanito comentó"
            # DONE: Ver lo del timezone pq a roly no le funciona
            # DONE: Is better to do this here than in the browser. This implies changing a little bit the method insert_comments in ajax_prep.js

            try:
                if request.POST['language'] == 'es':
                    dicc = [(x.usuario.nombre, x.texto, x.id, edit_fecha(x.fecha, 'es')) for x in new_comments.all()]
                else:
                    dicc = [(x.usuario.nombre, x.texto, x.id, edit_fecha(x.fecha, 'en')) for x in new_comments.all()]
            except KeyError:
                dicc = [(x.usuario.nombre, x.texto, x.id, edit_fecha(x.fecha, 'es')) for x in new_comments.all()]
            return HttpResponse(json.dumps({'comentarios': dicc}, encoding="utf-8"), 'json')


def tiempo_libre(request):
    if request.method == 'GET':
        if settings.NEED_TO_RECALCULATE:
            recalculate_all_data()
            settings.NEED_TO_RECALCULATE = False
        try:
            if request.COOKIES['language'] == 'es':
                tl = models.Seccion_Tiempo_Libre.objects.order_by('-pk').all()
                d = {
                    'language': 'es',
                    'keyword': get_keywords(tl),
                    'actividades': tl
                }
                d.update(data)
                return render(request, 'tiempo_libre.html', d)
            else:
                tl = models.Seccion_Tiempo_Libre.objects.order_by('-pk').all()
                d = {
                    'language': 'en',
                    'keyword': get_keywords(tl),
                    'actividades': tl
                }
                d.update(data)
                return render(request, 'tiempo_libre_en.html', d)
        except KeyError:
            tl = models.Seccion_Tiempo_Libre.objects.order_by('-pk').all()
            d = {
                'language': 'es',
                'keyword': get_keywords(tl),
                'actividades': tl
            }
            d.update(data)
            return render(request, 'tiempo_libre.html', d)


# DONE: This needs to recieve the month
def eventos(request):
    return eventos_month(request, now().month)


def eventos_month(request, month):
    if request.method == 'GET':
        if settings.NEED_TO_RECALCULATE:
            recalculate_all_data()
            settings.NEED_TO_RECALCULATE = False

        try:
            month = fix_month(month, True)
        except:
            month = fix_month(month)
        t = now()
        events = models.Eventos.objects.filter(fecha_inicio__month=month[0], fecha_inicio__year=t.year)
        years = models.Eventos.objects.filter(fecha_inicio__year=t.year)
        months = []

        for x in years:
            if x.fecha_inicio.month not in months and 2 >= x.fecha_inicio.month - t.month > -1:
                months.append(x.fecha_inicio.month)
        try:
            if request.COOKIES['language'] == 'es':
                d = {
                    'mes_actual': month,
                    'language': 'es',
                    'keyword': get_keywords(events),
                    'eventos': events,
                    'months': fix_months(months)
                }
                d.update(data)
                return render(request, 'eventos.html', d)
            else:
                # events = [(x.en_titulo, x.imagen, x.fecha_inicio, x.fecha_final, x.en_comite, fix_coma(x.email), x.fax, x.provincia, x.en_receptivo, x.en_sede, x.telefono, fix_coma(x.web)) for x in models.Eventos.objects.all()]
                d = {
                    'mes_actual': month,
                    'language': 'en',
                    'keyword': get_keywords(events),
                    'eventos': events,
                    'months': fix_months(months)
                }
                d.update(data)
                return render(request, 'eventos_en.html', d)
        except KeyError:
            d = {
                'mes_actual': month,
                'language': 'es',
                'keyword': get_keywords(events),
                'eventos': events,
                'months': fix_months(months)
            }
            d.update(data)
            return render(request, 'eventos.html', d)


def proximo_anho(request):
    if request.method == 'GET':
        if settings.NEED_TO_RECALCULATE:
            recalculate_all_data()
            settings.NEED_TO_RECALCULATE = False

        events = models.Eventos.objects.filter(fecha_inicio__year=now().year + 1)
        try:
            if request.COOKIES['language'] == "es":
                d = {'language': 'es', 'events': events, 'anho': now().year + 1}
                d.update(data)
                return render(request, 'proximo_anho.html', d)
            else:
                d = {'language': 'en', 'events': events, 'anho': now().year + 1}
                d.update(data)
                return render(request, 'proximo_anho_en.html', d)
        except KeyError:
            d = {'language': 'es', 'events': events, 'anho': now().year + 1}
            d.update(data)
            return render(request, 'proximo_anho.html', d)


def get_keyword(item):
    if item.keywords.count():
        keyword = item.keywords.all()[0]
    else:
        keyword = None
    return keyword


def get_keywords(list_items):
    keyword = [x.keywords.all()[0] if x.keywords.count() else None for x in list_items]
    res = []
    for x in keyword:
        if x:
            for y in x.keywords.split(','):
                res.append(y.strip())
    return set(res)


def noticia(request, slug):
    if request.method == 'GET':
        if settings.NEED_TO_RECALCULATE:
            recalculate_all_data()
            settings.NEED_TO_RECALCULATE = False
        try:
            news = models.Noticia.objects.get(slug=slug)
        except models.Noticia.DoesNotExist:
            raise Http404("Esa noticia no existe")

        a = {
            'noticia': news,
            'id': news.id,
            'keyword': get_keyword(news),
            'number_comentarios': len(news.comentarios.all()),
            'comentarios': news.comentarios.all(),
            'allow_comments': news.allow_comments,
        }

        try:
            if request.COOKIES['language'] == 'es':
                d = {
                    'language': 'es',
                }
                d.update(a)
                d.update(data)
                return render(request, 'noticia.html', d)
            else:
                d = {
                    'language': 'en',
                }
                d.update(a)
                d.update(data)
                return render(request, 'noticia_en.html', d)
        except KeyError:
            d = {
                'language': 'es',
            }
            d.update(a)
            d.update(data)
            return render(request, 'noticia.html', d)


def fix_minute(minute):
    if minute < 10:
        return '0' + str(minute)
    return str(minute)


def edit_fecha(fecha, language):
    fecha_new = fecha.astimezone(tz=get_current_timezone())
    if language == 'es':
        return 'El ' + str(fecha_new.day) + ' de ' + str(fix_month(fecha_new.month)[1]) + ' de ' + str(
            fecha_new.year) + ' a las ' + str(fecha_new.hour) + ':' + fix_minute(fecha_new.minute)
    else:
        return 'On ' + str(fix_month(fecha_new.month)[2]) + ' ' + str(fecha_new.day) + ', ' + str(
            fecha_new.year) + ' at ' + str(fecha_new.hour) + ':' + fix_minute(fecha_new.minute)


def split_fecha(fecha):
    return str(fecha.year) + '-' + str(fecha.month) + '-' + str(fecha.day), str(fecha.hour) + ':' + str(fecha.minute)


def photo(request):
    return render(request, 'photo.html',
                  {
                  })


def noticias(request):
    if request.method == 'GET':
        if settings.NEED_TO_RECALCULATE:
            recalculate_all_data()
            settings.NEED_TO_RECALCULATE = False

        news = {}
        for x in models.Noticia.objects.filter(fecha_publicacion__year=now().year):
            month = fix_month(x.fecha_publicacion.month)
            try:
                news[month].append(x)
            except KeyError:
                news[month] = [x]
        try:
            if request.COOKIES['language'] == 'es':
                d = {
                    'language': 'es',
                    'news': news
                }
                d.update(data)
                return render(request, 'noticias.html', d)
            else:
                d = {
                    'language': 'en',
                    'news': news
                }
                d.update(data)
                return render(request, 'noticias_en.html', d)
        except KeyError:
            d = {
                'language': 'es',
                'news': news
            }
            d.update(data)
            return render(request, 'noticias.html', d)


def unsubscribe(request):
    if request.method == 'GET':
        try:
            element = models.Noticia.objects.get(pk=int(request.GET['new']))
        except KeyError:
            element = models.Seccion_Imagenes_Imagen.objects.get(pk=int(request.GET['image']))
        mail = request.GET['mail']
        for x in element.comentarios.filter(usuario__correo=mail):
            x.recibir_notificaciones = False
            x.save()
        return render(request, 'unsubscribe.html', {})


def de_cuba(request):
    if settings.NEED_TO_RECALCULATE:
        recalculate_all_data()
        settings.NEED_TO_RECALCULATE = False
    try:
        language = request.COOKIES['language']
        if language == "es":
            d = {
                'language': "es",
                'title_url': ("Información General", "/informacion_general/"),
                'title_url_1': ("Información por destinos", "/informacion_destinos/")
            }
            d.update(data)
            return render(request, 'de_cuba.html', d)
        else:
            d = {
                'language': "en",
                'title_url': ("General Information", "/informacion_general/"),
                'title_url_1': ("Information according to destination", "/informacion_destinos/")
            }
            d.update(data)
            return render(request, 'de_cuba_en.html', d)
    except KeyError:
        d = {
            'language': "es",
            'title_url': ("Información General", "/informacion_general/"),
            'title_url_1': ("Información por destinos", "/informacion_destinos/")
        }
        d.update(data)
        return render(request, 'de_cuba.html', d)


def old_revistas(request):
    if settings.NEED_TO_RECALCULATE:
        recalculate_all_data()
        settings.NEED_TO_RECALCULATE = False

    if request.method == "GET":
        try:
            anho = int(request.GET['anho'])
        except KeyError:
            anho = now().year

        revistas_normal = models.Revista.objects.filter(anho=anho, tipo="Normal").order_by("numero")
        revistas_especial = models.Revista.objects.filter(anho=anho, tipo="Especial").order_by("numero")
        rev = [None, None, None, None]
        rev_es = [None, None]
        fotos_es = [None, None, None, None]
        fotos_es_es = [None, None]
        fotos_en = [None, None, None, None]
        fotos_es_en = [None, None]
        for x in revistas_especial:
            if x.numero == 1:
                try:
                    rev_es[0].append(x)
                except AttributeError:
                    rev_es[0] = [x]
                if x.idioma == u'Español':
                    fotos_es_es[0] = x.get_small_thumbnail()
                if x.idioma == u'Inglés':
                    fotos_es_en[0] = x.get_small_thumbnail()
                if not fotos_es_es[0]:
                    fotos_es_es[0] = x.get_small_thumbnail()
                if not fotos_es_en[0]:
                    fotos_es_en[0] = x.get_small_thumbnail()
            elif x.numero == 2:
                try:
                    rev_es[1].append(x)
                except AttributeError:
                    rev_es[1] = [x]
                if x.idioma == u'Español':
                    fotos_es_es[1] = x.get_small_thumbnail()
                if x.idioma == u'Inglés':
                    fotos_es_en[1] = x.get_small_thumbnail()
                if not fotos_es_es[1]:
                    fotos_es_es[1] = x.get_small_thumbnail()
                if not fotos_es_en[1]:
                    fotos_es_en[1] = x.get_small_thumbnail()
        for x in revistas_normal:
            if x.numero == 1:
                try:
                    rev[0].append(x)
                except AttributeError:
                    rev[0] = [x]
                if x.idioma == u'Español':
                    fotos_es[0] = x.get_small_thumbnail()
                if x.idioma == u'Inglés':
                    fotos_en[0] = x.get_small_thumbnail()
                if not fotos_es[0]:
                    fotos_es[0] = x.get_small_thumbnail()
                if not fotos_en[0]:
                    fotos_en[0] = x.get_small_thumbnail()
            elif x.numero == 2:
                try:
                    rev[1].append(x)
                except AttributeError:
                    rev[1] = [x]
                if x.idioma == u'Español':
                    fotos_es[1] = x.get_small_thumbnail()
                if x.idioma == u'Inglés':
                    fotos_en[1] = x.get_small_thumbnail()
                if not fotos_es[1]:
                    fotos_es[1] = x.get_small_thumbnail()
                if not fotos_en[1]:
                    fotos_en[1] = x.get_small_thumbnail()
            elif x.numero == 3:
                try:
                    rev[2].append(x)
                except AttributeError:
                    rev[2] = [x]
                if x.idioma == u'Español':
                    fotos_es[2] = x.get_small_thumbnail()
                if x.idioma == u'Inglés':
                    fotos_en[2] = x.get_small_thumbnail()
                if not fotos_es[2]:
                    fotos_es[2] = x.get_small_thumbnail()
                if not fotos_en[2]:
                    fotos_en[2] = x.get_small_thumbnail()
            elif x.numero == 4:
                try:
                    rev[3].append(x)
                except AttributeError:
                    rev[3] = [x]
                if x.idioma == u'Español':
                    fotos_es[3] = x.get_small_thumbnail()
                if x.idioma == u'Inglés':
                    fotos_en[3] = x.get_small_thumbnail()
                if not fotos_es[3]:
                    fotos_es[3] = x.get_small_thumbnail()
                if not fotos_en[3]:
                    fotos_en[3] = x.get_small_thumbnail()
        anhos = []
        for x in models.Revista.objects.all():
            if x.anho not in anhos:
                anhos.append(x.anho)
        anhos.sort()
        d = {
            'anho': anho,
            'revistas': rev,
            'revistas_es': rev_es,
            'anhos': anhos

        }

        try:
            language = request.COOKIES['language']
            if language == "es":

                lang = {
                    'language': "es",
                    'fotos': fotos_es,
                    'fotos_es': fotos_es_es
                }
                d.update(data)
                d.update(lang)
                return render(request, 'old_revistas.html', d)
            else:
                lang = {
                    'language': "en",
                    'fotos': fotos_en,
                    'fotos_es': fotos_es_en
                }
                d.update(lang)
                d.update(data)
                return render(request, 'old_revistas_en.html', d)
        except KeyError:
            lang = {
                'language': "es",
                'fotos': fotos_es,
                'fotos_es': fotos_es_en
            }
            d.update(lang)
            d.update(data)
            return render(request, 'old_revistas.html', d)

    else:
        pass


def error(request):
    raise Http404(u'Esta página no existe')


# DONE: Fix double uploading from /images/
def ajax_photo_upload(request):
    response_data = {}

    if request.is_ajax():
        foto = request.FILES['upload']
        nombre = request.POST['name']
        email = request.POST['email']
        pic_description = request.POST['pic_description']

        notifyme = False
        if 'notifications' in request.POST:
            notifyme = True

        # DONE: Anonimo y Anonymous are not allowed names.
        # DONE: See what to do when people have same name but different emails.
        # DONE: foto requires some other fields.
        # DONE: foto's save method is not saving rigth the dates.
        # DONE: How to find out if pictures are the same (check for file name?)
        upload = None
        try:
            if pic_description:
                if nombre and email:
                    usuario, _ = models.User.objects.get_or_create(correo=email)
                    usuario.nombre = nombre
                    usuario.save()

                    upload = models.Seccion_Imagenes_Imagen(
                        usuario=usuario, recibir_notificaciones=notifyme, descripcion=pic_description
                    )
                else:
                    response_data['status'] = "error"
                    response_data[
                        'result'] = "We're sorry, but something went wrong. Please be sure that your file respects the upload conditions."

                    return HttpResponse(json.dumps(response_data), content_type='application/json')
            else:
                response_data['status'] = "error"
                response_data[
                    'result'] = "We're sorry, but something went wrong. Please be sure that your file respects the upload conditions."

                return HttpResponse(json.dumps(response_data), content_type='application/json')

            upload.foto.save(foto.name, foto, True)

            upload.save()

        except models.ValidationError:
            response_data['status'] = "error"
            response_data[
                'result'] = "We're sorry, but something went wrong. Please be sure that your file respects the upload conditions."
            from BuenViaje import settings

            path = settings.BASE_DIR + os.sep + upload.foto.url
            # print(path)
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    print(e.message)
            return HttpResponse(json.dumps(response_data), content_type='application/json')

        response_data['status'] = "success"
        response_data['result'] = "Your file has been uploaded:"
        response_data['fileLink'] = "/%s" % upload.foto.url

        return HttpResponse(json.dumps(response_data), content_type="application/json")

    response_data['status'] = "error"
    response_data[
        'result'] = "We're sorry, but something went wrong. Please be sure that your file respects the upload conditions."

    return HttpResponse(json.dumps(response_data), content_type='application/json')


def ajax_noticias(request, id):
    # DONE: Prepare this for "Recibir notificaciones". Check that you can't receive notifications if you don't provide an email.
    # DONE: Start working on the pictures.
    if request.method == 'POST':
        if "texto" in request.POST:
            # Being inside here means the page is sending a comment
            nombre = request.POST['nombre']
            correo = request.POST['email']
            texto = request.POST['texto']

            news = models.Noticia.objects.get(pk=int(id))

            if correo:
                try:
                    usuario, _ = models.User.objects.get_or_create(correo=correo)
                    usuario.nombre = nombre
                    usuario.save()
                except ValidationError:
                    return HttpResponse(json.dumps({'error': 'mail'}, encoding="utf-8"), 'json')
            else:
                usuario = models.User.objects.create(nombre=nombre)

            if "noti" in request.POST:
                comentario = models.Comentarios.objects.create(usuario=usuario, recibir_notificaciones=True,
                                                               fecha=now(), noticia=news, texto=texto)
            else:
                comentario = models.Comentarios.objects.create(usuario=usuario, recibir_notificaciones=False,
                                                               fecha=now(), noticia=news, texto=texto)
            comentario.save()

            pk_coment = int(request.POST['pk_last_comment'])

            new_comments = models.Comentarios.objects.filter(noticia__pk=int(id), id__gt=int(pk_coment)).order_by(
                'fecha')
            try:
                if request.POST['language'] == 'es':
                    dicc = [(x.usuario.nombre, x.texto, x.id, edit_fecha(x.fecha, 'es')) for x in new_comments.all()]
                else:
                    dicc = [(x.usuario.nombre, x.texto, x.id, edit_fecha(x.fecha, 'en')) for x in new_comments.all()]
            except KeyError:
                dicc = [(x.usuario.nombre, x.texto, x.id, edit_fecha(x.fecha, 'es')) for x in new_comments.all()]
            # dicc = [(x.usuario.nombre, x.texto, x.id, edit_fecha(x.fecha)) for x in new_comments.all()]

            a = HttpResponse(json.dumps({'comentarios': dicc}, encoding="utf-8"), 'json')
            if usuario.nombre and usuario.nombre != u'' and usuario.nombre != "(Anonymous)":
                HttpResponse.set_cookie(a, key="buenviaje_usuario", value=usuario.nombre)
            else:
                HttpResponse.delete_cookie(a, key="buenviaje_usuario")
            if usuario.correo:
                HttpResponse.set_cookie(a, key="buenviaje_correo", value=usuario.correo)
            else:
                HttpResponse.delete_cookie(a, key="buenviaje_correo")

            if "noti" in request.POST:
                HttpResponse.set_cookie(a, key="buenviaje_notify", value="true")
            else:
                HttpResponse.delete_cookie(a, key="buenviaje_notify")
                for com in models.Comentarios.objects.filter(noticia__pk=int(id), usuario=usuario):
                    com.recibir_notificaciones = False
                    com.save()

            if 'buenviaje_idioma' in request.COOKIES:
                t = Thread(target=send_mails, args=(news, comentario.pk, request.COOKIES['buenviaje_idioma']))
            else:
                t = Thread(target=send_mails, args=(news, comentario.pk, "es"))
            t.start()

            return a
        else:
            pk_coment = request.POST['pk_last_comment']
            if "old" in request.POST:
                # The page wants the old comments
                new_comments = models.Comentarios.objects.filter(noticia__pk=id, id__lt=int(pk_coment)).order_by(
                    '-fecha')
            else:
                # The page wants the new comments
                new_comments = models.Comentarios.objects.filter(noticia__pk=id, id__gt=int(pk_coment)).order_by(
                    'fecha')

            # DONE: Fix the to send the datetime in a string which should be language sensitive, i.e. It should says: "El 4 de abril de 2015 a las 7:10 fulanito comentó"
            # DONE: Ver lo del timezone pq a roly no le funciona
            # DONE: Is better to do this here than in the browser. This implies changing a little bit the method insert_comments in ajax_prep.js

            try:
                if request.POST['language'] == 'es':
                    dicc = [(x.usuario.nombre, x.texto, x.id, edit_fecha(x.fecha, 'es')) for x in new_comments.all()]
                else:
                    dicc = [(x.usuario.nombre, x.texto, x.id, edit_fecha(x.fecha, 'en')) for x in new_comments.all()]
            except KeyError:
                dicc = [(x.usuario.nombre, x.texto, x.id, edit_fecha(x.fecha, 'es')) for x in new_comments.all()]
            return HttpResponse(json.dumps({'comentarios': dicc}, encoding="utf-8"), 'json')


# DONE: Do the template!!!!!!
def send_mails(current_news, id_comentario, lang):
    try:
        connection = get_connection()
        connection.open()
        to_send = get_user_notify(current_news)
        comment = models.Comentarios.objects.get(pk=id_comentario)
        html = get_template('email.html')

        for x in to_send:
            print(x)
            publicacion = []
            img = False
            user = x[2]

            if user == comment.usuario:
                continue

            if comment.noticia:
                publicacion = comment.noticia
            elif comment.imagen:
                img = True
                publicacion = comment.imagen

            context = Context({
                'site': settings.WEB_PAGE_URL,
                'comentario': comment.texto,
                'publicacion': publicacion
            })

            if lang == "es":
                if img and publicacion.usuario == user:
                    a = {
                        'language': "es",
                        'texto': comment.usuario.nombre + u" ha hecho un comentario en una foto subida por usted:",
                    }
                else:
                    a = {
                        'language': "es",
                        'texto': comment.usuario.nombre + u" ha hecho un comentario en una publiación que usted ha comentado:",
                    }
            else:
                if img and publicacion.usuario == user:
                    a = {
                        'language': lang,
                        'texto': comment.usuario.nombre + u" has made a comment on a picture uploaded by you:",
                    }
                else:
                    a = {
                        'language': lang,
                        'texto': comment.usuario.nombre + u" has made a comment on a publication you commented before:",
                    }

            context.update(a)

            html_message = html.render(context)

            message = EmailMultiAlternatives(
                u'Notificación de Buen Viaje a Cuba', comment.texto,
                from_email='Buen Viaje a Cuba <buenviajeacuba@buenviajeacuba.com>',
                to=[u'%s <%s>' % (x[1], x[0])], connection=connection
            )

            message.attach_alternative(
                html_message,
                "text/html"
            )
            try:
                message.send()
                print('correo enviado a ' + x[0] + "<" + x[1] + ">")
            except Exception as e:
                print e.message

        connection.close()

    except Exception as e:
        print e.message


def contains(elemnto, lista):
    for x in lista:
        if x[0] == elemnto.usuario.correo:
            return False
    return True


def remove_dirt_data(collection):
    res = []
    for x in collection:
        for y in string.punctuation:
            x = x.replace(y, '')
        x.strip()
        res.append(x)
    return res


def match(query, text):
    if text:
        _bool = True
        t = remove_dirt_data(text.strip().split())
        for word_query in query:
            if _bool:
                _bool = False
                for word in t:
                    if word_query.lower() in word.lower():
                        _bool = True
                        break
            else:
                return False
        return _bool
    return False


# TODO: Just search in active months
def search(request):
    if settings.NEED_TO_RECALCULATE:
        recalculate_all_data()
        settings.NEED_TO_RECALCULATE = False

    if request.method == 'POST':
        language = 'en'
        if request.POST['language'] == 'es':
            language = 'es'
        query_words = request.POST['query'].strip().split()
        if not len(query_words):
            try:
                language = request.POST['language']
            except KeyError:
                language = "es"

            d = {
                'language': language,
                'total': -1
            }
            d.update(data)
            if language == 'es':
                return render(request, 'search.html', d)
            else:
                return render(request, 'search_en.html', d)

        events = []
        news = []
        magazines = []
        free_time = []
        secciones_rev = []
        dist = []
        info_dest = []
        info_gen_cuba = []
        secciones_info_gen = []
        if language == 'es':
            # for event in models.Eventos.objects.filter(fecha_inicio__gt=now()).all():
            for event in models.Eventos.objects.all():
                if match(query_words, event.titulo) or match(query_words, event.provincia) or match(query_words,
                                                                                                    event.sede) or match(
                    query_words, event.comite) or match(query_words, event.web) or match(query_words,
                                                                                         event.email) or match(
                    query_words, event.fax) or match(query_words, event.telefono):
                    events.append(event)
            for new in models.Noticia.objects.all():
                if match(query_words, new.titulo) or match(query_words, new.texto):
                    news.append(new)
            for new in models.Revista.objects.all():
                if match(query_words, new.tipo) or match(query_words, str(new.numero)):
                    magazines.append(new)
            for new in models.Seccion_Tiempo_Libre.objects.all():
                if match(query_words, new.titulo) or match(query_words, new.texto):
                    free_time.append(new)
            for new in models.Seccion_La_Revista.objects.all():
                for sec in new.secciones.all():
                    if match(query_words, sec.titulo) or match(query_words, sec.descripcion):
                        secciones_rev.append(sec)
            for new in models.Seccion_Distribucion.objects.all():
                if match(query_words, new.encabezado) or match(query_words, new.texto):
                    dist.append(new)
            for new in models.Seccion_Cuba_Informacion_Destino.objects.all():
                if match(query_words, new.nombre) or match(query_words, new.texto):
                    info_dest.append(new)
            for new in models.Seccion_Cuba_Informacion_General.objects.all():
                if match(query_words, new.texto):
                    info_gen_cuba.append(new)
                for sec in new.secciones.all():
                    if match(query_words, sec.titulo) or match(query_words, sec.texto):
                        secciones_info_gen.append(sec)
        else:
            for event in models.Eventos.objects.all():
                if match(query_words, event.en_titulo) or match(query_words, event.provincia) or match(query_words,
                                                                                                       event.en_sede) or match(
                    query_words, event.en_comite) or match(query_words, event.web) or match(query_words,
                                                                                            event.email) or match(
                    query_words, event.fax) or match(query_words, event.telefono):
                    events.append(event)
            for new in models.Noticia.objects.all():
                if match(query_words, new.en_titulo) or match(query_words, new.en_texto):
                    news.append(new)
            for new in models.Revista.objects.all():
                if match(query_words, new.tipo) or match(query_words, str(new.numero)):
                    magazines.append(new)
            for new in models.Seccion_Tiempo_Libre.objects.all():
                if match(query_words, new.en_titulo) or match(query_words, new.en_texto):
                    free_time.append(new)
            for new in models.Seccion_La_Revista.objects.all():
                for sec in new.secciones.all():
                    if match(query_words, sec.en_titulo) or match(query_words, sec.en_descripcion):
                        secciones_rev.append(sec)
            for new in models.Seccion_Distribucion.objects.all():
                if match(query_words, new.en_encabezado) or match(query_words, new.en_texto):
                    dist.append(new)
            for new in models.Seccion_Cuba_Informacion_Destino.objects.all():
                if match(query_words, new.en_nombre) or match(query_words, new.en_texto):
                    info_dest.append(new)
            for new in models.Seccion_Cuba_Informacion_General.objects.all():
                if match(query_words, new.en_texto):
                    info_gen_cuba.append(new)
                for sec in new.secciones.all():
                    if match(query_words, sec.en_titulo) or match(query_words, sec.en_texto):
                        secciones_info_gen.append(sec)
        total_results = len(news) + len(events) + len(magazines) + len(free_time) + len(secciones_rev) + len(
            dist) + len(info_dest) + len(info_gen_cuba) + len(secciones_info_gen)
        d = {
            'language': language,
            'news': news,
            'events': events,
            'magazines': magazines.sort(key=lambda x: x.anho),
            'free_time': free_time,
            'la_revista_secciones': secciones_rev,
            'distribuciones': dist,
            'informacion_destinos': info_dest,
            'informacion_general_cuba': info_gen_cuba,
            'informacion_general_cuba_secciones': secciones_info_gen,
            'query': request.POST['query'],
            'total': total_results

        }
        if language == "es":
            d.update(data)
            return render(request, 'search.html', d)
        else:
            d.update(data)
            return render(request, 'search_en.html', d)
    else:
        try:
            language = request.COOKIES['language']
        except KeyError:
            language = "es"

        d = {
            'language': language,
            'total': -1
        }
        d.update(data)
        if language == 'es':
            return render(request, 'search.html', d)
        else:
            return render(request, 'search_en.html', d)


def subscribe(request):
    if request.method == 'GET':
        newsletters = md_newsletter.Newsletter.objects.all()
        return render(request, 'subscribe_newsletter.html',
                      {
                          'language': 'es',
                          'newsletter': newsletters
                      })
    if request.is_ajax():
        name = request.POST['name']
        mail = request.POST['mail']
        newsletter = int(request.POST['id_newsletter'])
        response_data = {}
        try:
            news = md_newsletter.Newsletter.objects.get(pk=newsletter)
            obj, _ = md_newsletter.Subscription.objects.get_or_create(email_field=mail, subscribed=True,
                                                                      newsletter=news)
            obj.name_field = name
            # obj = md_newsletter.Subscription.objects.create(name_field=name, email_field=mail, subscribed=True, newsletter=news)
            obj.save()
        except Exception as e:
            response_data['return'] = 'fail'
            response_data['message'] = e.message
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        response_data['return'] = 'success'
        return HttpResponse(json.dumps(response_data), content_type="application/json")


def contactenos(request):
    if settings.NEED_TO_RECALCULATE:
        recalculate_all_data()
        settings.NEED_TO_RECALCULATE = False

    if request.is_ajax():
        response_data = {}
        try:
            asunto = request.POST['asunto']
            mail = request.POST['email']
            texto = request.POST['texto']
            send_mail(subject=asunto, from_email=mail, message=texto,
                      recipient_list=("buenviajeacuba@buenviajeacuba.com",))
            response_data['status'] = "Success"
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except Exception as e:
            print e.message
            response_data['status'] = "Error"
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        try:
            if request.COOKIES['language'] == 'es':
                d = {
                    'language': request.COOKIES['language'],
                }
                d.update(data)
                return render(request, 'contactenos.html', d)
            else:
                d = {
                    'language': request.COOKIES['language'],
                }
                d.update(data)
                return render(request, 'contactenos_en.html', d)
        except KeyError:
            d = {
                'language': "es",
            }
            d.update(data)
            return render(request, 'contactenos.html', d)


def notification(request):
    user = models.User.objects.get(pk=7)
    comment = models.Comentarios.objects.get(pk=7)
    publicacion = []
    img = False
    if comment.noticia:
        publicacion = comment.noticia
    elif comment.imagen:
        img = True
        publicacion = comment.imagen

    d = {
        'comentario': comment.texto,
        'publicacion': publicacion
    }
    try:
        language = request.COOKIES['language']
        if language == "es":
            if img and publicacion.usuario == user:
                a = {
                    'language': language,
                    'texto': user.nombre + u" ha hecho un comentario en una foto subida por usted:",
                }
            else:
                a = {
                    'language': language,
                    'texto': user.nombre + u" ha hecho un comentario en una imagen que usted ha comentado:",
                }
        else:
            if img and publicacion.usuario == user:
                a = {
                    'language': language,
                    'texto': user.nombre + u" has made a comment on a picture uploaded by you:",
                }
            else:
                a = {
                    'language': language,
                    'texto': user.nombre + u" has made a comment on a publication you commented before:",
                }

    except KeyError:
        if img and publicacion.usuario == user:
            a = {
                'language': "es",
                'texto': user.nombre + u" ha hecho un comentario en una foto subida por usted:",
            }
        else:
            a = {
                'language': "es",
                'texto': user.nombre + u" ha hecho un comentario en una imagen que usted ha comentado:",
            }
    d.update(a)

    return render(request, 'email.html', d)  # Get a tuple with all the emails


def get_user_notify(news_pic):
    to_send = []
    try:
        a = news_pic.recibir_notificaciones
        b = news_pic.usuario
        if a and b.correo:
            print(b.nombre)
            if b.nombre != u'':
                to_send.append((b.correo, b.nombre, b))
            else:
                to_send.append((b.correo, "(Anonymous)", b))
    except:
        pass

    for x in news_pic.comentarios.filter(recibir_notificaciones=True).all():
        if contains(x, to_send):
            if x.usuario.nombre != u'':
                to_send.append((x.usuario.correo, x.usuario.nombre, x.usuario))
            else:
                to_send.append((x.usuario.correo, "(Anonymous)", x.usuario))
    return to_send


# DONE: If do directly to an inside URL I have no language so everything shows up in English. Fix this.
def change_language(request):
    if request.COOKIES['language'] == 'es':
        lang = 'en'
    else:
        lang = 'es'
    try:
        ret = HttpResponseRedirect(request.environ['HTTP_REFERER'].split('?')[0])
    except KeyError:
        ret = HttpResponseRedirect('/')
    ret.set_cookie('language', lang)
    return ret
