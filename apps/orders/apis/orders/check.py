from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.status import HTTP_200_OK

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order
from apps.users.permissions import IsWaitressOrCapitaonOrAdminOrOwner


class CheckOrderAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsWaitressOrCapitaonOrAdminOrOwner
    ]

    def get(self, request, table_id):
        orders = Order.objects.filter(table__id=table_id, is_paid=False)

        if orders.exists():
            return Response(
                {'message': 'Sifariş yaradılıb'},
                status=HTTP_200_OK
            )

        return Response(
            {'message': 'Sifariş yoxdur.'},
            status=HTTP_404_NOT_FOUND
        )
