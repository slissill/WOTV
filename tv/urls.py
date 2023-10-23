from django.urls import path
from . import views

app_name = "tv"

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('progs', views.progs, name='progs'),
]
