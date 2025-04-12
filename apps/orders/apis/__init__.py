
from apps.orders.apis.order_items.add import AddOrderItemAPIView
from apps.orders.apis.order_items.list import ListOrderItemsAPIView
from apps.orders.apis.order_items.remove import DeleteOrderItemAPIView

from apps.orders.apis.orders.create import CreateOrderAPIView
from apps.orders.apis.orders.check import CheckOrderAPIView
from apps.orders.apis.orders.close import CloseTableOrderAPIView
from apps.orders.apis.orders.table_orders import ListTableOrdersAPIView
from apps.orders.apis.orders.table_change import ChangeTableOrderAPIView
from apps.orders.apis.orders.table_join import JoinTableOrdersAPIView
from apps.orders.apis.orders.waitress_list import ListWaitressAPIView
from apps.orders.apis.orders.waitress_change import ChangeWaitressAPIView
