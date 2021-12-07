from asnake.aspace import ASpace
from cartographer_backend import settings
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.urls import reverse

from .models import (ArrangementMap, ArrangementMapComponent,
                     DeletedArrangementMap)


@receiver(pre_delete, sender=ArrangementMap)
def create_deleted_map(sender, instance, **kwargs):
    DeletedArrangementMap.objects.create(
        ref=reverse('arrangementmap-detail', kwargs={'pk': instance.pk}))


@receiver(pre_delete, sender=ArrangementMapComponent)
def create_deleted_component(sender, instance, **kwargs):
    DeletedArrangementMap.objects.create(
        ref=reverse('arrangementmapcomponent-detail', kwargs={'pk': instance.pk}),
        archivesspace_uri=instance.archivesspace_uri)


@receiver([post_save, pre_delete], sender=ArrangementMapComponent)
def update_map(sender, instance, **kwargs):
    ArrangementMap.objects.get(components=instance).save()


@receiver(pre_save, sender=ArrangementMapComponent)
def calculate_child_count(sender, instance, **kwargs):
    if instance.archivesspace_uri and not kwargs["raw"]:
        aspace = ASpace(baseurl=settings.ASPACE['baseurl'],
                        username=settings.ASPACE['username'],
                        password=settings.ASPACE['password'])
        escaped_uri = instance.archivesspace_uri.replace('/', r'\/')
        search_uri = f"search?q=resource:/{escaped_uri}/ AND publish:true&page=1&fields[]=uri&type[]=archival_object&page_size=1"
        resource = aspace.client.get(search_uri).json()
        instance.child_count = resource["total_hits"]
