from django.urls import path
from django.contrib import admin


from . import views

urlpatterns = [
    path('', views.login),
    path('main/',views.hello),
   
    path('test/',views.test),
    path('main/logout/',views.logout),
    path('main/auto/',views.auto),
    path('main/current/',views.current),
    path('main/chart/',views.chart_simple1),
    path('main/charttest/',views.charttest),
    path('main/test2/',views.test2),
    path('main/dl/',views.dl),
    path('main/buy/',views.mainbuy),
    path('main/sell/',views.mainsell),
    path('main/set/',views.set),
    path('main/fix/',views.fix),
    path('main/test/',views.mysql),
    path('main/cancel/',views.cancel),
    path('main/query/',views.query),
    path('main/query/3.html',views.query2),
    
    #path('main/sell/',views.mainsell),
    #path('login/',views.login),
]