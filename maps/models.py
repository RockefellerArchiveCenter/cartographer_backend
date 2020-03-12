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
    archivesspace_level = models.CharField(max_length=255, default='collection')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    map = models.ForeignKey(ArrangementMap, on_delete=models.CASCADE, related_name='components')
    tree_index = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @property
    def publish(self):
        return self.map.publish

    @property
    def children(self):
        return ArrangementMapComponent.objects.filter(parent=self)

    def process_ancestors(self, parent, queryset):
        queryset |= ArrangementMapComponent.objects.filter(pk=parent.pk)
        if parent.parent:
            return self.process_ancestors(parent.parent, queryset)
        return queryset

    @property
    def ancestors(self):
        queryset = ArrangementMapComponent.objects.none()
        return self.process_ancestors(
            self.parent, queryset) if self.parent else queryset


class DeletedArrangementMap(models.Model):
    ref = models.CharField(max_length=100)
    deleted = models.DateTimeField(auto_now_add=True)
