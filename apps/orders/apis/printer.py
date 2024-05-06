
import os
import requests
import json
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.users.permissions import IsAdmin
from apps.tables.models import Table

from datetime import datetime
from django.conf import settings


class PrinterService:
    PRINTER_URL = settings.PRINTER_URL

    @staticmethod
    def _generate_header(order):
        """Generates the header section of the receipt."""
        return (
            f"Tarix: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            "\n"
            f"Ofisiant: {order.waitress.get_full_name() if order.waitress else 'N/A'}\n"
            "\n"
            f"Zal: {order.table.room.name if order.table and order.table.room else 'N/A'} "
            f"{order.table.number if order.table else 'N/A'}\n"
            + "-" * 25 + "\n"
        )

    @staticmethod
    def _generate_body(items):
        """Generates the body section listing all the items."""
        body = []
        for index, item in enumerate(items, start=1):
            name = item.meal.name
            quantity = item.quantity
            price = item.meal.price
            line_total = quantity * price
            body.append(
                f"{index}. {name:.<9} {quantity} x {price:,.2f} = {line_total:,.2f}\n"
            )
        return ''.join(body), sum(item.quantity * item.meal.price for item in items)

    @staticmethod
    def _generate_footer(total):
        """Generates the footer section of the receipt."""
        return (
            "-" * 25 + "\n"
            "\n"
            f"Ümumi məbləğ: {total:,.2f} AZN\n"
            "\n"
            "Nuş Olsun!\nTəşəkkür edirik!\n"
        )

    @staticmethod
    def generate_receipt_text(order):
        """
        Generates a formatted receipt text from an order.
        Delegates the creation of each receipt section to helper methods.
        """
        header = PrinterService._generate_header(order)
        body, total = PrinterService._generate_body(order.order_items.all())
        footer = PrinterService._generate_footer(total)

        return f"\n{header}{body}{footer}\n"

    # def send_to_printer(self, text):
    #     response = requests.post(
    #         self.PRINTER_URL,
    #         json={"text": text},
    #         headers={
    #             "Content-Type": "application/json"
    #         }
    #     )
    #     return response

    def send_to_printer(self, text):
        # Define the file path for the temporary .txt file
        file_path = "apps/files/temp_print.txt"

        try:
            # Step 1: Write the text to a .txt file
            with open(file_path, "w") as file:
                file.write(text)

            # Step 2: Send the file via multipart/form-data
            with open(file_path, "rb") as file:
                files = {'printFile': ('temp_print.txt', file, 'text/plain')}

                print(self.PRINTER_URL)
                response = requests.post(
                    self.PRINTER_URL,
                    files=files
                )

            # Return the response from the server request
            return response

        finally:
            # Step 3: Delete the temporary file
            if os.path.exists(file_path):
                os.remove(file_path)

    def soft_print_order(self, text):
        try:
            file_path = "receipt.txt"
            with open(file_path, "w") as file:
                file.write(text)
            return True, file_path
        except Exception as e:
            return False, str(e)

    def print_order_for_table(self, table_id):
        try:
            table = Table.objects.get(pk=table_id)
            if not table.can_print_check():
                return False, "No active order to print or check already printed."

            order = table.current_order
            if not order:
                return False, "Aktiv sifariş tapılmadı."

            receipt_text = self.generate_receipt_text(order)

            response = self.send_to_printer(receipt_text)
            if response.status_code == 200:
                order.is_check_printed = True
                order.save()
                return True, "Çek uğurla print edildi"
            else:
                return False, "Çek print edilmədi. Printer API qoşulmayıb"
        except Table.DoesNotExist:
            return False, "Table does not exist."


class PrintCheckAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, table_id):
        if not table_id:
            return Response({"error": "Table ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            printer_service = PrinterService()

            success, message = printer_service.print_order_for_table(table_id)
            if success:
                return Response({"message": message}, status=status.HTTP_200_OK)
            else:
                return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, table_id):
        if not table_id:
            return Response({"error": "Table ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        table = Table.objects.filter(id=table_id).first()
        if not table:
            return Response({"error": "Masa tapılmadı."}, status=status.HTTP_404_NOT_FOUND)
        order = table.current_order
        if not order:
            return Response({"error": "Masa üçün sifariş tapılmadı."}, status=status.HTTP_404_NOT_FOUND)

        if table.can_print_check():
            return Response({"error": "Masa üçün çek print etmək mümkündür."}, status=status.HTTP_404_NOT_FOUND)

        order.is_check_printed = False
        order.save()
        table.save()

        return Response({"success": True, "message": "Masa üçün yenidən çek print etmək mümkündür."}, status=status.HTTP_200_OK)

    # def get(self, request, table_id):
    #     if not table_id:
    #         return Response({"error": "Table ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    #     try:
    #         printer_service = PrinterService()
    #         success, message = printer_service.print_order_for_table(
    #             table_id, soft=True)
    #         if success:
    #             return Response({"message": message}, status=status.HTTP_200_OK)
    #         else:
    #             return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
