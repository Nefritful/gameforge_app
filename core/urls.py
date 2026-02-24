from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("projects/", views.projects, name="projects"),
    path("projects/<int:project_id>/", views.project_editor, name="project_editor"),

    path("auth/login/", views.login_post, name="login_post"),
    path("auth/register/", views.register_post, name="register_post"),
    path("auth/logout/", views.logout_get, name="logout_get"),

    # API (минимум)
    path("api/projects/<int:project_id>/files/get", views.api_file_get, name="api_file_get"),
    path("api/projects/<int:project_id>/files/save", views.api_file_save, name="api_file_save"),
    path("api/projects/<int:project_id>/scenes/list", views.api_scenes_list, name="api_scenes_list"),
    path("api/projects/<int:project_id>/scenes/create", views.api_scenes_create, name="api_scenes_create"),
]
