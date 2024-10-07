from drf_yasg.utils import swagger_auto_schema

from django.db import transaction
from django.utils import timezone

from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from apps.meals.models import Meal
from apps.orders.models import OrderItem
from apps.orders.serializers import OrderItemSerializer
from apps.tables.models import Table
from apps.users.permissions import IsWaitressOrCapitaonOrAdminOrOwner


class AddOrderItemAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsWaitressOrCapitaonOrAdminOrOwner
    ]

    @swagger_auto_schema(
        operation_description="Add an item to an existing unpaid order for the specified table.",
        request_body=OrderItemSerializer,
        responses={
            201: OrderItemSerializer,
            404: 'Order not found or payment already made', 400: 'Invalid data'
        }
    )
    def post(self, request, table_id):
        try:
            with transaction.atomic():
                order = self.get_order(request, table_id)
                if not order:
                    return Response({
                        'error': 'Order not found or payment has been made already.'},
                        status=HTTP_404_NOT_FOUND
                    )

                meal = self.get_meal(request.data.get("meal_id", 0))
                if not meal:
                    return Response({'error': 'Meal not found'}, status=HTTP_404_NOT_FOUND)

                response = self.handle_order_item(order, meal)
                order.update_total_price()
                return response
        except Exception as e:
            return Response({'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    def get_order(self, request, table_id):
        order = request.user.orders.select_for_update().filter(
            table__id=table_id, is_paid=False).first()
        if request.user.type in ["admin", 'captain_waitress', 'restaurant']:
            table = Table.objects.filter(id=table_id).first()
            order = table.current_order if table else None
        return order

    def get_meal(self, meal_id):
        return Meal.objects.filter(id=meal_id).first()

    def handle_order_item(self, order, meal):
        order_items = order.order_items.filter(meal=meal)
        if order_items.count() > 1:
            return Response({'error': 'Order Item is more than 1'}, status=HTTP_400_BAD_REQUEST)

        if order_items.exists():
            self.update_order_item(order_items.first(), meal)
        else:
            self.create_order_item(order, meal)

        return Response({'message': 'Order item updated successfully'}, status=HTTP_200_OK)

    def update_order_item(self, order_item, meal):
        order_item.quantity += 1
        order_item.price += meal.price
        order_item.item_added_at = timezone.now()
        order_item.save(update_fields=['quantity', 'price', 'item_added_at'])
        order_item.refresh_from_db()

    def create_order_item(self, order, meal):
        OrderItem.objects.create(
            meal=meal,
            price=meal.price,
            order=order,
            quantity=1
        )
