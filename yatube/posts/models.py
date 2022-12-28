from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='group_title',)
    description = models.TextField(verbose_name='group_description',)
    slug = models.SlugField(
        blank=True,
        null=False,
        unique=True,
        verbose_name='group_slug',
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='post_text',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='date_of_pub',
    )
    group = models.ForeignKey('Group',
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True,
                              related_name='posts',
                              verbose_name='group_of_post',
                              )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='author',
                               )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'posts'

    def __str__(self):
        return self.text[:settings.ITEMS_PER_PAGE]
