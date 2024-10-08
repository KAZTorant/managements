from rest_framework.views import APIView


from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.orders.models import Order
from apps.tables.models import Table


from apps.users.permissions import IsAdminOrOwner


class JoinTableOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    @swagger_auto_schema(
        operation_description="Join other tables' orders to a table's order",
        responses={
            200: openapi.Response(description='Table successfully joined.'),
            400: openapi.Response(description='Table could not be joined.'),
            404: openapi.Response(description='Table not found.'),
        },        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'other_table_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    description="List of IDs of other tables whose orders should be joined."
                ),
            },
            required=['other_table_ids']
        ),
    )
    def post(self, request, table_id):
        try:
            table = Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            return Response({"detail": "Table not found."}, status=status.HTTP_404_NOT_FOUND)

        # Extract other table ids from request data
        other_table_ids = request.data.get('other_table_ids', [])
        if not other_table_ids:
            return Response({"detail": "No other table IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get all tables to be joined
            other_tables = Table.objects.filter(id__in=other_table_ids)
            if not other_tables.exists():
                return Response({"detail": "No valid tables found to join."}, status=status.HTTP_400_BAD_REQUEST)

            # Get all unpaid orders from the tables to be joined
            orders_to_join = Order.objects.filter(
                table__in=other_tables, is_paid=False)
            if not orders_to_join.exists():
                return Response({"detail": "No unpaid orders found to join."}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure the target table has a current order before proceeding
            if not table.current_order:
                return Response({"detail": "The target table must have a current order."}, status=status.HTTP_400_BAD_REQUEST)

            # Update all orders to be linked to the target table
            orders_to_join.update(
                table=table,
                is_main=False,
                waitress=table.current_order.waitress
            )

            return Response({"detail": "Tables successfully joined."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
