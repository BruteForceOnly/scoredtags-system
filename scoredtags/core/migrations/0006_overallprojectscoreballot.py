# Generated by Django 4.2.4 on 2024-10-22 11:24

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_projectseriesentry_order_num'),
    ]

    operations = [
        migrations.CreateModel(
            name='OverallProjectScoreBallot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid_hash', models.BinaryField(max_length=32)),
                ('uid_salt', models.BinaryField(max_length=16, null=True)),
                ('score', models.SmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('submitted_on', models.DateTimeField(null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.project')),
            ],
        ),
    ]