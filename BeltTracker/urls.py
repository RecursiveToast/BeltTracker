# BeltTracker/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Hier kommen alle URLs deiner App rein
    path('events/add/', views.add_event, name='add_event'),
    # Füge hier weitere URLs deiner App hinzu (z. B. für Gürtel, Tragezeiten, etc.)
]