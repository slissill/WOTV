from django.db import models
import sys
import django
from django.shortcuts import render
from django.http import HttpResponse
from .utils.datas import maj_programmes, read_progs
from .utils.imdb import get_imdb_infos, update_imdb_infos
from .models import Channel, Programme, ProgressModel
from datetime import date, datetime, timedelta
from django.db.models import Q
from django.db.models import Count
from django.http import JsonResponse
import json

def index(request):    
    context = {"datas" : "welcome"}
    return render(request, "tv/index.html", context)


#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


def get_days_v2(datas):
    days = sorted(set(element.day for element in datas))    
    jours_semaine = ['lun', 'mar', 'mer', 'jeu', 'ven', 'sam', 'dim']
    formatted_dates = [
                            {'name': f"{jours_semaine[date.weekday()]} {date.day}", 
                             'code': date.strftime('%Y%m%d'),  
                             'today': date == datetime.now().date(), 
                            } for date in days if date >= datetime.now().date() - timedelta(days=1)
                    ]
    return formatted_dates


def progs(request):    

    progs = read_progs()

    crit_day = datetime.now().date().strftime('%Y%m%d')

    if request.method == 'POST':
        crit_day = request.POST.get('crit_day')

    criteres =[
                {'name' : "crit_day", 'value' : crit_day, 'liste' : get_days_v2(progs)}, 
            ]
        
    progs_filtre = [prog for prog in progs if prog.day_str == crit_day]

    context = {
                "progs"     : progs_filtre, 
                "criteres"  : criteres, 
                "crit_day"  : crit_day
               }
    return render(request, "tv/progs.html", context)
