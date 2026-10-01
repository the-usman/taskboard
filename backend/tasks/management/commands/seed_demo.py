from datetime import UTC, datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from tasks.models import Membership, Task, Team

PEOPLE = [
    # username, first name, membership status (None = not in the team)
    ("sara", "Sara", Membership.Status.ACTIVE),
    ("omar", "Omar", Membership.Status.ACTIVE),
    ("lina", "Lina", Membership.Status.ACTIVE),
    ("nadia", "Nadia", Membership.Status.INVITED),
    ("rami", "Rami", Membership.Status.REMOVED),
    ("outsider", "Olu", None),
]


class Command(BaseCommand):
    help = "Create a demo team with members and tasks. Running it again starts over."

    def handle(self, *args, **options):
        User = get_user_model()
        User.objects.filter(username__in=["admin", *(p[0] for p in PEOPLE)]).delete()
        Team.objects.filter(name="Launch crew").delete()

        User.objects.create_superuser("admin", password="password")
        team = Team.objects.create(name="Launch crew")
        users = {}
        for username, first_name, status in PEOPLE:
            # Staff, so they can log in through the admin login page.
            user = User.objects.create_user(
                username, password="password", first_name=first_name, is_staff=True
            )
            if status is not None:
                Membership.objects.create(team=team, user=user, status=status)
            users[username] = user

        today = timezone.now().date()
        this_monday = today - timedelta(days=today.weekday())
        last_monday = this_monday - timedelta(days=7)

        def day(n, week_start=last_monday):
            return week_start + timedelta(days=n)

        def at(n, hour):
            return datetime.combine(day(n), time(hour), tzinfo=UTC)

        def task(title, assignee=None, due=None, done_at=None, status=None, archived=False):
            Task.objects.create(
                team=team,
                title=title,
                assignee=users.get(assignee),
                due_date=due,
                status=status or (Task.Status.DONE if done_at else Task.Status.TODO),
                completed_at=done_at,
                is_archived=archived,
            )

        # Last week. Day 0 is Monday, day 6 is Sunday.
        task("Draft launch email", "omar", due=day(1), done_at=at(0, 10))
        task("Fix signup bug", "omar", due=day(2), done_at=at(2, 15))
        task("Prepare demo", "omar", due=day(4), done_at=at(6, 18))
        task("Update pricing page", "sara", due=day(3), done_at=at(1, 11))
        task("Review press kit", "sara", due=day(4), done_at=at(3, 16))
        task("Order T-shirts", "rami", done_at=at(2, 9))
        task("Renew domain", done_at=at(4, 12))
        task("Old brainstorm", "sara", done_at=at(1, 14), archived=True)
        task("Write FAQ", "lina", due=day(2), status=Task.Status.DOING)
        task("Record walkthrough video", "lina", due=day(4))
        task("Plan launch party", "sara", due=day(6))

        # This week.
        task("Send launch email", "sara", due=day(2, this_monday), done_at=timezone.now())
        task("Collect feedback", "omar", due=day(4, this_monday))

        base = "http://127.0.0.1:8000"
        self.stdout.write(
            f'Created team "{team.name}" (id {team.id}).\n\n'
            f"Run `python manage.py runserver`, then log in at {base}/admin/\n"
            "as any of these users. The password is always `password`.\n\n"
            "  sara, omar, lina   active members\n"
            "  nadia              invited, hasn't joined yet\n"
            "  rami               removed from the team\n"
            "  outsider           not in the team\n"
            "  admin              superuser, for browsing the data in the admin\n\n"
            "Then open:\n"
            f"  {base}/api/teams/{team.id}/tasks/\n"
            f"  {base}/api/teams/{team.id}/weekly-summary/  (this week)\n"
            f"  {base}/api/teams/{team.id}/weekly-summary/?week={last_monday}  (last week)\n"
        )
