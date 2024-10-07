
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated


from apps.orders.serializers import ListOrderItemSerializer
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
        order = table.current_order if table else None

        return (
            order.order_items.order_by('-item_added_at').all()
            if order else
            OrderItem.objects.none()
        )

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        return response
