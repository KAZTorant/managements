
import os
import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.users.permissions import IsAdminOrOwner
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
                f"{index}. {name:.<6} {quantity} x {price:,.1f} = {line_total:,.1f}\n"
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
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text)

            # Step 2: Send the file via multipart/form-data
            with open(file_path, "rb") as file:
                files = {'textFile': ('temp_print.txt', file, 'text/plain')}
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

    def print_order_for_table(self, table_id, force_print=False):
        try:
            table = Table.objects.get(pk=table_id)
            if not table.can_print_check() and not force_print:
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
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

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


class PrinterServiceV2:
    PRINTER_URL = settings.PRINTER_URL

    @staticmethod
    def _generate_header(table):
        """Generates the header section of the receipt."""
        return (
            f"Tarix: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            "\n"
            f"Zal: {table.room.name if table and table.room else 'N/A'} "
            f"{table.number if table else 'N/A'}\n"
            f"Ofisiant: {table.current_order.waitress.get_full_name()}\n"
            + "-" * 25 + "\n"
        )

    @staticmethod
    def _generate_body_for_orders(orders):
        """Generates the body section listing all items from multiple orders."""
        body = []
        total = 0
        item_index = 1  # Running index for all items

        for order in orders:
            # Include order-specific header
            order_header = f"Sifariş ID: {order.id}\n"
            body.append(order_header)
            order_total = 0
            items = order.order_items.all()
            for item in items:
                name = item.meal.name
                quantity = item.quantity
                price = item.meal.price
                line_total = quantity * price
                body.append(
                    f"{item_index}. {name:.<20} {quantity} x {price:,.1f} = {line_total:,.1f}\n"
                )
                total += line_total
                order_total += line_total
                item_index += 1
            body.append(f"Sifariş məbləği: {order_total:,.2f} AZN\n")
            body.append("-" * 25 + "\n")  # Separator between orders

        return ''.join(body), total

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
    def generate_receipt_text_for_orders(table, orders):
        """
        Generates a formatted receipt text from multiple orders.
        """
        if not orders:
            return ""
        # Generate header using table information
        header = PrinterServiceV2._generate_header(table)
        # Generate body and total from all orders
        body, total = PrinterServiceV2._generate_body_for_orders(orders)
        # Generate footer
        footer = PrinterServiceV2._generate_footer(total)
        return f"\n{header}{body}{footer}\n"

    def send_to_printer(self, text):
        # Define the file path for the temporary .txt file
        file_path = "apps/files/temp_print.txt"

        try:
            # Step 1: Write the text to a .txt file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text)

            # Step 2: Send the file via multipart/form-data
            with open(file_path, "rb") as file:
                files = {'textFile': ('temp_print.txt', file, 'text/plain')}
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

    def print_orders_for_table(self, table_id, force_print=False):
        try:
            table = Table.objects.get(pk=table_id)
            if not table.can_print_check() and not force_print:
                return False, "No active order to print or check already printed."

            orders = table.current_orders
            receipt_text = self.generate_receipt_text_for_orders(table, orders)
            print(receipt_text)
            response = self.send_to_printer(receipt_text)
            if response.status_code == 200:
                orders.update(is_check_printed=True)
                return True, "Çek uğurla print edildi"
            else:
                return False, "Çek print edilmədi. Printer API qoşulmayıb"
        except Table.DoesNotExist:
            return False, "Table does not exist."


class PrintCheckAPIViewV2(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def post(self, request, table_id):
        if not table_id:
            return Response({"error": "Table ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            printer = PrinterServiceV2()

            success, message = printer.print_orders_for_table(table_id)
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
        orders = table.current_orders
        if not orders.exists():
            return Response({"error": "Masa üçün sifariş tapılmadı."}, status=status.HTTP_404_NOT_FOUND)

        if table.can_print_check():
            return Response({"error": "Masa üçün çek print etmək mümkündür."}, status=status.HTTP_404_NOT_FOUND)
        orders.update(is_check_printed=False)
        table.save()

        return Response({"success": True, "message": "Masa üçün yenidən çek print etmək mümkündür."}, status=status.HTTP_200_OK)
