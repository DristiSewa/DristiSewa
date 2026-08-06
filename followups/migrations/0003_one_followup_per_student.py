from django.db import migrations, models


def remove_duplicate_followups(apps, schema_editor):
    """Keep the most recently updated tracker for each student."""
    FollowUp = apps.get_model("followups", "FollowUp")
    seen_students = set()
    for followup in FollowUp.objects.order_by("student_id", "-updated_at", "-id").iterator():
        if followup.student_id in seen_students:
            followup.delete()
        else:
            seen_students.add(followup.student_id)


class Migration(migrations.Migration):
    dependencies = [("followups", "0002_appointment")]

    operations = [
        migrations.RunPython(remove_duplicate_followups, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="followup",
            constraint=models.UniqueConstraint(fields=("student",), name="one_followup_per_student"),
        ),
    ]
