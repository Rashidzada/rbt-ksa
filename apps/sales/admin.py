from django.contrib import admin
from .models import VehicleForSale, SaleVehicleImage

class SaleVehicleImageInline(admin.TabularInline):
    model = SaleVehicleImage
    extra = 1
    fields = ('image', 'image_url')

@admin.register(VehicleForSale)
class VehicleForSaleAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'price', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'city', 'is_featured')
    search_fields = ('title', 'brand', 'model', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SaleVehicleImageInline]

admin.site.register(SaleVehicleImage)
