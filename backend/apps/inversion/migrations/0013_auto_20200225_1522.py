# Generated by Django 2.2.6 on 2020-02-25 15:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inversion', '0012_auto_20200225_1516'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='idea',
            options={'ordering': ['-monto_actual']},
        ),
    ]
