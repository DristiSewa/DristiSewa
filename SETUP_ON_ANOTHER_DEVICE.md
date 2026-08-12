# DristiSewa Setup on Another Windows Device

## Requirements

- Windows 10 or newer
- Python 3.11 or newer
- Git is optional

## 1. Extract the project

Extract `DristiSewa-system.zip` to a folder such as `C:\Projects\DristiSewa`.

Open PowerShell in that folder.

## 2. Create and activate a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run PowerShell once as the current user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate the environment again.

## 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configure environment variables

Copy `.env.example` to `.env` if the project contains `.env.example`. Otherwise, create `.env` with the required values from `config/settings/base.py` and your deployment needs.

For local development, use the development settings:

```powershell
$env:DJANGO_SETTINGS_MODULE = "config.settings.dev"
```

## 5. Prepare the database

The ZIP intentionally excludes the live `db.sqlite3` file because it was open during packaging.

Create a fresh database:

```powershell
python manage.py migrate
```

To restore the included backup data, run:

```powershell
python manage.py loaddata data_backup.json
```

If the backup contains users, use those credentials. Otherwise create an administrator:

```powershell
python manage.py createsuperuser
```

## 6. Run the application

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in a browser.

## Troubleshooting

- If `dj_database_url` or another module is missing, activate `.venv` and run `pip install -r requirements.txt` again.
- If static files are missing in a production deployment, run `python manage.py collectstatic`.
- Keep `.env`, `db.sqlite3`, and uploaded media private. Do not commit passwords or production secrets.
