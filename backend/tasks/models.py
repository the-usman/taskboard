from django.conf import settings
from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Membership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner"
        MEMBER = "member"

    class Status(models.TextChoices):
        ACTIVE = "active"
        INVITED = "invited"  # invited, hasn't joined yet
        REMOVED = "removed"  # left the team or was removed from it

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["team", "user"], name="one_membership_per_team")
        ]

    def __str__(self):
        return f"{self.user} in {self.team} ({self.status})"


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo"
        DOING = "doing"
        DONE = "done"

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.TODO)
    due_date = models.DateField(null=True, blank=True)
    # Set when the task is marked done.
    completed_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.title
