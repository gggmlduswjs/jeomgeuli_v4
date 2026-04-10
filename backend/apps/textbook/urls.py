from django.urls import path
from . import views

urlpatterns = [
    path("extract/", views.extract, name="textbook-extract"),
    path("classify/", views.classify, name="textbook-classify"),
]
