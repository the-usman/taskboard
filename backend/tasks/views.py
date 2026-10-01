from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .access import get_team_for_member
from .utils import display_name


@require_GET
@login_required
def task_list(request, team_id):
    team = get_team_for_member(request.user, team_id)
    tasks = (
        team.tasks.filter(is_archived=False)
        .select_related("assignee")
        .order_by("due_date", "id")
    )
    return JsonResponse(
        {
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "assignee": display_name(task.assignee) if task.assignee else None,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                }
                for task in tasks
            ]
        }
    )
