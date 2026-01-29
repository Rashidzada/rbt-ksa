from django.views.generic import ListView, DetailView
from .models import VehicleForSale

class SaleVehicleListView(ListView):
    model = VehicleForSale
    template_name = 'sales/sale_list.html'
    context_object_name = 'vehicles'

    def get_queryset(self):
        return VehicleForSale.objects.prefetch_related('images')

class SaleVehicleDetailView(DetailView):
    model = VehicleForSale
    template_name = 'sales/sale_detail.html'
    context_object_name = 'vehicle'

    def get_queryset(self):
        return VehicleForSale.objects.prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = context['vehicle']
        primary = vehicle.primary_image
        if primary:
            gallery_qs = vehicle.images.exclude(id=primary.id)
        else:
            gallery_qs = vehicle.images.all()
        context['gallery_images'] = [img for img in gallery_qs if img.resolved_url]
        return context
