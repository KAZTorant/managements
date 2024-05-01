from apps.tables.models import Table
from apps.tables.models import Room

from rest_framework.generics import ListAPIView
from rest_framework import serializers


class TableSerializer(serializers.ModelSerializer):

    waitress = serializers.SerializerMethodField()
    print_check = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = (
            "id",
            "number",
            "room",
            "waitress",
            "total_price",
            "print_check",
        )

    def get_waitress(self, obj: Table):
        if not obj.waitress:
            return {
                "name": "",
                "id": 0,
            }

        return {
            "name": obj.waitress.get_full_name(),
            "id": obj.waitress.id,
        }

    def get_print_check(self, obj: Table):
        return obj.current_order.is_check_printed if obj.current_order else False


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = (
            "id",
            "name",
            "description"
        )


class TableAPIView(ListAPIView):
    model = Table
    serializer_class = TableSerializer

    def get_queryset(self):
        room_id = self.kwargs.get("room_id", None)
        return Table.objects.filter(room__id=room_id)


class RoomAPIView(ListAPIView):
    model = Room
    serializer_class = RoomSerializer

    def get_queryset(self):
        return Room.objects.filter(is_active=True)
