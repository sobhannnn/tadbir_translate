# Generated by Django 3.2.6 on 2021-08-24 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic', '0002_auto_20210824_2003'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='name',
            field=models.PositiveSmallIntegerField(choices=[(1, 'bimeshavande'), (2, 'bimegozar'), (3, 'karshenas'), (4, 'arzyab'), (5, 'admin')], default=1),
        ),
    ]
