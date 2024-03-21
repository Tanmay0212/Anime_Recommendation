from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('submit/', views.submit_ratings, name='submit_ratings'),
    path('anime-titles/', views.anime_titles, name='anime-titles'),
    path('results/', views.show_results, name='results'),
    path('progress/', views.progress_update, name='progress_update'),
]