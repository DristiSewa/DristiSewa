"""
Find broken foreign key references in SQLite before migration.
Run: python3 find_broken.py
"""
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
os.environ["DATABASE_URL"] = f"sqlite:///db.sqlite3"
django.setup()

from django.apps import apps

print("Scanning for broken references...\n")

for model in apps.get_models():
    for field in model._meta.get_fields():
        if hasattr(field, 'remote_field') and field.remote_field and hasattr(field, 'column'):
            related_model = field.related_model
            if related_model is None:
                continue
            try:
                for obj in model.objects.all():
                    val = getattr(obj, field.attname, None)
                    if val is not None:
                        if not related_model.objects.filter(pk=val).exists():
                            print(f"BROKEN: {model.__name__} id={obj.pk} → {field.name}={val} (no matching {related_model.__name__})")
            except Exception as e:
                print(f"Error checking {model.__name__}.{field.name}: {e}")

print("\nDone.")
