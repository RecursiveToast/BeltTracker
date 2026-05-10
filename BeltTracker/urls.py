# BeltTracker/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Hier kommen alle URLs deiner App rein
    path('events/add/', views.add_event, name='add_event'),
    path('events/edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('events/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    # Füge hier weitere URLs deiner App hinzu (z. B. für Gürtel, Tragezeiten, etc.)
]