from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.orders.models import Order
from apps.orders.serializers import ListOrderSerializer

from apps.tables.models import Table
from apps.users.permissions import IsWaitressOrCapitaonOrAdminOrOwner


class ListTableOrdersAPIView(ListAPIView):
    serializer_class = ListOrderSerializer
    permission_classes = [
        IsAuthenticated,
        IsWaitressOrCapitaonOrAdminOrOwner
    ]

    def get_queryset(self):
        table_id = self.kwargs.get("table_id", 0)

        table = Table.objects.filter(id=table_id).first()
        if not table:
            return Order.objects.none()

        return table.orders.filter(is_paid=False)
