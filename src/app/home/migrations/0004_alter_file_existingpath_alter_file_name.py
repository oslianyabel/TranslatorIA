# Generated by Django 4.2.5 on 2024-04-19 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_alter_file_existingpath'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='existingPath',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='file',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
