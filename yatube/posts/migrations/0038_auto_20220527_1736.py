# Generated by Django 2.2.16 on 2022-05-27 14:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0037_auto_20220518_0050'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupFollow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_following', to='posts.Group', verbose_name='Избранная группа')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_follower', to=settings.AUTH_USER_MODEL, verbose_name='Подписанный пользователь')),
            ],
            options={
                'verbose_name': 'Подписка на группу',
                'verbose_name_plural': 'Подписки на группы',
            },
        ),
        migrations.AddConstraint(
            model_name='groupfollow',
            constraint=models.UniqueConstraint(fields=('user', 'group'), name='unique_follow'),
        ),
    ]