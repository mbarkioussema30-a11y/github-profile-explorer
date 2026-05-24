from django.urls import path
from . import views

urlpatterns = [
    path("", views.search_view, name="search"),
    path("profile/<str:username>/", views.profile_view, name="profile"),
    path("profile/<str:username>/repos/", views.repos_view, name="repos"),
    path("profile/<str:username>/followers/", views.followers_view, name="followers"),
    path("profile/<str:username>/save/", views.save_profile_view, name="save_profile"),
    path("saved/", views.saved_profiles_view, name="saved_profiles"),
    path("saved/<str:username>/delete/", views.delete_saved_profile_view, name="delete_saved_profile"),
]