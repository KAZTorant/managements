
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.orders.serializers import ListOrderItemSerializer
from apps.orders.models import Order
from apps.orders.models import OrderItem
from apps.tables.models import Table
from apps.users.permissions import IsWaitressOrCapitaonOrAdminOrOwner


class ListOrderItemsAPIView(ListAPIView):
    serializer_class = ListOrderItemSerializer
    permission_classes = [
        IsAuthenticated,
        IsWaitressOrCapitaonOrAdminOrOwner
    ]

    def get_queryset(self):
        table_id = self.kwargs.get("table_id", 0)

        table = Table.objects.filter(id=table_id).first()
        default_order_id = table.current_order.id if table and table.current_order else None

        if not default_order_id:
            return OrderItem.objects.none()

        order_id = self.request.GET.get("order_id", default_order_id)
        order = table.current_orders.filter(id=order_id).first()
        if not order:
            return OrderItem.objects.none()
        if self.request.user.type == "waitress":
            return order.order_items.order_by('-item_added_at').all()
        return order.order_items.all()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'order_id',
                openapi.IN_QUERY,
                description="Filter by order ID",
                type=openapi.TYPE_STRING
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response
