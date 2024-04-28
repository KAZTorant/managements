from django.urls import path

from apps.orders.apis import CreateOrderAPIView
from apps.orders.apis import AddOrderItemAPIView

urlpatterns = [
    path(
        'create/<int:table_id>/',
        CreateOrderAPIView.as_view(),
        name='create-order'
    ),

    path(
        'add-order-item/<int:table_id>/',
        AddOrderItemAPIView.as_view(),
        name='add-order-item'
    ),
]
