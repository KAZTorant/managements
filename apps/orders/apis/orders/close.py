from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.apis.printer import PrinterService
from apps.orders.models import Order
from apps.tables.models import Table

from apps.users.permissions import IsAdminOrOwner


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

        orders = table.current_orders

        if not orders.exists():
            return Response(
                {"success": False, "message": "Masada sifariş yoxdur."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            printer = PrinterService()
            printer.print_order_for_table(table_id, False)
        except Exception as e:
            print("Printer error", str(e))

        orders.update(is_paid=True)
        return Response(
            {"success": True, "message": "Sifariş uğurla bağlamşdır."},
            status=status.HTTP_200_OK
        )
