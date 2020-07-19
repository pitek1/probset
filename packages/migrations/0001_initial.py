# Generated by Django 3.0.8 on 2020-07-19 22:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import packages.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('problems', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField()),
                ('package', models.FileField(upload_to=packages.models.Package.get_file_name)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems.Problem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
