from django.http import Http404

from .models import Membership, Team


def get_team_for_member(user, team_id):
    """Return the team if `user` is an active member of it, otherwise raise 404.

    404 rather than 403, so someone outside the team can't tell whether it exists.
    """
    try:
        return Team.objects.get(
            id=team_id,
            memberships__user=user,
            memberships__status=Membership.Status.ACTIVE,
        )
    except Team.DoesNotExist:
        raise Http404("Team not found") from None
