from django.urls import path

from apps.users.apis import PinLoginAPIView
from apps.users.apis import NetworkAPIView

urlpatterns = [
    path(
        "login/",
        PinLoginAPIView.as_view(),
    ),
    path(
        "network-ip/",
        NetworkAPIView.as_view(),
    )
]
