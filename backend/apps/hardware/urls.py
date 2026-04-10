from django.urls import path
from . import views

urlpatterns = [
    path("status/", views.hw_status, name="hardware-status"),
    path("connect/", views.connect, name="hardware-connect"),
    path("clear/", views.clear, name="hardware-clear"),
    path("send/", views.send, name="hardware-send"),
    path("send_text/", views.send_text, name="hardware-send-text"),
]
