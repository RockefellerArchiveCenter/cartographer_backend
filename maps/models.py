from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class User(AbstractUser):
    pass


class ArrangementMap(models.Model):
    title = models.CharField(max_length=255)
    publish = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class ArrangementMapComponent(MPTTModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    archivesspace_uri = models.CharField(max_length=255, null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    map = models.ForeignKey(ArrangementMap, on_delete=models.CASCADE, related_name='components')
    tree_index = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class DeletedArrangementMap(models.Model):
    ref = models.CharField(max_length=100)
    deleted = models.DateTimeField(auto_now_add=True)
