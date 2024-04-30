from django.urls import path

from apps.orders.apis import CreateOrderAPIView
from apps.orders.apis import AddOrderItemAPIView
from apps.orders.apis import AddMultipleOrderItemsAPIView
from apps.orders.apis import DeleteOrderItemAPIView
from apps.orders.apis import ListOrderItemsAPIView
from apps.orders.apis import ChangeOrderTableAPIView
from apps.orders.apis import CloseTableOrderAPIView

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

    path(
        'delete-order-item/<int:table_id>/',
        DeleteOrderItemAPIView.as_view(),
        name='delete-order-item'
    ),

    path(
        'list-order-items/<int:table_id>/',
        ListOrderItemsAPIView.as_view(),
        name='list-order-itemsm'
    ),

    path(
        'change-table-for-order/<int:table_id>/',
        ChangeOrderTableAPIView.as_view(),
        name='change-table-for-order'
    ),

    path(
        'close-table-for-order/<int:table_id>/',
        CloseTableOrderAPIView.as_view(),
        name='close-table-for-order'
    ),
]
