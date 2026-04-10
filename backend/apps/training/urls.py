from django.urls import path
from . import views

urlpatterns = [
    path("sessions/", views.create_session, name="training-session-create"),
    path("sessions/<int:session_id>/", views.get_session, name="training-session-get"),
    path("sessions/<int:session_id>/show/", views.show_word, name="training-show-word"),
    path("sessions/<int:session_id>/answer/", views.submit_answer, name="training-submit-answer"),
    path("sessions/<int:session_id>/finish/", views.finish_session, name="training-finish-session"),
]
