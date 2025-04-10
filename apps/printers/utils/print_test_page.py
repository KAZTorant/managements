import os

import cups


def send_test_page(printer_name):
    try:
        conn = cups.Connection()

        # Check if the printer exists
        printers = conn.getPrinters()
        print(printers)
        if printer_name not in printers:
            return False, f"Printer '{printer_name}' not found."

        # Check if printer is accepting jobs and not disabled
        printer_attrs = conn.getPrinterAttributes(printer_name)
        if not printer_attrs.get("printer-is-accepting-jobs", False):
            return False, f"Printer '{printer_name}' is not accepting jobs."
        if printer_attrs.get("printer-state", 0) == 5:  # 5 = stopped
            return False, f"Printer '{printer_name}' is stopped."

        # Receipt content
        receipt_text = """
        ============================
              KAZZA CAFE
        ============================
        Order #12345
        Table: 4
        Server: Elvin

        ----------------------------
        2x Latte             10.00₼
        1x Burger            12.50₼
        1x Fries              4.00₼
        ----------------------------
        Total:              26.50₼
        ----------------------------
        Thank you for dining with us!
        ============================
        """

        # File path in utils folder
        receipt_path = os.path.join(os.path.dirname(__file__), 'receipt.txt')

        # Write to file
        with open(receipt_path, 'w') as f:
            f.write(receipt_text)

        # Confirm file exists
        if not os.path.exists(receipt_path):
            return False, "Receipt file was not created."

        print(f"[✓] Sending to printer '{printer_name}' — file: {receipt_path}")

        # Send to printer
        conn.printFile(printer_name, receipt_path, "Test Receipt", {})

        # Uncomment if you want to auto-delete after printing
        # os.remove(receipt_path)

        return True, f"Receipt successfully sent to '{printer_name}'"
    except Exception as e:
        return False, f"[✗] Error: {str(e)}"
