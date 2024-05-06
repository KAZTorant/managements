from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.meals.models import Meal
from apps.orders.models import OrderItem


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.orders.models import Order
from apps.tables.models import Table
from apps.users.models import User

from apps.users.permissions import IsAdminOrOwner, IsRestaurantOwner


# DeleteOrderItemAPIView
class DeleteOrderItemSerializer(serializers.Serializer):
    meal_id = serializers.IntegerField(
        help_text="ID of the meal to decrease quantity from")
    quantity = serializers.IntegerField(
        help_text="Quantity to decrease", min_value=1, default=1)

    def validate_meal_id(self, value):
        # Ensure the meal exists
        try:
            Meal.objects.get(id=value)
        except Meal.DoesNotExist:
            raise serializers.ValidationError("Meal not found")
        return value

    def save(self):
        meal_id = self.validated_data.get('meal_id', 0)
        quantity_to_decrease = self.validated_data.get('quantity', 0)
        order = self.context['order']

        # Try to find the order item within the order
        order_item = OrderItem.objects.filter(
            order=order, meal_id=meal_id).first()
        if not order_item:
            raise serializers.ValidationError("Order item not found")

        # Decrease quantity or delete if necessary
        new_quantity = order_item.quantity - quantity_to_decrease
        if new_quantity > 0:
            OrderItem.objects.filter(id=order_item.id).update(
                quantity=new_quantity)
        else:
            order_item.delete()

        order.update_total_price()


class DeleteOrderItemAPIView(APIView):
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    @swagger_auto_schema(
        operation_description="Decrease the quantity or delete an item from an existing unpaid order for the specified table.",
        request_body=DeleteOrderItemSerializer,
        responses={204: 'Item quantity updated or item deleted successfully',
                   404: 'Order or item not found, or payment already made',
                   400: 'Invalid data'}
    )
    def delete(self, request, table_id):
        # Check if there is an existing unpaid order and if it belongs to the user
        table = Table.objects.filter(id=table_id).first()
        order = table.current_order if table else None
        if not order:
            return Response(
                {'error': 'Sifariş yoxdur və ya ödəniş edilib'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Deserialize data
        serializer = DeleteOrderItemSerializer(
            data=request.data, context={'order': order})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Change order's table
class ChangeOrderTableAPIView(APIView):
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
                'new_table_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='New table ID')
            }
        )
    )
    def post(self, request, table_id):
        table: Table = Table.objects.filter(id=table_id).first()
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


# List waitresses
class ListWaitressSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
        )

    def get_full_name(self, obj: User):
        return obj.get_full_name()


class ListWaitressAPIView(ListAPIView):

    serializer_class = ListWaitressSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        return User.objects.filter(type="waitress")


# Change waitress
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
        table: Table = Table.objects.filter(id=table_id).first()
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


class CloseTableOrderAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def delete(self, request, table_id):

        table = Table.objects.filter(id=table_id).first()
        if not table:
            return Response(
                {
                    "errors": 'Masa tapılmadı.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        order: Order = table.current_order

        if not order:
            return Response(
                {"success": False, "message": "Masada sifariş yoxdur."},
                status=status.HTTP_404_NOT_FOUND
            )

        order.is_paid = True
        order.save()
        return Response(
            {"success": True, "message": "Sifariş uğurla bağlamşdır."},
            status=status.HTTP_200_OK
        )
