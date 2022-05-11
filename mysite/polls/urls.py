from django.urls import path

from . import views

urlpatterns = [
    path('', views.login),
    path('main/account/',views.account),
    path('main/',views.hello),
    path('test/',views.test),
    path('main/logout/',views.logout),
    path('main/auto/',views.auto),
    path('main/current/',views.current),
    path('main/chart/',views.chart_simple1),
    path('main/stock/',views.stockpy),
    path('main/charttest/',views.charttest),
    path('main/test2/',views.test2),
    #path('main/buy/',views.mainbuy),
    #path('main/sell/',views.mainsell),
    #path('login/',views.login),
]