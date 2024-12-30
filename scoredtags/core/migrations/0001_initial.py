# Generated by Django 4.2.4 on 2024-08-17 08:13

import core.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CreatorProjectContribution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_info', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='EditRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(verbose_name='submitted on')),
                ('voting_ends_date', models.DateTimeField(verbose_name='voting ends on')),
                ('evaluation_date', models.DateTimeField(blank=True, null=True, verbose_name='evaluated on')),
                ('evaluation_result', models.CharField(max_length=10)),
                ('title', models.CharField(default='New Request', max_length=50)),
                ('description', models.CharField(max_length=250)),
                ('votes', models.IntegerField(default=0)),
            ],
            managers=[
                ('objects', core.models.EditRequestManager()),
            ],
        ),
        migrations.CreateModel(
            name='SharedData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TagType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Creator',
            fields=[
                ('shareddata', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='linked_creator', serialize=False, to='core.shareddata')),
                ('creator_type', models.SmallIntegerField(choices=[(0, 'unknown'), (1, 'person'), (2, 'group')], default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('shareddata', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='linked_project', serialize=False, to='core.shareddata')),
                ('overall_score', models.FloatField(null=True)),
                ('release_date', models.DateField(null=True)),
                ('last_update_date', models.DateField(null=True)),
                ('creators', models.ManyToManyField(through='core.CreatorProjectContribution', to='core.creator')),
            ],
        ),
        migrations.CreateModel(
            name='EditRequestComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pro_con_text', models.CharField(max_length=100)),
                ('pro_con_type', models.SmallIntegerField(default=0)),
                ('upvotes', models.IntegerField(default=0)),
                ('edit_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.editrequest')),
            ],
        ),
        migrations.CreateModel(
            name='DataName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('shareddata', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.shareddata')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('shareddata', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='linked_tag', serialize=False, to='core.shareddata')),
                ('related_search_tags', models.ManyToManyField(to='core.tag')),
                ('tag_type', models.ForeignKey(default=core.models.TagType.get_default_pk, on_delete=django.db.models.deletion.SET_DEFAULT, to='core.tagtype')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectTagInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(null=True)),
                ('num_votes', models.PositiveIntegerField(default=0)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.project')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.tag')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='tags',
            field=models.ManyToManyField(through='core.ProjectTagInfo', to='core.tag'),
        ),
        migrations.AddField(
            model_name='creatorprojectcontribution',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.creator'),
        ),
        migrations.AddField(
            model_name='creatorprojectcontribution',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.project'),
        ),
        migrations.CreateModel(
            name='CreatorCircle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_info', models.CharField(max_length=10)),
                ('circle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='core.creator')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='joined_circles', to='core.creator')),
            ],
        ),
        migrations.AddField(
            model_name='creator',
            name='circles',
            field=models.ManyToManyField(related_name='circle_members', through='core.CreatorCircle', to='core.creator'),
        ),
        migrations.AddField(
            model_name='creator',
            name='content_tags',
            field=models.ManyToManyField(related_name='content_creators', to='core.tag'),
        ),
    ]