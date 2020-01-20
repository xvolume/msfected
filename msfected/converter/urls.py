from django.urls import path

from . import views


urlpatterns = [
    path('', views.combiner, name='index')
]