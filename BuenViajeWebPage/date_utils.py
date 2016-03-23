__author__ = 'Carlos'
from django.utils.timezone import get_current_timezone
from BuenViaje.settings import NEED_TO_RECALCULATE


def fix_month(x):
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


def fix_minute(minute):
    if minute < 10:
        return '0' + str(minute)
    return str(minute)


def edit_fecha(fecha, language):
    fecha_new = fecha.astimezone(tz=get_current_timezone())
    if language == 'es':
        return 'El ' + str(fecha_new.day) + ' de ' + str(fix_month(fecha_new.month)[1]) + ' de ' + str(fecha_new.year) + ' a las ' + str(fecha_new.hour) + ':' + fix_minute(fecha_new.minute)
    else:
        return 'On ' + str(fix_month(fecha_new.month)[2]) + ' ' + str(fecha_new.day) + ', ' + str(fecha_new.year) + ' at ' + str(fecha_new.hour) + ':' + fix_minute(fecha_new.minute)


def edit_fecha_evento(fecha, language):
    fecha_new = fecha
    if language == 'es':
        return str(fecha_new.day) + ' de ' + str(fix_month(fecha_new.month)[1])
    else:
        return str(fix_month(fecha_new.month)[2]) + ' ' + str(fecha_new.day)




