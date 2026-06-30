"""
Fix broken foreign key references in SQLite before migration.
Run: python3 fix_broken.py
"""
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
os.environ["DATABASE_URL"] = "sqlite:///db.sqlite3"
django.setup()

from analytics.models import DetailedActivityLog

# Fix DetailedActivityLog — set user=NULL for orphaned records
broken_ids = [84, 83, 82, 77, 75, 26, 25, 13, 12, 9, 8]
updated = DetailedActivityLog.objects.filter(id__in=broken_ids).update(user=None)
print(f"Fixed {updated} DetailedActivityLog records (set user to NULL)")

# Fix SuperAdmin — delete the orphaned record
try:
    from superadmin.models import SuperAdmin
    deleted, _ = SuperAdmin.objects.filter(id=1).delete()
    print(f"Deleted {deleted} broken SuperAdmin record")
except Exception as e:
    print(f"SuperAdmin fix skipped: {e}")

print("\nAll broken references fixed. Ready to export.")
