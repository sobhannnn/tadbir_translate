# Generated by Django 3.2.6 on 2021-08-28 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic', '0004_alter_role_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='hazinegharardad',
            name='madarek',
            field=models.TextField(blank=True, max_length=5000, null=True),
        ),
    ]
