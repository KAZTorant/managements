import socket


def send_raw_receipt(ip: str, port: int = 9100):
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

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            s.sendall(receipt_text.encode("utf-8"))
        return True, "✅ Receipt sent successfully over TCP."
    except Exception as e:
        return False, f"❌ Failed to send receipt: {str(e)}"
