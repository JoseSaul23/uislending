# Generated by Django 2.2.6 on 2019-10-24 02:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inversion', '0008_auto_20191023_2132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idea',
            name='descripcion',
            field=models.TextField(validators=[django.core.validators.MaxLengthValidator(150)]),
        ),
        migrations.AlterField(
            model_name='idea',
            name='estado',
            field=models.CharField(choices=[('F', 'Fallida'), ('E', 'Exitosa'), ('P', 'Publica'), ('I', 'Inactiva')], default='P', max_length=1),
        ),
        migrations.AlterField(
            model_name='inversion',
            name='monto_invertido',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='user',
            name='saldo',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]