# Generated by Django 4.2.9 on 2024-10-31 13:50


from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("futuboard", "0003_auto_20241031_1550"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usergroupuser",
            name="usergroupid",
            field=models.ForeignKey(
                db_column="usergroupID", on_delete=django.db.models.deletion.DO_NOTHING, to="futuboard.usergroup"
            ),
        ),
        migrations.AlterField(
            model_name="usergroupuser",
            name="usergroupuserid",
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, null=False),
        ),
    ]
