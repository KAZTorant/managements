from django.urls import path
from apps.tables.apis import TableAPIView
from apps.tables.apis import TableDetailAPIView
from apps.tables.apis import RoomAPIView

urlpatterns = [
    path("<int:room_id>/tables/", TableAPIView.as_view()),
    path("rooms/", RoomAPIView.as_view()),
    path("<int:table_id>/details", TableDetailAPIView.as_view()),
]
