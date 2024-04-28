from django.urls import path
from apps.tables.apis import TableAPIView

urlpatterns = [
    path("<int:room_id>/tables", TableAPIView.as_view()),
]
