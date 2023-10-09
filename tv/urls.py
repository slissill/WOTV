from django.urls import path
from . import views

app_name = "tv"

urlpatterns = [
    path('', views.hello_world, name='hello_wold'),
    path('index', views.index, name='index'),

    path('programmes', views.programmes, name='programmes'),
    
    path('edit_tranches', views.ref_tranches, name='ref_tranches'),
    path('edit_categories', views.ref_categories, name='ref_categories'),
    path('edit_channels', views.ref_channels, name='ref_channels'),
    

    path('update', views.update_datas, name='update'),
    path('ma_table', views.ma_table, name='ma_table'),
    path('progs', views.progs, name='progs'),

    path('get_progress', views.get_progress, name='get_progress'),


]
