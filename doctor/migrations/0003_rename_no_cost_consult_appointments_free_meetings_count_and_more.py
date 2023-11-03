# Generated by Django 4.2.4 on 2023-11-02 13:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("doctor", "0002_appointments_initial_schedule_date_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="appointments",
            old_name="no_cost_consult",
            new_name="free_meetings_count",
        ),
        migrations.RenameField(
            model_name="appointments",
            old_name="is_attended",
            new_name="is_join",
        ),
        migrations.RemoveField(
            model_name="appointments",
            name="access_token",
        ),
        migrations.RemoveField(
            model_name="appointments",
            name="meeting_link",
        ),
    ]