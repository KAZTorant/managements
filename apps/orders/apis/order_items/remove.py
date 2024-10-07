from rest_framework.views import APIView
from django.db.models import Sum
from decimal import Decimal
from django.db import models

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.orders.models import OrderItem


from drf_yasg.utils import swagger_auto_schema

from apps.orders.models import Order
from apps.orders.serializers import DeleteOrderItemSerializer
from apps.tables.models import Table

from apps.users.permissions import IsRestaurantOwner


class DeleteOrderItemAPIView(APIView):
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    @swagger_auto_schema(
        operation_description="Decrease the quantity or delete an item from an existing unpaid order for the specified table.",
        request_body=DeleteOrderItemSerializer,
        responses={
            204: 'Item quantity updated or item deleted successfully',
            404: 'Order or item not found, or payment already made',
            400: 'Invalid data'
        }
    )
    def delete(self, request, table_id):
        # Check if there is an existing unpaid order and if it belongs to the user
        table = Table.objects.filter(id=table_id).first()
        order: (Order | None) = table.current_order if table else None
        if not order:
            return Response(
                {'error': 'Sifariş yoxdur və ya ödəniş edilib'},
                status=status.HTTP_404_NOT_FOUND
            )

        meal_id = request.data.get("meal_id", 0)

        if not order.order_items.exists():
            order.is_deleted = True
            return Response(
                {'error': 'Sifariş yoxdur və ya ödəniş edilib'},
                status=status.HTTP_404_NOT_FOUND
            )

        order_item: OrderItem = order.order_items.filter(
            meal__id=meal_id
        ).first()

        if not order_item:
            return Response(
                {'error': 'Sifariş yoxdur və ya ödəniş edilib'},
                status=status.HTTP_404_NOT_FOUND
            )

        if order_item.quantity == 1:
            order_item.is_deleted_by_adminstrator = True
            order_item.save()
            order_item.delete()
        else:
            new_quantity = order_item.quantity - 1
            order_item.quantity = new_quantity
            order_item.price = new_quantity * order_item.meal.price
            order_item.save()

        order.refresh_from_db()
        total_price = order.order_items.aggregate(
            total=Sum('price', output_field=models.DecimalField())
        )['total']
        order.total_price = total_price or Decimal(0)
        order.save()

        if not order.order_items.exists():
            order.is_deleted = True
            return Response(
                {'error': 'Sifariş yoxdur və ya ödəniş edilib'},
            )

        return Response({}, status=status.HTTP_200_OK)
