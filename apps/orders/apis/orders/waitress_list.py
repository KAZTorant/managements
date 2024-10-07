from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.orders.serializers import ListWaitressSerializer
from apps.users.permissions import IsAdminOrOwner
from apps.users.models import User


class ListWaitressAPIView(ListAPIView):

    serializer_class = ListWaitressSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        return User.objects.filter(type="waitress")
