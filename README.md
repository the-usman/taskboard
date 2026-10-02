# Taskboard: code review exercise

Thanks for taking the time to do this. It's close to how we work day to day: an AI coding assistant has written a pull request, and you're the reviewer.

## The situation

Taskboard is a small task tracker for teams, made up for this exercise. A teammate asked an AI coding assistant to build the **weekly team summary** described in [SPEC.md](SPEC.md). The assistant opened a pull request on the `weekly-summary` branch, and wrote the description in [PULL_REQUEST.md](PULL_REQUEST.md). All of its tests pass.

Your job is to review it before it's merged.

## What to do

Spend **2 hours at most**, including setup. We don't expect you to find or fix everything. We're more interested in what you prioritise and how clearly you explain it.

1. Set up the project and run the tests (see [Setup](#setup)).
2. Read [SPEC.md](SPEC.md), then review the pull request. This shows exactly what it changed:

   ```bash
   git diff main...weekly-summary
   ```

3. Write your review in [REVIEW.md](REVIEW.md): the problems you find, most serious first.
4. Fix the **three** problems you think matter most, on the `weekly-summary` branch. Give each fix a test that fails without it. Commit as you go.
5. Submit your work (see [Submitting](#submitting)).

**In scope:** everything the pull request changed, judged against the spec. Code that was already on `main` works as intended; read it to see how this codebase does things.

**Out of scope:** `settings.py`, which is local-only, and anything about deployment, secrets, Docker, CI, type hints or code style. Don't spend your time on these.

## AI tools

Using AI tools is up to you, and it doesn't change your score. If you use them, tell us how when you submit. In the follow-up call we'll talk through your review, so make sure you can explain everything in it.

You don't need access to an LLM. The summary's model call goes through a fake client in `backend/tasks/llm.py`, which never calls a real model.

## Setup

You need Python 3.11 or newer, Node.js 20 or newer, and git. The project is on the `weekly-summary` branch already; check with `git branch`.

### Backend

```bash
cd backend
python3 -m venv .venv            # Windows: python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest
```

To try the endpoint in a browser (optional):

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

`seed_demo` creates a demo team and prints who you can log in as and which URLs to open.

### Frontend

```bash
cd frontend
npm install
npm test
npm run dev        # optional: shows the components at http://localhost:5173
```

The frontend's dev page uses sample data from `src/sampleData.ts`. It doesn't call the API.

## Submitting

1. Commit everything on the `weekly-summary` branch, including `REVIEW.md`.
2. From the `taskboard` folder, bundle the repository into one file:

   ```bash
   git bundle create ../taskboard-yourname.bundle --all
   ```

3. Zip that `.bundle` file.
4. In the TestGorilla assessment, paste your `REVIEW.md`, upload the zip, and tell us whether and how you used AI tools.

After that, we'll set up a call of about 45 minutes to go through your review together.
