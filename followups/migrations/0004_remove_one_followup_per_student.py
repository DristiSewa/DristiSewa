from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("followups", "0003_one_followup_per_student")]

    operations = [
        migrations.RemoveConstraint(
            model_name="followup",
            name="one_followup_per_student",
        ),
    ]
