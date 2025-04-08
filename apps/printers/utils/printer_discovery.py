# printers/utils/printer_discovery.py

import socket
import concurrent.futures


def get_printer_name(ip, port=9100, timeout=1):
    """
    Dummy implementation to get the printer name.
    You may customize this to use SNMP or another protocol if available.
    """
    try:
        with socket.create_connection((ip, port), timeout=timeout) as conn:
            # ESC/POS command (this example won't really return a name)
            conn.sendall(b"\x1b\x21\x00")
            # In a real implementation, you might read and parse the response
            return "POS Printer"
    except Exception:
        return None


def is_printer(ip, port=9100, timeout=1):
    """
    Attempts to connect to the given IP and port.
    Returns True if a connection is successful.
    """
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False


def scan_printers_with_names(base_ip='192.168.1.', port=9100):
    """
    Scans the local subnet (e.g., 192.168.1.1 to 192.168.1.254) for printers on the specified port.
    Returns a list of dictionaries containing the printer's IP and name.
    """
    found = []

    def check_ip(i):
        ip = f"{base_ip}{i}"
        if is_printer(ip, port):
            name = get_printer_name(ip, port) or "Unknown Printer"
            return {"ip": ip, "name": name}
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(check_ip, range(1, 255))

    return [res for res in results if res is not None]
