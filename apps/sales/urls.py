from django.urls import path
from .views import SaleVehicleListView, SaleVehicleDetailView

app_name = 'sales'

urlpatterns = [
    path('', SaleVehicleListView.as_view(), name='vehicle_list'),
    path('<slug:slug>/', SaleVehicleDetailView.as_view(), name='vehicle_detail'),
]
