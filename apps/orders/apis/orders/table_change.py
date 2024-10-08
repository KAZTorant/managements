from rest_framework.views import APIView


from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.orders.models import Order
from apps.tables.models import Table


from apps.users.permissions import IsAdminOrOwner


class ChangeTableOrderAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    @swagger_auto_schema(
        operation_description="Change an order's assigned table to a new table.",
        responses={
            200: openapi.Response(description='Table successfully changed.'),
            404: 'Order not found or already paid, or table not found, or table not assignable.'
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'new_table_id':
                openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='New table ID'
                )
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

        order: Order = table.current_order

        if not order:
            return Response(
                {'error': 'Sifariş yoxdur və ya ödəniş edilib'},
                status=status.HTTP_404_NOT_FOUND
            )

        new_table_id = request.data.get("new_table_id", 0)
        new_table = Table.objects.filter(id=new_table_id).first()

        if not new_table:
            return Response(
                {'error': 'Sifarişi əlavə etmək istədiyiniz masa tapılmadı!'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not new_table.assignable_table:
            return Response(
                {'error': 'Masada bağlanılmamış sifariş var!'},
                status=status.HTTP_404_NOT_FOUND
            )

        order.table = new_table
        order.save()

        return Response(
            {'message': 'Masa uğurla dəyişdirildi.'},
            status=status.HTTP_200_OK
        )
