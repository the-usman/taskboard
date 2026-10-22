import json
from datetime import UTC, date, datetime, timedelta

import pytest

from tasks.llm import FakeLLMClient
from tasks.models import Membership, Task

URL = "/api/teams/{}/weekly-summary/"
MONDAY = date(2026, 10, 5)
DONE = Task.Status.DONE


def day(n):
    """A date in the week of Monday 5 October 2026. Day 0 is Monday."""
    return MONDAY + timedelta(days=n)


def at(n, hour=12):
    """A moment in that week."""
    return datetime(2026, 10, 5 + n, hour, tzinfo=UTC)


@pytest.fixture
def model_reply(monkeypatch):
    def set_reply(highlight, top_member):
        reply = json.dumps({"highlight": highlight, "top_member": top_member})
        monkeypatch.setattr(FakeLLMClient, "reply", reply)

    return set_reply


def test_member_sees_the_weekly_summary(client, team, add_member, make_task, model_reply):
    omar = add_member(team, "omar", "Omar")
    sara = add_member(team, "sara", "Sara")
    lina = add_member(team, "lina", "Lina")
    # Completed this week: Omar 3, Sara 1. Due this week: 8 tasks, 5 of them done
    # (Sara finished one of them early, last week).
    make_task(team, assignee=omar, due_date=day(1), status=DONE, completed_at=at(0))
    make_task(team, assignee=omar, due_date=day(2), status=DONE, completed_at=at(2))
    make_task(team, assignee=omar, due_date=day(4), status=DONE, completed_at=at(3))
    make_task(team, assignee=sara, due_date=day(3), status=DONE, completed_at=at(1))
    make_task(team, assignee=sara, due_date=day(4), status=DONE, completed_at=at(-3))
    make_task(team, assignee=lina, due_date=day(2), status=Task.Status.DOING)
    make_task(team, assignee=lina, due_date=day(4))
    make_task(team, assignee=sara, due_date=day(5))
    model_reply("Omar closed 3 tasks this week.", "Omar")
    client.force_login(sara)

    response = client.get(URL.format(team.id), {"week": "2026-10-05"})

    assert response.status_code == 200
    assert response.json() == {
        "week_start": "2026-10-05",
        "week_end": "2026-10-11",
        "completed_count": 4,
        "due_count": 8,
        "done_percent": 62,  # 5 of 8 done
        "members": [
            {"user_id": omar.id, "name": "Omar", "completed_count": 3},
            {"user_id": sara.id, "name": "Sara", "completed_count": 1},
            {"user_id": lina.id, "name": "Lina", "completed_count": 0},
        ],
        "top_member": "Omar",
        "highlight": "Omar closed 3 tasks this week.",
    }


def test_the_model_is_sent_the_figures(client, team, add_member, make_task, model_reply):
    sara = add_member(team, "sara", "Sara")
    make_task(team, assignee=sara, due_date=day(2), status=DONE, completed_at=at(2))
    model_reply("Sara cleared everything that was due.", "Sara")
    client.force_login(sara)

    client.get(URL.format(team.id), {"week": "2026-10-05"})

    [prompt] = FakeLLMClient.prompts
    assert "Tasks completed: 1" in prompt
    assert "Tasks due: 1 (100% done)" in prompt
    assert "- Sara: 1 completed" in prompt


def test_the_week_defaults_to_the_current_week(
    client, team, add_member, make_task, model_reply, monkeypatch
):
    sara = add_member(team, "sara", "Sara")
    make_task(team, assignee=sara, due_date=day(2))
    model_reply("A quiet week.", None)
    monkeypatch.setattr("tasks.views.timezone.now", lambda: at(3, hour=9))
    client.force_login(sara)

    response = client.get(URL.format(team.id))

    assert response.json()["week_start"] == "2026-10-05"
    assert response.json()["week_end"] == "2026-10-11"


def test_archived_tasks_do_not_count(client, team, add_member, make_task, model_reply):
    sara = add_member(team, "sara", "Sara")
    make_task(team, assignee=sara, due_date=day(1))
    make_task(team, assignee=sara, due_date=day(2), status=DONE, completed_at=at(2), is_archived=True)
    model_reply("A quiet week.", None)
    client.force_login(sara)

    data = client.get(URL.format(team.id), {"week": "2026-10-05"}).json()

    assert data["completed_count"] == 0
    assert data["due_count"] == 1
    assert data["done_percent"] == 0


def test_people_outside_the_team_are_refused(client, team, make_user):
    client.force_login(make_user("outsider"))

    response = client.get(URL.format(team.id))

    assert response.status_code == 404


@pytest.mark.parametrize("status", [Membership.Status.INVITED, Membership.Status.REMOVED])
def test_invited_and_removed_members_get_404(client, team, add_member, status):
    client.force_login(add_member(team, "former", status=status))

    assert client.get(URL.format(team.id)).status_code == 404


def test_a_team_that_does_not_exist_gets_404(client, make_user):
    client.force_login(make_user("sara"))

    assert client.get(URL.format(999)).status_code == 404


def test_an_invalid_week_is_rejected(client, team, add_member):
    client.force_login(add_member(team, "sara", "Sara"))

    response = client.get(URL.format(team.id), {"week": "next week"})

    assert response.status_code == 400
    assert response.json() == {"error": "week must be a date in YYYY-MM-DD format"}
