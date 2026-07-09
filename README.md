# SocialSite

A Django-based discussion board where users create topic-based rooms and chat in them.

## Requirements

- Python >= 3.12 (required by Django 6.0)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt   # runtime deps + ruff; use requirements.txt alone for runtime-only
python manage.py migrate
```

## Run

```bash
python manage.py runserver
```

## Lint

```bash
ruff check .            # lint
ruff check --fix .      # auto-fix what's safe
```

Config lives in `pyproject.toml`. Rule set: pyflakes, pycodestyle, isort, pyupgrade, and `DJ` (flake8-django) checks. Migrations and `venv/` are excluded.

## Migrations

```bash
python manage.py makemigrations base
python manage.py migrate
```

Model changes must be accompanied by a migration in the same commit — `makemigrations --check --dry-run` will flag drift. `db.sqlite3` is gitignored and created locally by `migrate`; there is no seed data checked into the repo.

## Tests

```bash
python manage.py test base
python manage.py test base.tests.SomeTestCase.test_something   # single test
```

## Architecture

Single-app Django project (Django 6.0, SQLite). All application logic lives in the `base` app; `socialsite/` is just the project shell (settings/urls/wsgi/asgi).

- **URL wiring**: `socialsite/urls.py` mounts `base.urls` at the root (`''`) plus `/admin/`. `base/urls.py` defines auth routes (`login`, `logout`, `register`) and room CRUD routes (`home`, `room/<pk>`, `create-room`, `update-room/<pk>`, `delete-room/<pk>`).
- **Models** (`base/models.py`): `Topic` (name only) → `Room` (FK to `Topic` and `User` as host) → `Message` (FK to `Room` and `User`). Note the `Message.ser` field name is the FK to `User` (not `user`) — this is a pre-existing naming quirk, not a typo.
- **Views** (`base/views.py`) are plain function-based views, not class-based/DRF. `home` does search across `Room` via `Q` objects on `topic__name`, `name`, and `description` (`?q=` query param).
- **Forms**: `RoomForm` (`base/forms.py`) is a `ModelForm` with an explicit `fields` list and overrides `__init__` to inject `class: form-control` onto every widget so Bootstrap styling applies without per-field template markup.
- **Templates**: `templates/main.html` is the base layout (loads Bootstrap 5.3.8 via CDN with SRI hashes) and includes `templates/navbar.html`. App-specific templates live under `base/templates/base/`.
- **Auth**: room creation/edit/deletion require the requesting user to be the room's host; login/register/logout are handled via Django's built-in auth.
- **Settings** (`socialsite/settings.py`): `DEBUG = True` and a hardcoded `SECRET_KEY` are committed — fine for local/dev, but do not carry them into a deployment config.
