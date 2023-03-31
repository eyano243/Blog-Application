from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()\
                      .filter(status=Post.Status.PUBLISHED)



class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250,verbose_name="titre")
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User,
                           on_delete=models.CASCADE,
                           related_name='blog_posts',verbose_name="auteur")
    body = models.TextField(verbose_name="contenu")
    publish = models.DateTimeField(default=timezone.now,verbose_name="publier" )
    created = models.DateTimeField(auto_now_add=True,verbose_name="créé")
    updated = models.DateTimeField(auto_now=True,verbose_name="mis à jour")
    status = models.CharField(max_length=2,
                          choices=Status.choices,
                          default=Status.DRAFT, verbose_name="statut")

    objects = models.Manager() # The default manager
    published = PublishedManager() # Our custom manager

    class Meta:
        ordering = ['-publish'] 
        indexes = [
                    models.Index(fields=['-publish']),
                ]
    def __str__(self):
        return self.title


    def get_absolute_url(self):
        return reverse("blog:post_detail", 
                       args=[self.publish.year,
                            self.publish.month,
                            self.publish.day,
                            self.slug])
    


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="Poste")
    name = models.CharField(max_length=80, verbose_name="Nom")
    email = models.EmailField(verbose_name='E-mail')
    body = models.TextField(verbose_name="contenu")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]
    def __str__(self):
        return f'Comment by {self.name} on {self.post}'