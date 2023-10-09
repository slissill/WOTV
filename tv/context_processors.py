import sys
import django
from .models import Channel, Programme
from django.db.models import Count, Max
from django.db.models.functions import TruncDate

def donnees_context(request):
    nb_dates = Programme.objects.values('day').annotate(day_count=Count('day')).count()
    nb_programmes = Programme.objects.count()    
    ver_python = sys.version[:6]
    ver_django = django.get_version()
    
    return {'nb_dates': nb_dates, 
            'nb_programmes' : nb_programmes, 
            'ver_python' : ver_python, 
            'ver_django' : ver_django
            }
