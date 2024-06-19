# Generated by Django 5.0.6 on 2024-06-19 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0009_userprofile_groups_userprofile_is_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='tipo',
            field=models.PositiveSmallIntegerField(choices=[(1, 'T.I'), (2, 'C.C'), (3, 'C.E'), (4, 'C.I')], default=2),
        ),
    ]
