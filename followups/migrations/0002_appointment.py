# Generated manually to follow 0001_initial conventions

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
        ('followups', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('purpose', models.CharField(blank=True, max_length=200)),
                ('appointment_date', models.DateField()),
                ('appointment_time', models.TimeField()),
                ('status', models.CharField(choices=[('SCHEDULED', 'Scheduled'), ('RESCHEDULED', 'Rescheduled'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')], default='SCHEDULED', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('staff', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointments', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='students.student')),
            ],
            options={
                'ordering': ['-appointment_date', '-appointment_time'],
            },
        ),
    ]
