from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import socket


class NetworkAPIView(APIView):

    def get(self, request):
        ip = self.get_network_ip()
        return Response(
            {'network_ip': ip},
            status=status.HTTP_200_OK
        )

    def get_network_ip(self):
        try:
            # This gets the IP address associated with the default route
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            return ip_address
        except Exception as e:
            print(str(e))
            return 'localhost'
