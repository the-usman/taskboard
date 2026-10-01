from django.urls import path

from . import views

urlpatterns = [
    path("teams/<int:team_id>/tasks/", views.task_list, name="task-list"),
]
