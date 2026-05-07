"""
URL configuration for tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
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
]