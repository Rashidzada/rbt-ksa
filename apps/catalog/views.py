from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Category, Vehicle

class VehicleListView(ListView):
    model = Vehicle
    template_name = 'catalog/vehicle_list.html'
    context_object_name = 'vehicles'

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'], is_active=True)
        queryset = (
            Vehicle.objects.filter(category=self.category, is_active=True)
            .select_related('category')
            .prefetch_related('images')
        )
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(features_text__icontains=query)
                | Q(price_text__icontains=query)
                | Q(fuel_type__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['query'] = self.request.GET.get('q', '').strip()
        return context

class VehicleDetailView(DetailView):
    model = Vehicle
    template_name = 'catalog/vehicle_detail.html'
    context_object_name = 'vehicle'

    def get_queryset(self):
        return (
            Vehicle.objects.filter(is_active=True)
            .select_related('category')
            .prefetch_related('images')
        )

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
