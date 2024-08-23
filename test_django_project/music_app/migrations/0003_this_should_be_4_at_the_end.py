from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("music_app", "0002_add_more_notes")
        ("user_app", "0059_migration_1")
    ]

    operations = [
        migrations.DeleteModel("Tribble"),
        migrations.AddField("Author", "rating", models.IntegerField(default=0)),
    ]
