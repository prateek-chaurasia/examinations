# Generated by Django 2.2.3 on 2019-09-06 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='difficulty_level',
        ),
        migrations.AddField(
            model_name='question',
            name='fail_percentage',
            field=models.CharField(choices=[('30', '30'), ('40', '40'), ('50', '50'), ('60', '60'), ('70', '70'), ('80', '80')], default='30', max_length=2),
        ),
    ]
