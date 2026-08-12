from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def copy_manager_assignments(apps, schema_editor):
    Student = apps.get_model("students", "Student")
    User = apps.get_model("accounts", "User")
    manager_ids = set(User.objects.filter(role="MANAGER").values_list("id", flat=True))
    for student in Student.objects.filter(assigned_to_id__in=manager_ids).only("id", "assigned_to_id"):
        student.assigned_manager_id = student.assigned_to_id
        student.save(update_fields=["assigned_manager"])


class Migration(migrations.Migration):
    dependencies = [
        ("students", "0005_student_assigned_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="assigned_manager",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="manager_assigned_students",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(copy_manager_assignments, migrations.RunPython.noop),
    ]
