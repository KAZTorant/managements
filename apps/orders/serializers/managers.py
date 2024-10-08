from rest_framework import serializers
from apps.meals.models import Meal
from apps.orders.models import Order
from apps.orders.models import OrderItem
from apps.users.models import User

# from apps.tables.models import Table
# from apps.users.models import User


class DeleteOrderItemSerializer(serializers.Serializer):
    meal_id = serializers.IntegerField(
        help_text="ID of the meal to decrease quantity from"
    )
    order_id = serializers.IntegerField(
        help_text="ID of the order",
        required=False
    )

    quantity = serializers.IntegerField(
        help_text="Quantity to decrease", min_value=1, default=1
    )

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
        order: Order = self.context['order']

        # Try to find the order item within the order
        order_item = OrderItem.objects.filter(
            order=order,
            meal_id=meal_id
        ).first()
        if not order_item:
            raise serializers.ValidationError("Order item not found")

        # Decrease quantity or delete if necessary
        new_quantity = order_item.quantity - quantity_to_decrease
        if new_quantity > 0:
            order_item.quantity = new_quantity
            order_item.save()
        else:
            order_item.delete()
        order.refresh_from_db()
        order.update_total_price()


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
