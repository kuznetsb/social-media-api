# Generated by Django 4.2 on 2023-04-23 15:55

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("network", "0005_post_schedule"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="post",
            unique_together=set(),
        ),
    ]