from datetime import UTC, date, datetime, time, timedelta

from .llm import get_llm_client
from .models import Task
from .utils import display_name


def build_weekly_summary(team, week_start: date) -> dict:
    # Weeks end on Sunday, six days after the Monday they start on.
    week_end = week_start + timedelta(days=6)
    start = datetime.combine(week_start, time.min, tzinfo=UTC)
    end = datetime.combine(week_end, time.min, tzinfo=UTC)

    tasks = Task.objects.filter(team=team, is_archived=False)
    completed_this_week = tasks.filter(
        status=Task.Status.DONE, completed_at__gte=start, completed_at__lt=end
    )

    members = []
    for membership in team.memberships.all():
        members.append(
            {
                "user_id": membership.user.id,
                "name": display_name(membership.user),
                "completed_count": completed_this_week.filter(assignee=membership.user).count(),
            }
        )
    members.sort(key=lambda row: (-row["completed_count"], row["name"]))

    due = tasks.filter(due_date__range=(week_start, week_end))
    due_count = due.count()
    done_count = due.filter(status=Task.Status.DONE).count()

    summary = {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        # Sum the member rows rather than running another query.
        "completed_count": sum(row["completed_count"] for row in members),
        "due_count": due_count,
        # round() gives the nearest whole percent.
        "done_percent": round(done_count / due_count * 100),
        "members": members,
    }
    top = members[0] if members else None
    summary["top_member"] = top["name"] if top and top["completed_count"] > 0 else None
    summary["highlight"] = _highlight(team, summary)
    return summary


def _highlight(team, summary):
    member_lines = "\n".join(
        f"- {row['name']}: {row['completed_count']} completed" for row in summary["members"]
    )
    prompt = (
        "You write the one-sentence highlight for a team's weekly summary.\n\n"
        f"Team: {team.name}\n"
        f"Week: {summary['week_start']} to {summary['week_end']}\n"
        f"Tasks completed: {summary['completed_count']}\n"
        f"Tasks due: {summary['due_count']} ({summary['done_percent']}% done)\n"
        f"Completed per member:\n{member_lines}\n\n"
        "Reply with the sentence only."
    )
    try:
        reply = get_llm_client().complete(prompt)
    except Exception:
        return None
    if not isinstance(reply, str) or not reply.strip():
        return None
    return reply.strip()
