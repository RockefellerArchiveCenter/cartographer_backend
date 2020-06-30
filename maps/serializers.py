from django.urls import reverse
from rest_framework import serializers

from .models import (ArrangementMap, ArrangementMapComponent,
                     DeletedArrangementMap)


class ComponentReferenceSerializer(serializers.ModelSerializer):
    ref = serializers.SerializerMethodField()
    level = serializers.CharField(source='archivesspace_level')
    order = serializers.StringRelatedField(source="tree_index")

    class Meta:
        model = ArrangementMapComponent
        fields = ('title', 'ref', 'archivesspace_uri', 'level', 'order')

    def get_ref(self, obj):
        return reverse('arrangementmapcomponent-detail', kwargs={'pk': obj.pk})


class ArrangementMapComponentSerializer(serializers.ModelSerializer):
    ancestors = ComponentReferenceSerializer(read_only=True, many=True)
    children = ComponentReferenceSerializer(read_only=True, many=True)
    level = serializers.CharField(source='archivesspace_level')
    ref = serializers.SerializerMethodField()
    order = serializers.StringRelatedField(source="tree_index")

    class Meta:
        model = ArrangementMapComponent
        fields = ('id', 'ref', 'title', 'map', 'parent', 'order', 'level',
                  'archivesspace_uri', 'publish', 'ancestors', 'children')

    def get_ref(self, obj):
        return reverse('arrangementmapcomponent-detail', kwargs={'pk': obj.pk})


class ArrangementMapComponentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArrangementMapComponent
        fields = ('id', 'title')


class ArrangementMapSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    ref = serializers.SerializerMethodField()

    class Meta:
        model = ArrangementMap
        fields = ('id', 'ref', 'title', 'children', 'publish', 'created', 'modified')

    def process_tree_item(self, objects, tree):
        for item in objects:
            parent = item.parent.id if item.parent else None
            ref = self.get_ref(item)
            if item.is_leaf_node():
                tree.append({'id': item.pk, 'title': item.title, 'ref': ref, 'level': item.archivesspace_level,
                             'parent': parent, 'archivesspace_uri': item.archivesspace_uri,
                             'order': item.tree_index})
            else:
                tree.append({'id': item.pk, 'title': item.title, 'ref': ref, 'level': item.archivesspace_level,
                             'parent': parent, 'archivesspace_uri': item.archivesspace_uri,
                             'order': item.tree_index, 'children': []})
                self.process_tree_item(item.children.all().order_by('tree_index'), tree[-1].get('children'))
        return tree

    def get_children(self, obj):
        if len(obj.components.all()):
            self.tree = []
            self.process_tree_item(obj.components.filter(parent__isnull=True).all().order_by('tree_index'), self.tree)
            return self.tree

    def get_ref(self, obj):
        if isinstance(obj, ArrangementMapComponent):
            return reverse('arrangementmapcomponent-detail', kwargs={'pk': obj.pk})
        else:
            return reverse('arrangementmap-detail', kwargs={'pk': obj.pk})


class ArrangementMapListSerializer(serializers.ModelSerializer):
    ref = serializers.SerializerMethodField()

    class Meta:
        model = ArrangementMap
        fields = ('id', 'ref', 'title', 'publish')

    def get_ref(self, obj):
        return reverse('arrangementmap-detail', kwargs={'pk': obj.pk})


class DeletedArrangementMapSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeletedArrangementMap
        fields = ('ref', 'archivesspace_uri', 'deleted')
