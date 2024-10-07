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

        order: Order = table.current_order

        if not order:
            return Response(
                {"success": False, "message": "Masada sifariş yoxdur."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            printer_service = PrinterService()
            success, message = printer_service.print_order_for_table(
                table_id, False)
        except Exception as e:
            print("Printer error", str(e))

        order.is_paid = True
        order.save()

        return Response(
            {"success": True, "message": "Sifariş uğurla bağlamşdır."},
            status=status.HTTP_200_OK
        )
