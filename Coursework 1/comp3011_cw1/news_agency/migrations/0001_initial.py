# Generated by Django 5.0.2 on 2024-02-14 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('headline', models.CharField(max_length=64)),
                ('category', models.CharField(choices=[('pol', 'Politics'), ('art', 'Art'), ('tech', 'Technology'), ('trivia', 'Trivia')], max_length=32)),
                ('region', models.CharField(choices=[('uk', 'United Kingdom'), ('eu', 'Europe'), ('w', 'World')], max_length=32)),
                ('author', models.CharField(max_length=64)),
                ('date', models.DateTimeField(verbose_name='story date')),
                ('details', models.CharField(max_length=128)),
            ],
        ),
    ]
