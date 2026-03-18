from django.contrib import admin
from django.urls import path,include
from . import views
from .views import home, predict_stock_action,update_companies,delete_companies

app_name = "stock_predict"

urlpatterns = [
    path("home/",views.home,name='home'),
    path("predict/",views.predict_stock_action,name='predict'),
    path("update_companies/", views.update_companies, name="update_companies"),
    path("delete_companies/", views.delete_companies, name="delete_companies"),
]
