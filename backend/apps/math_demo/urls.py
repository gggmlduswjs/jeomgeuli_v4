from django.urls import path
from . import views

urlpatterns = [
    path("detect/", views.detect, name="math-detect"),
    path("explain/", views.explain, name="math-explain"),
]
