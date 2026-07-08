# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Setup
```bash
python3 -m venv venv          # requires Python >= 3.12 (Django 6.0 requirement)
source venv/bin/activate
pip install -r requirements-dev.txt   # installs runtime deps + ruff; use requirements.txt alone for runtime-only
python manage.py migrate
```

### Run
```bash
python manage.py runserver
```

### Lint
```bash
ruff check .            # lint
ruff check --fix .      # auto-fix what's safe
```
Config lives in `pyproject.toml`. Rule set: pyflakes, pycodestyle, isort, pyupgrade, and `DJ` (flake8-django) checks. Migrations and `venv/` are excluded.

### Migrations
```bash
python manage.py makemigrations base
python manage.py migrate
```
Model changes must be accompanied by a migration in the same commit — `makemigrations --check --dry-run` will flag drift. `db.sqlite3` is gitignored and created locally by `migrate`; there is no seed data checked into the repo.

### Tests
`base/tests.py` currently has no tests written. Standard Django test invocation once tests exist:
```bash
python manage.py test base
python manage.py test base.tests.SomeTestCase.test_something   # single test
```

## Architecture

Single-app Django project (Django 6.0, SQLite). All application logic lives in the `base` app; `socialsite/` is just the project shell (settings/urls/wsgi/asgi).

- **URL wiring**: `socialsite/urls.py` mounts `base.urls` at the root (`''`) plus `/admin/`. `base/urls.py` defines the room CRUD routes (`home`, `room/<pk>`, `create-room`, `update-room/<pk>`, `delete-room/<pk>`).
- **Models** (`base/models.py`): `Topic` (name only) → `Room` (FK to `Topic` and `User` as host) → `Message` (FK to `Room` and `User`). Note the `Message.ser` field name is the FK to `User` (not `user`) — this is a pre-existing naming quirk, not a typo to silently "fix" without a migration.
- **Views** (`base/views.py`) are plain function-based views, not class-based/DRF. `home` does search across `Room` via `Q` objects on `topic__name`, `name`, and `description` (`?q=` query param).
- **Forms**: `RoomForm` (`base/forms.py`) is a `ModelForm` with explicit `fields` list (not `__all__`, per `DJ007`) and overrides `__init__` to inject `class: form-control` onto every widget so Bootstrap styling applies without per-field template markup.
- **Templates**: `templates/main.html` is the base layout (loads Bootstrap 5.3.8 via CDN with SRI hashes) and includes `templates/navbar.html`. App-specific templates live under `base/templates/base/`. When updating the CDN version, regenerate the `integrity` hash from https://getbootstrap.com/docs — do not hand-write SRI hashes.
- **Auth**: no login/permission checks currently exist on create/update/delete room views — any request can mutate any room. Keep this in mind before treating those endpoints as already access-controlled.
- **Settings** (`socialsite/settings.py`): `DEBUG = True` and a hardcoded `SECRET_KEY` are committed — acceptable for this local/dev-only project, but never carry them into a deployment config.
