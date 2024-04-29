from django.urls import path

from apps.users.apis import PinLoginAPIView

urlpatterns = [
    path(
        "login/",
        PinLoginAPIView.as_view(),
    )
]
