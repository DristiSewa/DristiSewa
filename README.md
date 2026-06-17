# DristiSewa

Django-based education consultancy management system (Admin / Manager / Front Desk / Student roles, branch-scoped).

## Running on a new device

The `venv/` folder is machine-specific and should **not** be copied between
computers — recreate it on each machine. Everything else (code, `db.sqlite3`,
`media/`, templates) can be copied as-is.

### 1. Prerequisites
- Python 3.11+ installed
- (Optional) Git, if you're cloning instead of copying the folder

### 2. Get the project onto the new device
Copy the whole `DristiSewa/` folder (excluding `venv/`), or clone the git repo
if one has been set up.

### 3. Create and activate a virtual environment

macOS / Linux:
```bash
cd DristiSewa
python3 -m venv venv
source venv/bin/activate
```

Windows:
```bash
cd DristiSewa
python -m venv venv
venv\Scripts\activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure environment variables
Copy `.env.example` to `.env` and fill in real values (especially
`SECRET_KEY` and, if you want OTP/notification emails to actually send,
`EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` — use a Gmail App Password, not
your normal password):

```bash
cp .env.example .env   # macOS/Linux
copy .env.example .env # Windows
```

If you don't configure email credentials, leave
`EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` — OTP emails
will just print to the terminal instead of being sent.

### 6. Database
- If `db.sqlite3` was copied along with the project, your existing data
  (users, branches, students, etc.) is already there — just run migrations
  to make sure the schema is up to date:
  ```bash
  python manage.py migrate
  ```
- If starting fresh (no `db.sqlite3`), run migrations and create an admin
  account:
  ```bash
  python manage.py migrate
  python manage.py createsuperuser
  ```

### 7. Run the development server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/

## Project notes
See `claude.md` for architecture notes and the locked-template rules
followed during development.
