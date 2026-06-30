"""
Run with: python3 manage.py shell < setup_users.py
Creates a test branch and one user per role.
"""
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from branches.models import Branch
from accounts.models import User

# Create a branch
branch, _ = Branch.objects.get_or_create(
    code="KTM",
    defaults={"name": "Kathmandu", "address": "Kathmandu, Nepal", "is_active": True}
)
print(f"Branch: {branch}")

users = [
    dict(email="admin@dristisewa.com",    password="admindevs",    role="ADMIN",     first_name="Admin",    last_name="User",  is_staff=True, is_superuser=True, branch=None),
    dict(email="manager@dristisewa.com",  password="managerdevs", role="MANAGER",   first_name="Manager",  last_name="User",  is_staff=True,  is_superuser=False, branch=branch),
    dict(email="frontdesk@dristisewa.com",password="frontdevs",   role="FRONTDESK", first_name="FrontDesk",last_name="User",  is_staff=False, is_superuser=False, branch=branch),
    dict(email="student@dristisewa.com",  password="studentdevs", role="STUDENT",   first_name="Student",  last_name="User",  is_staff=False, is_superuser=False, branch=branch),
]

for u in users:
    password = u.pop("password")
    if not User.objects.filter(email=u["email"]).exists():
        user = User.objects.create_user(password=password, **u)
        print(f"Created: {user.email} ({user.role})")
    else:
        print(f"Already exists: {u['email']}")

print("\nDone! Login credentials:")
print("  Admin:     admin@dristisewa.com     / admindevs")
print("  Manager:   manager@dristisewa.com   / managerdevs")
print("  FrontDesk: frontdesk@dristisewa.com / frontdevs")
print("  Student:   student@dristisewa.com   / studentdevs")
