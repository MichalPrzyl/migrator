from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("music_app", "0001_add_notes")]

    operations = [
        migrations.DeleteModel("Tribble"),
        migrations.AddField("Author", "rating", models.IntegerField(default=0)),
    ]
