# Generated by Django 4.1.1 on 2022-09-17 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('url_shortener', '0004_generator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='url',
            name='url',
            field=models.URLField(max_length=1000),
        ),
    ]
