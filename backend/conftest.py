import pytest
from django.contrib.auth import get_user_model

from tasks.llm import FakeLLMClient
from tasks.models import Membership, Task, Team


@pytest.fixture(autouse=True)
def fresh_fake_llm(monkeypatch):
    """Each test starts with the fake model's defaults and no recorded prompts."""
    monkeypatch.setattr(FakeLLMClient, "prompts", [])


@pytest.fixture
def make_user(db):
    def make(username, first_name=""):
        return get_user_model().objects.create_user(
            username=username, password="password", first_name=first_name
        )

    return make


@pytest.fixture
def team(db):
    return Team.objects.create(name="Launch crew")


@pytest.fixture
def add_member(make_user):
    """Create a user and give them a membership of `team` with `status`."""

    def add(team, username, first_name="", status=Membership.Status.ACTIVE):
        user = make_user(username, first_name)
        Membership.objects.create(team=team, user=user, status=status)
        return user

    return add


@pytest.fixture
def make_task(db):
    def make(team, title="A task", **fields):
        return Task.objects.create(team=team, title=title, **fields)

    return make
