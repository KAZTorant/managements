from django.urls import path

from apps.orders.apis import CreateOrderAPIView
from apps.orders.apis import AddOrderItemAPIView
from apps.orders.apis import AddMultipleOrderItemsAPIView

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

    path(
        'add-multiple-order-items/<int:table_id>/',
        AddMultipleOrderItemsAPIView.as_view(),
        name='add-multiple-order-item'
    ),
]
