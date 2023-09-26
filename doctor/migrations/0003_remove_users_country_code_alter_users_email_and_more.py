# Generated by Django 4.2.4 on 2023-09-22 06:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("doctor", "0002_alter_doctors_medical_license"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="users",
            name="country_code",
        ),
        migrations.AlterField(
            model_name="users",
            name="email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name="users",
            name="first_name",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="users",
            name="last_name",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="users",
            name="phone_number",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
