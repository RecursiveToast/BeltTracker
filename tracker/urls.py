from django.contrib import admin
from django.urls import path, include
from BeltTracker import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.belt_list, name='belt_list'),
    path('belts/add/', views.add_belt, name='add_belt'),
    path('belts/delete/<int:belt_id>/', views.delete_belt, name='delete_belt'),

    # Tragezeiten
    path('wearing-times/', views.wearing_time_list, name='wearing_time_list'),
    path('wearing-times/start/', views.start_wearing_time, name='start_wearing_time'),
    path('wearing-times/end/<int:wearing_time_id>/', views.end_wearing_time, name='end_wearing_time'),
    path('wearing-times/update/<int:wearing_time_id>/', views.update_wearing_time, name='update_wearing_time'),

    # Events
    path('events/add/', views.add_event, name='add_event'),
    path('events/edit/<int:event_id>/', views.edit_event, name='edit_event'),  # NEU

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),  # NEU
]