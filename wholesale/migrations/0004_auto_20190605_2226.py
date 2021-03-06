# Generated by Django 2.1.8 on 2019-06-06 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wholesale', '0003_auto_20190603_0025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.URLField(null=True),
        ),
        migrations.AlterField(
            model_name='discount',
            name='maxQuan',
            field=models.IntegerField(default=9223372036854775807),
        ),
        migrations.AlterField(
            model_name='products',
            name='max_quantity',
            field=models.IntegerField(default=9223372036854775807),
        ),
    ]
