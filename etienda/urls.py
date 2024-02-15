from django.urls import path

from . import views
from .api import api

urlpatterns = [
    path("", views.index, name="index"),
    path("buscar", views.buscar, name="buscar"),
    path("resultados/<str:busqueda>", views.resultados, name="resultados"),
    path("busq_cat/<str:categoria>", views.busq_cat, name="busq_cat"),
    path("nuevo", views.nuevo, name="nuevo"),
    path("api/", api.urls),  # <---------- !
]