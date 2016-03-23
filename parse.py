import os
from datetime import date

os.environ['DJANGO_SETTINGS_MODULE'] = 'BuenViaje.settings'
from BuenViajeWebPage import models
import csv


def fix(string):
    string = string.strip().decode('utf-8')
    string = u' '.join(string.split())
    return string


def get_month(month):
    month = month.lower()
    if '.' not in month:
        month += '.'
    if month == 'ene.':
        return 1
    elif month == 'feb.' or month == '2.':
        return 2
    elif month == 'mar.':
        return 3
    elif month == 'abr.' or month == 'apr.':
        return 4
    elif month == 'may.':
        return 5
    elif month == 'jun.':
        return 6
    elif month == 'jul.':
        return 7
    elif month == 'ago.':
        return 8
    elif month == 'sep.':
        return 9
    elif month == 'oct.':
        return 10
    elif month == 'nov.':
        return 11
    elif month == 'dic.' or month == 'dec.':
        return 12
    else:
        print month

# DONE: No event has "sede"
if __name__ == '__main__':
    with open('eventos.csv') as f:
        excel = csv.reader(f)
        count = 1
        for rows in excel:
            name = rows[0].split('/')
            name_es = fix(name[0])
            name_en = fix(name[1])
            month_f1 = rows[1].split('-')
            month_f2 = rows[2].split('-')
            if len(month_f1) == 1:
                f_inicio = date(2015, get_month(month_f1[0]), 1)
                if not month_f2:
                    f_final = date(2015, get_month(month_f1[0]), 31)
            else:
                f_inicio = date(2015, get_month(month_f1[1]), int(month_f1[0]))
                f_final = date(2015, get_month(month_f2[1]), int(month_f2[0]))
            provincia = fix(rows[3])
            sede = fix(rows[4])
            receptivo = fix(rows[5])
            comite = fix(rows[6])
            tel = fix(rows[7])
            fax = fix(rows[8])
            mail = fix(rows[9])
            web = fix(rows[10])
            tmp = models.Eventos.objects.create(titulo=name_es, en_titulo=name_en, fecha_inicio=f_inicio, fecha_final=f_final, provincia=provincia, sede=sede, receptivo=receptivo, comite=comite, telefono=tel, fax=fax, email=mail, web=web)
            tmp.save()