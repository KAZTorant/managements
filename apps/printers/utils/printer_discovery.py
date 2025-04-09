# printers/utils/printer_discovery.py

import concurrent.futures
import platform
import socket

import cups


def get_printer_name(ip, port=9100, timeout=1):
    try:
        with socket.create_connection((ip, port), timeout=timeout) as conn:
            conn.sendall(b"\x1b\x21\x00")
            return "POS Printer"
    except Exception:
        return None


def is_printer(ip, port=9100, timeout=1):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False


def scan_network_printers(base_ip='192.168.1.', port=9100):
    """
    Scans the subnet for printers listening on port 9100.
    Returns list of {'type': 'network', 'ip': ..., 'name': ...}
    """
    found = []

    def check_ip(i):
        ip = f"{base_ip}{i}"
        if is_printer(ip, port):
            name = get_printer_name(ip, port) or "Unknown Network Printer"
            return {"type": "network", "ip": ip, "name": name}
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(check_ip, range(1, 255))

    return [res for res in results if res is not None]


def get_local_cups_printers():
    """
    Uses CUPS to get local (USB or system-configured) printers.
    Returns list of {'type': 'usb/local', 'name': ..., 'info': ...}
    """
    printers = []
    try:
        conn = cups.Connection()
        local_printers = conn.getPrinters()
        for name, info in local_printers.items():
            printers.append({
                "type": "usb/local",
                "name": name,
                "info": info.get("printer-info", ""),
                "location": info.get("printer-location", ""),
                "device_uri": info.get("device-uri", "")
            })
    except Exception as e:
        print(f"[!] Error accessing CUPS: {e}")
    return printers


def discover_all_printers():
    """
    Combines network + local printer discovery.
    """
    if platform.system() not in ["Linux", "Darwin"]:
        raise EnvironmentError("Only supported on Linux/macOS systems.")

    network = scan_network_printers()
    local = get_local_cups_printers()
    return network + local
