from django.contrib import admin

from .models import Membership, Task, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "team", "role", "status"]
    list_filter = ["status"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "team", "assignee", "status", "due_date", "completed_at", "is_archived"]
    list_filter = ["status", "is_archived"]
