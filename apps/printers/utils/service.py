import socket
import json
from datetime import datetime
from apps.tables.models import Table

from apps.printers.models import Printer


class DummyResponse:
    def __init__(self, status_code):
        self.status_code = status_code


class PrinterService:
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
        Generates a JSON object that will be sent directly to the printer for receipt printing.
        """
        if not orders:
            return {}

        receipt_data = {
            'date': datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
            'table': {
                'room': table.room.name if table and table.room else 'N/A',
                'number': table.number if table else 'N/A'
            },
            'waitress': table.current_order.waitress.get_full_name(),
            'orders': []
        }

        for order in orders:
            receipt_data['orders'].append(
                PrinterService._generate_order_data(order)
            )

        return receipt_data

    def send_to_printer(self, data):
        """
        Sends the receipt data as JSON directly to the connected printer using a socket connection.
        The method queries the Printer model for the main printer (is_main=True) to obtain its IP and port.
        """
        # Get the main printer from the Printer model.
        printer = Printer.objects.filter(is_main=True).first()
        if not printer:
            raise Exception("No main printer configured in the system.")

        ip_address = printer.ip_address
        port = printer.port

        try:
            # Convert the receipt data to a JSON string.
            json_data = json.dumps(data)
            # Open a socket connection to the printer and send the JSON data.
            with socket.create_connection((ip_address, port), timeout=5) as s:
                s.sendall(json_data.encode('utf-8'))
            # If sending is successful, return a dummy response with status code 200.
            return DummyResponse(200)
        except Exception as e:
            print(f"Error while sending data to printer: {e}")
            return DummyResponse(500)

    def print_orders_for_table(self, table_id, force_print=False):
        """
        Retrieves the table by ID, checks if printing is allowed,
        generates the receipt JSON data, and sends it directly to the printer.
        """
        try:
            table = Table.objects.get(pk=table_id)
            if not table.can_print_check() and not force_print:
                return False, "No active order to print or check already printed."

            orders = table.current_orders
            receipt_data = self.generate_receipt_data_for_orders(table, orders)
            response = self.send_to_printer(receipt_data)

            if response.status_code == 200:
                orders.update(is_check_printed=True)
                return True, "Çek uğurla print edildi"
            else:
                return False, "Çek print edilmədi. Printer is not connected."
        except Table.DoesNotExist:
            return False, "Table does not exist."
