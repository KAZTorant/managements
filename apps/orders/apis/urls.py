from django.urls import path

from apps.orders.apis import CreateOrderAPIView
from apps.orders.apis import CheckOrderAPIView

from apps.orders.apis import AddOrderItemAPIView
from apps.orders.apis import AddOrderItemAPIViewV2
from apps.orders.apis import AddMultipleOrderItemsAPIView
from apps.orders.apis import DeleteOrderItemAPIView
from apps.orders.apis import ListOrderItemsAPIView
from apps.orders.apis import ChangeOrderTableAPIView
from apps.orders.apis import CloseTableOrderAPIView
from apps.orders.apis import ListWaitressAPIView
from apps.orders.apis import ChangeWaitressAPIView
from apps.orders.apis import PrintCheckAPIView
from apps.orders.apis import DeleteOrderItemAPIViewV2

urlpatterns = [
    path(
        '<int:table_id>/check-status/',
        CheckOrderAPIView.as_view(),
        name='check-table-status'
    ),

    path(
        '<int:table_id>/create/',
        CreateOrderAPIView.as_view(),
        name='create-order'
    ),

    path(
        '<int:table_id>/add-order-item/',
        AddOrderItemAPIViewV2.as_view(),
        name='add-order-item'
    ),


    path(
        '<int:table_id>/add-multiple-order-items/',
        AddMultipleOrderItemsAPIView.as_view(),
        name='add-multiple-order-item'
    ),

    path(
        '<int:table_id>/delete-order-item/',
        DeleteOrderItemAPIViewV2.as_view(),
        name='delete-order-item'
    ),

    path(
        '<int:table_id>/list-order-items/',
        ListOrderItemsAPIView.as_view(),
        name='list-order-itemsm'
    ),

    path(
        '<int:table_id>/change-table-for-order/',
        ChangeOrderTableAPIView.as_view(),
        name='change-table-for-order'
    ),

    path(
        '<int:table_id>/close-table-for-order/',
        CloseTableOrderAPIView.as_view(),
        name='close-table-for-order'
    ),

    path(
        'list-waitress/',
        ListWaitressAPIView.as_view(),
        name='list-waitress'
    ),

    path(
        '<int:table_id>/change-waitress/',
        ChangeWaitressAPIView.as_view(),
        name='change-waitress'
    ),

    path(
        '<int:table_id>/print-check/',
        PrintCheckAPIView.as_view(),
        name='print-check'
    ),
]
