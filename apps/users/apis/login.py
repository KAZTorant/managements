from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()


class PinLoginSerializer(serializers.Serializer):
    pin = serializers.CharField(max_length=32, min_length=4)


class PinLoginAPIView(APIView):

    @swagger_auto_schema(
        request_body=PinLoginSerializer,
        responses={200: 'User details and token',
                   400: 'Invalid data', 404: 'User not found'},
        operation_description="Login using a PIN"
    )
    def post(self, request):
        serializer = PinLoginSerializer(data=request.data)
        if serializer.is_valid():
            pin = serializer.validated_data['pin']

            try:
                user = User.objects.get(username=pin)
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Return user details along with the token
            return Response({
                'username': user.username,
                'role': user.type,
                'full_name': user.get_full_name(),
            })
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
