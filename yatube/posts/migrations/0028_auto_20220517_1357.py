# Generated by Django 2.2.16 on 2022-05-17 10:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0027_auto_20220517_1327'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-created',), 'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
    ]
