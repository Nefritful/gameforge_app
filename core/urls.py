from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("projects/", views.projects, name="projects"),
    path("projects/<str:project_name>/", views.project_editor, name="project_editor"),

    path("auth/login/", views.login_post, name="login_post"),
    path("auth/register/", views.register_post, name="register_post"),
    path("auth/logout/", views.logout_get, name="logout_get"),

    # API: storage-first
    path("api/projects/<str:project_name>/manifest", views.api_manifest, name="api_manifest"),
    path("api/projects/<str:project_name>/file/read", views.api_file_read, name="api_file_read"),
    path("api/projects/<str:project_name>/file/write", views.api_file_write, name="api_file_write"),
    path("api/projects/<str:project_name>/fs/list", views.api_fs_list, name="api_fs_list"),
    path("api/projects/<str:project_name>/fs/mkdir", views.api_fs_mkdir, name="api_fs_mkdir"),
    path("api/projects/<str:project_name>/fs/delete", views.api_fs_delete, name="api_fs_delete"),
    path("api/projects/<str:project_name>/upload", views.api_upload, name="api_upload"),
    path("api/projects/<str:project_name>/scenes/create", views.api_scenes_create, name="api_scenes_create"),
]
