from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("user_app", "0001_migration_1")]

    operations = [
        migrations.DeleteModel("Tribble"),
        migrations.AddField("Author", "rating", models.IntegerField(default=0)),
    ]
