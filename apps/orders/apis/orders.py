
from apps.meals.models import Meal
from apps.orders.models import Order
from apps.orders.models import OrderItem
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import F

from drf_yasg.utils import swagger_auto_schema


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'table')

    def create(self, validated_data):
        validated_data["waitress"] = self.context['request'].user
        order = Order.objects.create(**validated_data)
        return order


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

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
        return


class OrderItemSerializer(serializers.ModelSerializer):
    meal_id = serializers.IntegerField(
        write_only=True,
        source='meal.id',
        help_text="ID of the meal"
    )

    class Meta:
        model = OrderItem
        # 'meal' and 'order' are for serialization
        fields = ['meal_id', 'quantity', 'meal', 'order']
        # These are for serialization only
        read_only_fields = ['meal', 'order']

    def validate_meal_id(self, value):
        try:
            Meal.objects.get(id=value)
        except Meal.DoesNotExist:
            raise serializers.ValidationError("Meal not found")
        return value

    def create(self, validated_data):
        meal = validated_data.pop('meal', None)
        meal_id = meal.get("id", 0)

        # Default to 1 if not specified
        quantity = validated_data.get('quantity', 1)

        meal = Meal.objects.get(id=meal_id)
        order = Order.objects.get(id=self.context['order_id'])

        # Check if the order item already exists
        order_item, created = OrderItem.objects.get_or_create(
            meal=meal,
            order=order,
            defaults={'quantity': quantity}
        )

        # If the order item was not created, it means it already exists, so update the quantity
        if not created:
            OrderItem.objects.filter(id=order_item.id).update(
                quantity=F('quantity') + quantity)

        # Refresh from database to get updated quantity if it was updated
        order_item.refresh_from_db()

        return order_item


class AddOrderItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Add an item to an existing unpaid order for the specified table.",
        request_body=OrderItemSerializer,
        responses={201: OrderItemSerializer,
                   404: 'Order not found or payment already made', 400: 'Invalid data'}
    )
    def post(self, request, table_id):
        # Check if there is an existing unpaid order and if it belongs to the user
        order = request.user.orders.filter(
            table__id=table_id,
            is_paid=False
        ).first()

        if not order:
            return Response(
                {'error': 'Order not found or payment has been made already.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Proceed to add a new order item to the found order
        serializer = OrderItemSerializer(
            data=request.data,
            context={
                'request': request,
                'order_id': order.id,
            }
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
