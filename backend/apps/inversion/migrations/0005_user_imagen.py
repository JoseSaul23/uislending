# Generated by Django 2.2.6 on 2019-10-23 03:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inversion', '0004_auto_20191023_0238'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='imagen',
            field=models.ImageField(default='imagenesUsuarios/usuario.png', upload_to='imagenesUsuarios/'),
        ),
    ]
