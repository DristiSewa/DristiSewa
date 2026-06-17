from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_student_assigned_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
