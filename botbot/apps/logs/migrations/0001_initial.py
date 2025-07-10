# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.contrib.postgres.search import SearchVectorField

class Migration(migrations.Migration):

    dependencies = [
        ('bots', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, help_text='', auto_created=True)),
                ('timestamp', models.DateTimeField(db_index=True, help_text='')),
                ('nick', models.CharField(max_length=255, help_text='')),
                ('text', models.TextField(help_text='')),
                ('action', models.BooleanField(default=False, help_text='')),
                ('command', models.CharField(max_length=50, blank=True, null=True, help_text='')),
                ('host', models.TextField(blank=True, null=True, help_text='')),
                ('raw', models.TextField(blank=True, null=True, help_text='')),
                ('room', models.CharField(max_length=100, blank=True, null=True, help_text='')),
                ('search_index', SearchVectorField(null=True, db_index=True, default=b'', editable=False, serialize=False, help_text='')),
                ('bot', models.ForeignKey(null=True, help_text='', to='bots.ChatBot', on_delete=models.CASCADE)),
                ('channel', models.ForeignKey(null=True, help_text='', to='bots.Channel', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('-timestamp',),
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='log',
            index_together=set([('channel', 'timestamp')]),
        ),
    ]
