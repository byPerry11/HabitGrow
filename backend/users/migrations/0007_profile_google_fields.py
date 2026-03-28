from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_profile_last_daily_reward_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='google_id',
            field=models.CharField(
                blank=True,
                help_text='Identificador único de la cuenta de Google vinculada (sub)',
                max_length=255,
                null=True,
                unique=True,
                verbose_name='Google ID',
            ),
        ),
        migrations.AddField(
            model_name='profile',
            name='google_avatar',
            field=models.URLField(
                blank=True,
                help_text='URL del avatar de perfil de Google',
                null=True,
                verbose_name='Avatar de Google',
            ),
        ),
    ]
