"""
URL configuration for MRTweb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('', views.show_MRT_hall, name='show_MRT_hall'),
    path('line/', views.show_line, name='show_line'),
    path('line/<str:line_name>/', views.show_direction, name='show_direction'),
    path('line/<str:line_name>/<str:direction_name>/', views.show_station, name='show_station'),
    path('line/<str:line_name>/<str:direction_name>/<str:station_name>/<str:day_type>/', views.show_train_time, name='show_train_time'),
    path('train/<str:direction_name>/<str:day_type>/<str:train_number>/', views.show_train, name='show_train'),
]
