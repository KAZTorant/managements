from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.orders.models import Order

from apps.tables.models import Table
from apps.users.models import User

from apps.users.permissions import IsAdminOrOwner


class ChangeWaitressAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    @swagger_auto_schema(
        operation_description="Change an order's assigned waitress to the table.",
        responses={
            200: openapi.Response(description='Waitress successfully changed.'),
            404: 'Order not found or already paid, or table not found.'
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'new_waitress_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='New waitress ID')
            }
        )
    )
    def post(self, request, table_id):
        table: (Table | None) = Table.objects.filter(id=table_id).first()
        if not table:
            return Response(
                {'error': 'Masa tapılmadı!'},
                status=status.HTTP_404_NOT_FOUND
            )

        new_waitress_id = request.data.get("new_waitress_id", 0)
        new_waitress = User.objects.filter(
            type="waitress"
        ).filter(id=new_waitress_id).first()
        if not new_waitress:
            return Response(
                {'error': 'Dəyişmək istədiyiniz ofisiant tapılmadı!'},
                status=status.HTTP_404_NOT_FOUND
            )

        order: Order = table.current_order

        if not order:
            return Response(
                {'error': 'Sifariş yoxdur və ya ödəniş edilib.'},
                status=status.HTTP_404_NOT_FOUND
            )

        order.waitress = new_waitress
        order.save()
        return Response(
            {'error': 'Ofisiant uğurla dəyişdirildi.'},
            status=status.HTTP_200_OK
        )
