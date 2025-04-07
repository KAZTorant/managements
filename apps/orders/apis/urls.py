from django.urls import path

from apps.orders.apis import CreateOrderAPIView
from apps.orders.apis import CheckOrderAPIView

from apps.orders.apis import AddOrderItemAPIView
from apps.orders.apis import ListOrderItemsAPIView
from apps.orders.apis import DeleteOrderItemAPIView

from apps.orders.apis import CloseTableOrderAPIView
from apps.orders.apis import ChangeTableOrderAPIView
from apps.orders.apis import JoinTableOrdersAPIView
from apps.orders.apis import ListTableOrdersAPIView

from apps.orders.apis import ListWaitressAPIView
from apps.orders.apis import ChangeWaitressAPIView

from apps.orders.apis import PrintCheckAPIView

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
        AddOrderItemAPIView.as_view(),
        name='add-order-item'
    ),


    path(
        '<int:table_id>/delete-order-item/',
        DeleteOrderItemAPIView.as_view(),
        name='delete-order-item'
    ),

    path(
        '<int:table_id>/list-order-items/',
        ListOrderItemsAPIView.as_view(),
        name='list-order-items'
    ),

    path(
        '<int:table_id>/list-orders/',
        ListTableOrdersAPIView.as_view(),
        name='list-orders'
    ),

    path(
        '<int:table_id>/change-table-for-order/',
        ChangeTableOrderAPIView.as_view(),
        name='change-table-for-order'
    ),

    path(
        '<int:table_id>/join-tables-orders/',
        JoinTableOrdersAPIView.as_view(),
        name='join-tables-orders'
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
        PrintCheckAPIViewV2.as_view(),
        name='print-check'
    ),
]
