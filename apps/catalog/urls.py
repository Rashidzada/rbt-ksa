from django.urls import path
from .views import VehicleListView, VehicleDetailView

app_name = 'catalog'

urlpatterns = [
    path('category/<slug:slug>/', VehicleListView.as_view(), name='vehicle_list'),
    path('vehicle/<slug:slug>/', VehicleDetailView.as_view(), name='vehicle_detail'),
]
