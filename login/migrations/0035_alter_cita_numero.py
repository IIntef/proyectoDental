# Generated by Django 5.0.6 on 2024-07-15 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0034_remove_cita_username_cita_numero'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cita',
            name='numero',
            field=models.IntegerField(blank=True, max_length=50),
        ),
    ]
