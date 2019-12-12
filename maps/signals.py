from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.urls import reverse

from .models import ArrangementMap, ArrangementMapComponent, DeletedArrangementMap


@receiver(pre_delete, sender=ArrangementMap)
def create_deleted_map(sender, instance, **kwargs):
    DeletedArrangementMap.objects.create(
        ref=reverse('arrangementmap-detail', kwargs={'pk': instance.pk}))


@receiver(pre_delete, sender=ArrangementMapComponent)
def create_deleted_component(sender, instance, **kwargs):
    DeletedArrangementMap.objects.create(
        ref=reverse('arrangementmapcomponent-detail', kwargs={'pk': instance.pk}))


@receiver([post_save, pre_delete], sender=ArrangementMapComponent)
def update_map(sender, instance, **kwargs):
    ArrangementMap.objects.get(components=instance).save()
