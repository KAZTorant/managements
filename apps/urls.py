from django.urls import path, include

urlpatterns = [
    path('tables/', include('apps.tables.apis.urls')),
    path('meals/', include('apps.meals.apis.urls')),
    path('orders/', include('apps.orders.apis.urls')),
    path('users/', include('apps.users.apis.urls')),
    path('finance/', include('apps.finance.urls')),
]
