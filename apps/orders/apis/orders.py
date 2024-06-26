
from django.utils import timezone
from apps.meals.models import Meal
from apps.orders.models import Order
from apps.orders.models import OrderItem
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.tables.models import Table

from apps.users.permissions import IsWaitressOrOrCapitaonOrAdminOrOwner

from django.db.models import F


class CheckOrderAPIView(APIView):
    permission_classes = [IsAuthenticated,
                          IsWaitressOrOrCapitaonOrAdminOrOwner]

    def get(self, request, table_id):
        # Check if there is an existing unpaid order for this table
        if Order.objects.filter(table__id=table_id, is_paid=False).exists():
            return Response(
                {'message': 'Sifariş yaradılıb'},
                status=status.HTTP_200_OK
            )

        return Response(
            {'message': 'Sifariş yoxdur.'},
            status=status.HTTP_404_NOT_FOUND
        )


# CreateOrderAPI
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'table')

    def create(self, validated_data):
        validated_data["waitress"] = self.context['request'].user
        order = Order.objects.create(**validated_data)
        return order


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated,
                          IsWaitressOrOrCapitaonOrAdminOrOwner]

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


# AddOrderItemAPI
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
        with transaction.atomic():
            # Extract meal details and fetch the meal instance
            meal_data = validated_data.pop('meal', None)
            meal_id = meal_data.get("id", 0)
            meal = Meal.objects.filter(id=meal_id).first()

            # Default to 1 if not specified
            quantity = validated_data.get('quantity', 1)

            # Fetch the order instance and lock it
            order = Order.objects.select_for_update().get(
                id=self.context['order_id'])

            # Attempt to get or create the order item
            order_item, created = OrderItem.objects.get_or_create(
                meal=meal,
                order=order,
                defaults={
                    'quantity': quantity,
                    'price': meal.price * quantity
                }
            )

            # If the order item was not created, it means it already exists, so update the quantity
            if not created:
                # Since we're in a transaction block with select_for_update, we can safely update
                order_item.quantity += quantity
                order_item.price += meal.price * quantity
                order_item.item_added_at = timezone.now()
                order_item.save()

            # Update the total price of the order
            order.update_total_price()

            # Ensure changes are persisted and visible outside this function
            order_item.refresh_from_db()

        return order_item


class AddOrderItemAPIView(APIView):
    permission_classes = [IsAuthenticated,
                          IsWaitressOrOrCapitaonOrAdminOrOwner]

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

        if request.user.type in ["admin", 'captain_waitress', 'restaurant']:
            table = Table.objects.filter(id=table_id).first()
            order = table.current_order if table else None

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


class AddOrderItemAPIViewV2(APIView):
    permission_classes = [IsAuthenticated,
                          IsWaitressOrOrCapitaonOrAdminOrOwner]

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


# AddMultipleOrderItemsAPIView


class OrderItemInputSerializer(serializers.Serializer):
    meal_id = serializers.IntegerField(
        required=True, help_text="ID of the meal to add to the order.")
    quantity = serializers.IntegerField(
        required=True, min_value=1, help_text="Quantity of the meal to order.")


class OrderItemOutputSerializer(serializers.Serializer):
    meal_id = serializers.IntegerField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)


class AddMultipleOrderItemsAPIView(APIView):
    permission_classes = [IsAuthenticated,
                          IsWaitressOrOrCapitaonOrAdminOrOwner]

    @swagger_auto_schema(
        operation_description="Add multiple items to an existing unpaid order for a specified table.",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                'meal_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the meal to add to the order.'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantity of the meal to order.', minimum=1),
            }),
            description="List of meals and their quantities to add to the order."
        ),
        responses={
            201: openapi.Response('Order items successfully added or updated.', OrderItemOutputSerializer(many=True)),
            404: openapi.Response(description='Order not found or payment already made.'),
            400: openapi.Response(description='Invalid data received.'),
        }
    )
    def post(self, request, table_id):
        # Retrieve the order, validate its existence and status
        order = self.get_order(request.user, table_id)
        if isinstance(order, Response):  # Error handling in case of a response object
            return order

        items = request.data  # This should be a list of dicts with 'meal_id' and 'quantity'

        # Process the items and handle any potential errors
        result = self.process_items(order, items)
        if isinstance(result, Response):  # Error handling in case of a response object
            return result

        order.update_total_price()
        # Successful processing
        return Response({
            'message': 'Order items added or updated successfully.',
            'items': result
        }, status=status.HTTP_201_CREATED)

    def get_order(self, user, table_id):
        """Retrieve and validate the order for the given table and user."""
        order = user.orders.filter(table__id=table_id, is_paid=False).first()

        if user.type in ["admin", 'captain_waitress']:
            table = Table.objects.filter(id=table_id).first()
            order = table.current_order if table else None

        if not order:
            return Response(
                {'error': 'Order not found or payment has been made already.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return order

    def process_items(self, order, items):
        """Process multiple items, adding them to the order."""
        created_items = []

        try:
            with transaction.atomic():
                for item in items:
                    meal, response = self.validate_meal(item.get('meal_id'))
                    if response:
                        return response

                    quantity = item.get('quantity', 1)
                    order_item, created = OrderItem.objects.get_or_create(
                        meal=meal,
                        order=order,
                        defaults={'quantity': quantity}
                    )

                    if not created:
                        order_item.quantity += quantity
                        order_item.save()

                    created_items.append({
                        'meal_id': order_item.meal.id,
                        'quantity': order_item.quantity
                    })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return created_items

    def validate_meal(self, meal_id):
        """Validate the meal ID and return the Meal object or an error response."""
        if not meal_id:
            return None, Response({'error': 'Meal ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            meal = Meal.objects.get(id=meal_id)
            return meal, None
        except Meal.DoesNotExist:
            return None, Response({'error': f'Meal with ID {meal_id} not found'}, status=status.HTTP_400_BAD_REQUEST)


# Orders List view
class ListOrderItemSerializer(serializers.ModelSerializer):

    meal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            "meal",
            "quantity",
        )

    def get_meal(self, obj: OrderItem):
        return {
            "id": obj.meal.id,
            "name": obj.meal.name,
            "price": obj.meal.price,
            "description": obj.meal.description,
        }


class ListOrderItemsAPIView(ListAPIView):
    serializer_class = ListOrderItemSerializer
    permission_classes = [IsAuthenticated,
                          IsWaitressOrOrCapitaonOrAdminOrOwner]

    def get_queryset(self):
        table_id = self.kwargs.get("table_id", 0)
        table = Table.objects.filter(id=table_id).first()
        order = table.current_order if table else None

        return (
            order.order_items.order_by('-item_added_at').all()
            if order else
            OrderItem.objects.none()
        )

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        return response
