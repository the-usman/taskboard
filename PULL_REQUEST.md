# Add the weekly team summary

Implements the weekly team summary from [SPEC.md](SPEC.md): an API endpoint and a card to display it.

## Backend

- **New endpoint** `GET /api/teams/<team_id>/weekly-summary/?week=YYYY-MM-DD` in `tasks/views.py`.
  - Restricted to members of the team.
  - `week` is validated, and defaults to the current week (Monday to Sunday).
- **`tasks/summary.py`** builds the summary:
  - Monday-to-Sunday week window in UTC.
  - Per-member completion counts, sorted by count and then name.
  - Due-date completion percentage.
  - Archived tasks are excluded throughout.
- **LLM highlight** through the existing `get_llm_client()` wrapper. To keep it to a single model call, the model writes the highlight and picks the top member in the same request.
- The fake LLM client's default reply is now JSON, so the endpoint works locally.

## Frontend

- **`WeeklySummaryCard`** shows the week, the counts, the top member, the highlight and the member list.
- Supports the model's bold markup in the highlight.
- Added to the dev page with sample data.

## Tests

- ✅ A member sees the full summary: counts, percentage, ordering, top member and highlight
- ✅ The model is sent the right figures
- ✅ The week defaults to the current week
- ✅ Archived tasks don't count
- ✅ People outside the team are refused
- ✅ An invalid `week` is rejected
- ✅ The card renders every field, and hides the optional ones when they're empty

All 13 backend tests and 4 frontend tests pass. The implementation covers every rule in the spec and is ready to merge.
