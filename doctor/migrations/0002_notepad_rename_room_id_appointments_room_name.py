# Generated by Django 4.2.4 on 2023-10-18 05:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("doctor", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotePad",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("room_name", models.CharField(max_length=50)),
                ("notepad", models.TextField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.RenameField(
            model_name="appointments",
            old_name="room_id",
            new_name="room_name",
        ),
    ]
