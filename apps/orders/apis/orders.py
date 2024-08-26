from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.db import transaction
from django.utils import timezone

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from apps.orders.models import Order
from apps.orders.models import OrderItem
from apps.orders.serializers import OrderSerializer
from apps.orders.serializers import OrderItemSerializer
from apps.orders.serializers import ListOrderItemSerializer
from apps.orders.serializers import OrderItemsSerializer
from apps.tables.models import Table
from apps.meals.models import Meal
from apps.users.permissions import IsWaitressOrCapitaonOrAdminOrOwner


class CheckOrderAPIView(APIView):
    permission_classes = [IsAuthenticated,
                          IsWaitressOrCapitaonOrAdminOrOwner]

    def get(self, request, table_id):
        # Check if there is an existing unpaid order for this table
        orders = Order.objects.filter(table__id=table_id, is_paid=False)
        if orders.exists():
            return Response(
                {'message': 'Sifariş yaradılıb'},
                status=status.HTTP_200_OK
            )

        return Response(
            {'message': 'Sifariş yoxdur.'},
            status=status.HTTP_404_NOT_FOUND
        )


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated,
                          IsWaitressOrCapitaonOrAdminOrOwner]

    def post(self, request, table_id):
        # Check if there is an existing unpaid order for this table
        if Order.objects.filter(table__id=table_id, is_paid=False).exists():
            return Response(
                {'error': 'There is an unpaid order for this table.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # If not, create a new order
        data = {'table': table_id}
        serializer = OrderSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddOrderItemAPIView(APIView):
    permission_classes = [IsAuthenticated,
                          IsWaitressOrCapitaonOrAdminOrOwner]

    @swagger_auto_schema(
        operation_description="Add an item to an existing unpaid order for the specified table.",
        request_body=OrderItemSerializer,
        responses={201: OrderItemSerializer,
                   404: 'Order not found or payment already made', 400: 'Invalid data'}
    )
    def post(self, request, table_id):
        try:
            with transaction.atomic():
                order = self.get_order(request, table_id)
                if not order:
                    return Response({
                        'error': 'Order not found or payment has been made already.'},
                        status=status.HTTP_404_NOT_FOUND
                    )

                meal = self.get_meal(request.data.get("meal_id", 0))
                if not meal:
                    return Response({'error': 'Meal not found'}, status=status.HTTP_404_NOT_FOUND)

                response = self.handle_order_item(order, meal)
                order.update_total_price()
                return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            return Response({'error': 'Order Item is more than 1'}, status=status.HTTP_400_BAD_REQUEST)

        if order_items.exists():
            self.update_order_item(order_items.first(), meal)
        else:
            self.create_order_item(order, meal)

        return Response({'message': 'Order item updated successfully'}, status=status.HTTP_200_OK)

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


class ListOrderItemsAPIView(ListAPIView):
    serializer_class = ListOrderItemSerializer
    permission_classes = [
        IsAuthenticated,
        IsWaitressOrCapitaonOrAdminOrOwner
    ]

    def get_queryset(self):
        table_id = self.kwargs.get("table_id", 0)
        table = Table.objects.filter(id=table_id).first()
        order = table.current_order if table else None

        return (
            order.order_items.order_by('-item_added_at').all()
            if order else
            OrderItem.objects.none()
        )


class ListOrderItemsAPIViewV2(APIView):
    permission_classes = [
        IsAuthenticated,
        IsWaitressOrCapitaonOrAdminOrOwner
    ]

    def get(self, request, *args, **kwargs):
        try:
            table_id = kwargs.get("table_id", 0)
            table = Table.objects.get(id=table_id)
            orders = table.orders.filter(is_paid=False)
            items = self.get_items(orders)
            return Response(items, status=status.HTTP_200_OK)
        except Table.DoesNotExist:
            return Response([], status=status.HTTP_404_NOT_FOUND)

    def get_items(self, orders):
        return [
            {
                "is_moved": order.is_moved,
                "order_id": order.id,
                "items": OrderItemsSerializer(
                    instance=order.order_items.all(),
                    many=True
                ).data
            }
            for order in orders
        ]
