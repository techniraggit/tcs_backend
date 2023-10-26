# Generated by Django 4.2.4 on 2023-10-26 06:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("doctor", "0002_appointments_is_attended"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="consultation",
            name="consult",
        ),
        migrations.AddField(
            model_name="consultation",
            name="appointment",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="doctor.appointments",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="appointments",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("completed", "Completed"),
                    ("rescheduled", "Rescheduled"),
                    ("free_consultation", "Free Consultation"),
                    ("cancelled", "Cancelled"),
                    ("unanswered_patient", "Unanswered Patient"),
                    ("unanswered_doctor", "Unanswered Doctor"),
                ],
                default="pending",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="consultation",
            name="doctor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING, to="doctor.doctors"
            ),
        ),
        migrations.AlterField(
            model_name="consultation",
            name="patient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING, to="doctor.patients"
            ),
        ),
        migrations.AlterField(
            model_name="consultation",
            name="prescription",
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]