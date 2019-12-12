from django.urls import reverse
from rest_framework import serializers
from .models import ArrangementMap, ArrangementMapComponent, DeletedArrangementMap


class ArrangementMapComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArrangementMapComponent
        fields = ('id', 'title', 'map', 'parent', 'tree_index', 'archivesspace_uri')


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
                tree.append({'id': item.pk, 'title': item.title, 'ref': ref,
                             'parent': parent, 'archivesspace_uri': item.archivesspace_uri,
                             'tree_index': item.tree_index})
            else:
                tree.append({'id': item.pk, 'title': item.title, 'ref': ref,
                             'parent': parent, 'archivesspace_uri': item.archivesspace_uri,
                             'tree_index': item.tree_index, 'children': []})
                self.process_tree_item(item.children.all().order_by('tree_index'), tree[-1].get('children'))
        return tree

    def get_children(self, obj):
        if len(obj.components.all()):
            self.tree = []
            self.process_tree_item(obj.components.filter(parent__isnull=True).all().order_by('tree_index'), self.tree)
            return self.tree

    def get_ref(self, obj):
        try:
            return reverse('arrangementmapcomponent-detail', kwargs={'pk': obj.pk})
        except:
            return reverse('arrangementmap-detail', kwargs={'pk': obj.pk})


class ArrangementMapListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArrangementMap
        fields = ('id', 'title',)


class DeletedArrangementMapSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeletedArrangementMap
        fields = ('ref', 'deleted')
