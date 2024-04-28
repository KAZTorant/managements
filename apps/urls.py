from django.urls import path, include

urlpatterns = [
    path('tables/', include('apps.tables.apis.urls')),
    path('meals/', include('apps.meals.apis.urls')),
]
