from rest_framework import serializers
from django.db import transaction
from django.utils import timezone

from apps.meals.models import Meal
from apps.orders.models import Order
from apps.orders.models import OrderItem


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'table')

    def create(self, validated_data):
        validated_data["waitress"] = self.context['request'].user
        order = Order.objects.create(**validated_data)
        return order


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


class OrderItemInputSerializer(serializers.Serializer):
    meal_id = serializers.IntegerField(
        required=True, help_text="ID of the meal to add to the order.")
    quantity = serializers.IntegerField(
        required=True, min_value=1, help_text="Quantity of the meal to order.")


class OrderItemOutputSerializer(serializers.Serializer):
    meal_id = serializers.IntegerField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)


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
