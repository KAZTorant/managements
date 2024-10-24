
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
    def _generate_header(table):
        """Generates the header section of the receipt."""
        return (
            f"Tarix: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            "\n"
            f"Yer: {table.room.name if table and table.room else 'N/A'} "
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
            order_header = f"Sifariş {order.id}\n"
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
        header = PrinterService._generate_header(table)
        # Generate body and total from all orders
        body, total = PrinterService._generate_body_for_orders(orders)
        # Generate footer
        footer = PrinterService._generate_footer(total)
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
            response = self.send_to_printer(receipt_text)
            if response.status_code == 200:
                orders.update(is_check_printed=True)
                return True, "Çek uğurla print edildi"
            else:
                return False, "Çek print edilmədi. Printer API qoşulmayıb"
        except Table.DoesNotExist:
            return False, "Table does not exist."


class PrinterServiceJSON:
    PRINTER_URL = settings.PRINTER_URL

    @staticmethod
    def _generate_order_data(order):
        """Generates a JSON structure for a single order."""
        items = []
        total = 0
        for item in order.order_items.all():
            line_total = item.quantity * item.meal.price
            items.append({
                'name': item.meal.name,
                'quantity': item.quantity,
                'price': item.meal.price,
                'line_total': line_total
            })
            total += line_total

        return {
            'order_id': order.id,
            'items': items,
            'order_total': total
        }

    @staticmethod
    def generate_receipt_data_for_orders(table, orders):
        """
        Generates a JSON object that will be sent to Electron JS for receipt printing.
        """
        if not orders:
            return {}

        # Generate the basic information about the table and orders
        receipt_data = {
            'date': datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
            'table': {
                'room': table.room.name if table and table.room else 'N/A',
                'number': table.number if table else 'N/A'
            },
            'waitress': table.current_order.waitress.get_full_name(),
            'orders': []
        }

        # Add each order and its items to the receipt data
        for order in orders:
            receipt_data['orders'].append(
                PrinterServiceJSON._generate_order_data(order))

        return receipt_data

    def send_to_printer(self, data):
        """
        Sends the receipt data (as JSON) to the printer (Electron JS).
        """
        try:
            # Step 1: Send the data as JSON to the printer service
            response = requests.post(
                self.PRINTER_URL,
                json=data,
                headers={'Content-Type': 'application/json'}
            )

            # Return the response from the server request
            return response
        except requests.exceptions.RequestException as e:
            # Handle exceptions in sending the request
            print(f"Error while sending data to printer: {e}")
            return None

    def print_orders_for_table(self, table_id, force_print=False):
        try:
            table = Table.objects.get(pk=table_id)
            if not table.can_print_check() and not force_print:
                return False, "No active order to print or check already printed."

            orders = table.current_orders
            receipt_data = self.generate_receipt_data_for_orders(table, orders)
            response = self.send_to_printer(receipt_data)

            if response and response.status_code == 200:
                orders.update(is_check_printed=True)
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
            if not settings.PRINTER_SERVICE:
                printer = PrinterService()
            else:
                printer = PrinterServiceJSON()

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
