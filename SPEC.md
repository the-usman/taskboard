# Spec: weekly team summary

Team leads want one screen that shows what their team got done in a week. This spec covers the API endpoint and the card that displays it.

## The data

These models are already on `main`, in `backend/tasks/models.py`.

- **Team.**
- **Membership** links a user to a team. Its `status` is one of:
  - `active`: a current member.
  - `invited`: invited, but hasn't joined yet.
  - `removed`: left the team, or was removed from it.
- **Task** belongs to a team. It can be assigned to a user (`assignee`) or left unassigned. It has an optional `due_date`, a `status` (`todo`, `doing` or `done`), `completed_at` (set when it's marked done) and `is_archived`.

## The endpoint

`GET /api/teams/<team_id>/weekly-summary/?week=YYYY-MM-DD`

1. **Who can see it.** Only active members of the team. Everyone else gets a 404: people outside the team, invited and removed members, and anyone asking for a team that doesn't exist. A 404 means outsiders can't tell whether a team exists. The existing task list endpoint already works this way.
2. **Which week.** `week` can be any date in the week wanted. Weeks run from Monday to Sunday, so `2026-10-07` (a Wednesday) means Monday 5 to Sunday 11 October 2026. Without `week`, use the current week. All times are in UTC. If `week` isn't a valid `YYYY-MM-DD` date, return 400 with `{"error": "week must be a date in YYYY-MM-DD format"}`.
3. **Archived tasks** never count, anywhere in the summary.
4. **`completed_count`** is how many of the team's tasks were completed during the week, judged by `completed_at`. It counts every completed task, including unassigned tasks and tasks assigned to people who have since left the team.
5. **`members`** has one row per active member, including members who completed nothing. Each row has:
   - `user_id`;
   - `name`: their first name, or their username if they haven't set one;
   - `completed_count`: how many tasks assigned to them were completed during the week.

   Sort the rows by `completed_count`, highest first, then by `name` from A to Z. Invited and removed members are not listed.
6. **`due_count` and `done_percent`.** `due_count` is how many tasks have a `due_date` in the week. `done_percent` is the share of those tasks whose status is now `done`, as a whole number rounded half up: 5 of 8 is 62.5%, which shows as `63`. If no tasks are due in the week, `done_percent` is `null`.
7. **`top_member`** is the `name` of the listed member with the highest `completed_count`. If two or more are tied, it's the one whose name comes first from A to Z. It's `null` if nobody completed anything. Our code works this out.
8. **`highlight`** is one sentence written by the LLM, for example "Omar closed 3 tasks and the team finished most of what was due."
   - Send the model the figures above, with members' first names only.
   - Use the model's reply as display text, and for nothing else.
   - The model is unreliable: it can fail, time out, or reply with something unusable. When that happens, still return the summary, with `highlight: null`.

### Example response

```json
{
  "week_start": "2026-10-05",
  "week_end": "2026-10-11",
  "completed_count": 6,
  "due_count": 8,
  "done_percent": 63,
  "members": [
    {"user_id": 5, "name": "Omar", "completed_count": 3},
    {"user_id": 3, "name": "Sara", "completed_count": 2},
    {"user_id": 4, "name": "Lina", "completed_count": 0}
  ],
  "top_member": "Omar",
  "highlight": "Omar closed 3 tasks and the team finished most of what was due."
}
```

The members' counts add up to 5 but `completed_count` is 6, because an unassigned task was completed that week too.

## The card

`WeeklySummaryCard` displays one summary.

9. It shows the week as "5 Oct 2026 – 11 Oct 2026" and the team's completed tasks as "Completed: 6".
10. It shows the due tasks as "Due this week: 8 · Done: 63%". When `done_percent` is `null`, it shows "No tasks were due this week" instead.
11. It shows "Top of the week: Omar" and the highlight, each only when it isn't `null`. The highlight is plain text: show exactly the characters the model returned.
12. It lists the members in the order the API returns them.
