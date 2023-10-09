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

def programmes(request):
    
    # valeurs par défaut
    crit_day = datetime.now().date().strftime('%Y%m%d')
    crit_tranche = "S2"    
    crit_category = "Film"

    if request.method == 'POST':
        crit_day = request.POST.get('crit_day')
        crit_tranche = request.POST.get('crit_tranche')
        crit_category = request.POST.get('crit_category')
    criteres =[
                {'name' : "crit_day", 'value' : crit_day, 'liste' : get_days()}, 
                {'name' : "crit_tranche", 'value' : crit_tranche, 'liste' : get_ref(request, "tranches", perim="in")}, 
                {'name' : "crit_category", 'value' : crit_category, 'liste' : get_ref(request, "categories", perim="in")}, 
            ]
    programmes = get_programmes(request, datetime.strptime(crit_day, "%Y%m%d").date(), crit_tranche, crit_category)
    context = {                                
                "programmes" : programmes,
                "criteres":criteres
                }
    return render(request, "tv/programmes.html", context)


def get_days():

    days = Programme.objects.order_by('day').values_list('day', flat=True).distinct()
    jours_semaine = ['lun', 'mar', 'mer', 'jeu', 'ven', 'sam', 'dim']
    formatted_dates = [
                            {'name': f"{jours_semaine[date.weekday()]} {date.day}", 
                             'code': date.strftime('%Y%m%d'),  
                             'today': date == datetime.now().date(), 
                            } for date in days if date >= datetime.now().date() - timedelta(days=1)
                    ]
    return formatted_dates

def get_programmes(request, crit_day, crit_tranche, crit_category): 
    channels = [r.code for r in  get_ref(request, "channels", perim="in")]
    programmes = Programme.objects.filter(day = crit_day, category = crit_category, channel__channel_id__in=channels).order_by('channel__sort')
    programmes = [p for p in programmes if p.tranche == crit_tranche]
    return programmes

def sys_infos():
     return f"python : {sys.version[:6]}, django : {django.get_version()}" 
def hello_world(request):    
    return HttpResponse("Hello World")
def index(request):    
    context = {"datas" : "welcome"}
    return render(request, "tv/index.html", context)
def ma_table(request):    
    context = {"datas" : "welcome"}
    return render(request, "tv/ma_table.html", context)





def get_programmes_film_to_update():
    excluded_channel_ids = ['CanalPlus.fr', 'CanalPlusCinema.fr', 'CanalPlusSport.fr', 'ParisPremiere.fr', 'PlanetePlus.fr']
    return Programme.objects.exclude(channel_id__in=excluded_channel_ids).filter(category='Film', status = 0).order_by('title')
    
def update_datas(request):    
    programmes_film_to_update = get_programmes_film_to_update()
    if request.method == 'POST':
        if 'update_programmes' in request.POST:
            maj_programmes()    
        elif 'update_movies_infos' in request.POST:
            programmes_film_to_update = get_programmes_film_to_update()
            update_imdb_infos(programmes_film_to_update)
    film_to_update_count = len(programmes_film_to_update)
    nb_dates = Programme.objects.values('day').annotate(day_count=Count('day')).count()
    nb_programmes = Programme.objects.count()    
    ver_python = sys.version[:6]
    ver_django = django.get_version()
    datas =  [
            {'titre' : "Nombre de dates"        , 'value' : nb_dates}, 
            {'titre' : "Nombre de programmes"   , 'value' : nb_programmes}, 
            {'titre' : "Version Python"         , 'value' :ver_python},
            {'titre' : "Version Django"         , 'value' : ver_django},                        
            ]
    context = {
                "datas" : datas, 
                "film_to_update_count" : film_to_update_count
                }
    return render(request, "tv/update_datas.html", context)

def get_progress(request):
        data = 0
        first_record = ProgressModel.objects.all()[0]
        if first_record: data = first_record.progress
        print (data)        
        return JsonResponse(data, safe=False)

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

class cls_referentiel():
    code = models.CharField(max_length=50, verbose_name="Code")
    name = models.CharField(max_length=100, verbose_name="Genre")    
    is_pref = models.BooleanField(verbose_name="Préférence utilisateur")    
    
    def __str__(self):
        return f"{self.code} =>{self.is_pref}" 
    
    def __init__(self, code, name, is_pref):
        self.code = code
        self.name = name
        self.is_pref = is_pref

def get_ref(request, code_ref, perim = "all", from_post = False):
    evaluate = False
    if from_post == False:
        cookie = request.COOKIES.get(code_ref)
        if cookie != None: 
            evaluate = True
            user_codes = json.loads(cookie)
    else:
        user_codes = request.POST.getlist('chkbox')
        evaluate = True

    ret = []
    if code_ref =='channels':
        for item in Channel.objects.all():
            is_pref = True
            if evaluate == True : is_pref = True if item.channel_id in user_codes else False
            ret.append(cls_referentiel(item.channel_id, item.display_name, is_pref))
    elif code_ref =='categories':
        for item in Programme.objects.order_by('category').values_list('category', flat=True).distinct():            
            is_pref = True
            if evaluate == True : is_pref = True if item in user_codes else False
            ret.append(cls_referentiel(item, item, is_pref))
    elif code_ref =='tranches':
        tranches = [
                {'code' : "N",  'name' : "Nuit"}, 
                {'code' : "MA", 'name' : "Matin"}, 
                {'code' : "AM", 'name' : "Après-midi"},
                {'code' : "S1", 'name' : "Soirée 1"},
                {'code' : "S2", 'name' : "Soirée 2"},            
                ]
        for item in tranches:
            is_pref = True
            if evaluate == True : is_pref = True if item['code'] in user_codes else False
            ret.append(cls_referentiel(item['code'], item['name'], is_pref))
    if perim == "all":
        return ret
    elif perim == "in":
        return [r for r in ret if r.is_pref==True]
    elif perim == "out":
        return [r for r in ret if r.is_pref==False]

#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
def ref_tranches(request):
    return ref_global(request, "tranches", "Horaires") 
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
def ref_categories(request):
    return ref_global(request, "categories", "Catégories") 
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
def ref_channels(request):
    return ref_global(request, "channels", "Chaines") 
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

def ref_global(request, code_ref, title):        
    ref = get_ref(request, code_ref, from_post= request.method == 'POST')
    print (ref)
    response = render(request, "tv/referentiel.html", {"items" : ref, "title" : title})    
    response.set_cookie(code_ref, json.dumps([r.code for r in ref if r.is_pref]), max_age=7*24*60*60, samesite=None) #7 jours     
    return response


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
