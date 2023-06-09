# Generated by Django 4.1.7 on 2023-04-02 13:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0005_auto_20220424_2025'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='titre')),
                ('slug', models.SlugField(max_length=250, unique_for_date='publish')),
                ('body', models.TextField(verbose_name='contenu')),
                ('publish', models.DateTimeField(default=django.utils.timezone.now, verbose_name='publier')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='créé')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='mis à jour')),
                ('status', models.CharField(choices=[('DF', 'Draft'), ('PB', 'Published')], default='DF', max_length=2, verbose_name='statut')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_posts', to=settings.AUTH_USER_MODEL, verbose_name='auteur')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'ordering': ['-publish'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='Nom')),
                ('email', models.EmailField(max_length=254, verbose_name='E-mail')),
                ('body', models.TextField(verbose_name='contenu')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='blog.post', verbose_name='Poste')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['-publish'], name='blog_post_publish_bb7600_idx'),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['created'], name='blog_commen_created_0e6ed4_idx'),
        ),
    ]
