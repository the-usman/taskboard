from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET

from .access import get_team_for_member
from .models import Membership, Team
from .summary import build_weekly_summary
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


@require_GET
@login_required
def weekly_summary(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if not Membership.objects.filter(team=team, user=request.user).exists():
        return JsonResponse({"error": "You are not a member of this team."}, status=403)

    week = request.GET.get("week")
    if week:
        try:
            week_start = datetime.strptime(week, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "week must be a date in YYYY-MM-DD format"}, status=400)
    else:
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())

    return JsonResponse(build_weekly_summary(team, week_start))
