from django.urls import path

from apps.printers.apis import PrintCheckAPIView


urlpatterns = [
    path(
        '<int:table_id>/print-check/',
        PrintCheckAPIView.as_view(),
        name='print-check'
    ),
]
