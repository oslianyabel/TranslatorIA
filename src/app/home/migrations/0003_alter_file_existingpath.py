# Generated by Django 4.2.5 on 2024-03-07 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='existingPath',
            field=models.CharField(max_length=255),
        ),
    ]