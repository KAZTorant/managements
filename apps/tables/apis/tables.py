from apps.tables.models import Table
from rest_framework.generics import ListAPIView
from rest_framework import serializers


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = (
            "number",
            "room"
        )


class TableAPIView(ListAPIView):
    model = Table
    serializer_class = TableSerializer

    def get_queryset(self):
        room_id = self.kwargs.get("room_id", None)
        return Table.objects.filter(room__id=room_id)