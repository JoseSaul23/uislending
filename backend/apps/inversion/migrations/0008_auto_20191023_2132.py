# Generated by Django 2.2.6 on 2019-10-23 21:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inversion', '0007_auto_20191023_1343'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inversion',
            name='monto_interese',
        ),
        migrations.AlterField(
            model_name='idea',
            name='intereses',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(50)]),
        ),
        migrations.AlterField(
            model_name='idea',
            name='monto_actual',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='idea',
            name='monto_objetivo',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(100000)]),
        ),
        migrations.AlterField(
            model_name='inversion',
            name='monto_invertido',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]