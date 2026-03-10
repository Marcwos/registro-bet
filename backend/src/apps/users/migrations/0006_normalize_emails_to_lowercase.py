from django.db import migrations


def normalize_emails(apps, schema_editor):
    UserModel = apps.get_model("users", "UserModel")
    for user in UserModel.objects.all():
        normalized = user.email.strip().lower()
        if normalized != user.email:
            user.email = normalized
            user.save(update_fields=["email"])


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_usermodel_theme_preference_usermodel_timezone"),
    ]

    operations = [
        migrations.RunPython(normalize_emails, migrations.RunPython.noop),
    ]
