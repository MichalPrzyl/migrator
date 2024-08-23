from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("test_app", "0001_create_models")]

    operations = [
        migrations.DeleteModel("Tribble"),
        migrations.AddField("Author", "rating", models.IntegerField(default=0)),
    ]
