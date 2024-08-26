from rest_framework import serializers

from apps.tables.models import Table
from apps.tables.models import Room


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


class TableDetailSerializer(serializers.ModelSerializer):

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
                "name": self.context['user'].get_full_name(),
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
