# Generated by Django 2.2.1 on 2019-05-14 07:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wholesale', '0009_merge_20190514_0048'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='image',
        ),
        migrations.RemoveField(
            model_name='products',
            name='image',
        ),
    ]