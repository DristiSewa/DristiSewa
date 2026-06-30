"""
Fix ALL broken user references in DetailedActivityLog at once.
Run: python3 fix_broken2.py
"""
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
os.environ["DATABASE_URL"] = "sqlite:///db.sqlite3"
django.setup()

from analytics.models import DetailedActivityLog
from accounts.models import User

valid_user_ids = set(User.objects.values_list('pk', flat=True))
broken = DetailedActivityLog.objects.exclude(user__isnull=True).exclude(user_id__in=valid_user_ids)
count = broken.count()
broken.update(user=None)
print(f"Fixed {count} broken DetailedActivityLog records.")
print("Ready to export.")
