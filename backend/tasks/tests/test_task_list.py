from datetime import date

import pytest

from tasks.models import Membership, Task

URL = "/api/teams/{}/tasks/"


def test_member_sees_the_teams_tasks(client, team, add_member, make_task):
    sara = add_member(team, "sara", "Sara")
    make_task(team, "Write launch post", assignee=sara, due_date=date(2026, 10, 9))
    make_task(team, "Book venue", due_date=date(2026, 10, 7))
    client.force_login(sara)

    response = client.get(URL.format(team.id))

    assert response.status_code == 200
    assert [(t["title"], t["assignee"]) for t in response.json()["tasks"]] == [
        ("Book venue", None),
        ("Write launch post", "Sara"),
    ]


def test_archived_tasks_are_hidden(client, team, add_member, make_task):
    sara = add_member(team, "sara", "Sara")
    make_task(team, "Old idea", status=Task.Status.DONE, is_archived=True)
    client.force_login(sara)

    response = client.get(URL.format(team.id))

    assert response.json()["tasks"] == []


def test_someone_outside_the_team_gets_404(client, team, make_user):
    client.force_login(make_user("outsider"))

    assert client.get(URL.format(team.id)).status_code == 404


@pytest.mark.parametrize("status", [Membership.Status.INVITED, Membership.Status.REMOVED])
def test_invited_and_removed_members_get_404(client, team, add_member, status):
    client.force_login(add_member(team, "former", status=status))

    assert client.get(URL.format(team.id)).status_code == 404


def test_a_team_that_does_not_exist_gets_404(client, make_user):
    client.force_login(make_user("sara"))

    assert client.get(URL.format(999)).status_code == 404


def test_you_must_be_logged_in(client, team):
    response = client.get(URL.format(team.id))

    assert response.status_code == 302
