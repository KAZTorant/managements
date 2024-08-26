from rest_framework import serializers


class PinLoginSerializer(serializers.Serializer):
    pin = serializers.CharField(max_length=32, min_length=4)
