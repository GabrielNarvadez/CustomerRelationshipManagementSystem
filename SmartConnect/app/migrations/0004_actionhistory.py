# Generated by Django 5.1.3 on 2024-12-05 03:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0003_alter_customer_email_alter_customer_id_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ActionHistory",
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
                ("action_type", models.CharField(max_length=255)),
                ("action_data", models.JSONField()),
                ("undone", models.BooleanField(default=False)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]