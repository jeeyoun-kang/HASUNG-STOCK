from django.urls import path

from . import views

urlpatterns = [
    path('', views.login),
    path('main/account/',views.account),
    path('main/',views.hello),
    path('test/',views.test),
    path('main/logout/',views.logout),
    path('main/auto/',views.auto),
    #path('login/',views.login),
]