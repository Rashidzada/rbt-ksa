from django.contrib import admin
from .models import Category, Vehicle, VehicleImage

class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price_text', 'capacity_text', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description', 'features_text')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [VehicleImageInline]

admin.site.register(VehicleImage)
