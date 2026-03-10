from collections import defaultdict

from django.db import migrations


def normalize_emails(apps, schema_editor):
    UserModel = apps.get_model("users", "UserModel")

    # Agrupar usuarios por email normalizado para detectar duplicados
    groups = defaultdict(list)
    for user in UserModel.objects.all():
        groups[user.email.strip().lower()].append(user)

    for normalized, users in groups.items():
        if len(users) > 1:
            # Resolver duplicados: priorizar verificado, luego el más reciente
            users.sort(key=lambda u: (u.is_email_verified, u.created_at), reverse=True)
            keeper = users[0]
            for duplicate in users[1:]:
                duplicate.delete()
            keeper.email = normalized
            keeper.save(update_fields=["email"])
        else:
            user = users[0]
            if user.email != normalized:
                user.email = normalized
                user.save(update_fields=["email"])


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_usermodel_theme_preference_usermodel_timezone"),
    ]

    operations = [
        migrations.RunPython(normalize_emails, migrations.RunPython.noop),
    ]
