# Generated by Django 4.2.4 on 2023-09-29 23:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Lexeme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(verbose_name='Date Added')),
                ('text', models.TextField()),
            ],
            options={
                'ordering': ['text'],
            },
        ),
        migrations.CreateModel(
            name='Web',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
                ('date_created', models.DateTimeField(verbose_name='Date Created')),
                ('last_modified', models.DateTimeField(verbose_name='Last Modified')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date_created'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(verbose_name='Date Added')),
                ('symmetric', models.BooleanField(default=False)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relation_name', to='web.lexeme')),
                ('sink', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sink', to='web.lexeme')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source', to='web.lexeme')),
                ('web', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.web')),
            ],
            options={
                'ordering': ['name', 'date_added', 'source'],
            },
        ),
        migrations.CreateModel(
            name='Lexicon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
                ('date_created', models.DateTimeField(verbose_name='Date Created')),
                ('last_modified', models.DateTimeField(verbose_name='Last Modified')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date_created'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='lexeme',
            name='lexicon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.lexicon'),
        ),
        migrations.AddField(
            model_name='lexeme',
            name='relations',
            field=models.ManyToManyField(through='web.Relation', to='web.lexeme'),
        ),
        migrations.AddConstraint(
            model_name='web',
            constraint=models.UniqueConstraint(fields=('user', 'name'), name='web_unique_name'),
        ),
        migrations.AddConstraint(
            model_name='web',
            constraint=models.CheckConstraint(check=models.Q(('date_created__lte', models.F('last_modified'))), name='web_causality'),
        ),
        migrations.AddConstraint(
            model_name='relation',
            constraint=models.UniqueConstraint(fields=('web', 'name', 'source', 'sink'), name='unique_relation'),
        ),
        migrations.AddConstraint(
            model_name='lexicon',
            constraint=models.UniqueConstraint(fields=('user', 'name'), name='lexicon_unique_name'),
        ),
        migrations.AddConstraint(
            model_name='lexicon',
            constraint=models.CheckConstraint(check=models.Q(('date_created__lte', models.F('last_modified'))), name='lexicon_causality'),
        ),
        migrations.AddConstraint(
            model_name='lexeme',
            constraint=models.UniqueConstraint(fields=('lexicon', 'text'), name='unique_lexeme'),
        ),
    ]