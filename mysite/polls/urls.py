from django.urls import path

from . import views

urlpatterns = [
    path('', views.login),
    path('main/account/',views.account),
    path('main/',views.hello),
    path('test/',views.test),
    #path('login/',views.login),
]