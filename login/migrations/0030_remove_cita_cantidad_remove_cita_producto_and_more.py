# Generated by Django 5.0.6 on 2024-07-15 11:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0029_cita_fecha'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cita',
            name='cantidad',
        ),
        migrations.RemoveField(
            model_name='cita',
            name='producto',
        ),
        migrations.AddField(
            model_name='cita',
            name='asistio',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cita',
            name='fecha_hora',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.fecha'),
        ),
        migrations.AddField(
            model_name='cita',
            name='motivo',
            field=models.CharField(choices=[('protesis', 'Protesis'), ('ortodoncia', 'Ortodoncia')], default='protesis', max_length=20),
        ),
        migrations.AddField(
            model_name='cita',
            name='paciente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cita',
            name='estado',
            field=models.CharField(choices=[('programada', 'Programada'), ('completada', 'Completada'), ('cancelada', 'Cancelada')], default='programada', max_length=20),
        ),
    ]
