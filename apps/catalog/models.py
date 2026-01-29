from django.db import models
import re
from django.utils.text import slugify
from django.utils.functional import cached_property

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon_text = models.CharField(max_length=50, help_text="Emoji or FontAwesome icon class")
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Vehicle(models.Model):
    FUEL_PETROL = 'petrol'
    FUEL_DIESEL = 'diesel'
    FUEL_HYBRID = 'hybrid'
    FUEL_ELECTRIC = 'electric'
    FUEL_CHOICES = [
        (FUEL_PETROL, 'Petrol'),
        (FUEL_DIESEL, 'Diesel'),
        (FUEL_HYBRID, 'Hybrid'),
        (FUEL_ELECTRIC, 'Electric'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='vehicles')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    price_text = models.CharField(max_length=100, help_text="e.g. 500 SAR / Day")
    capacity_text = models.CharField(max_length=100, help_text="e.g. 4 Seats")
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default=FUEL_PETROL)
    description = models.TextField()
    features_text = models.TextField(help_text="Separate features with a comma")
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="Optional: specific number for this vehicle")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def features_list(self):
        return [f.strip() for f in self.features_text.split(',') if f.strip()]

    def __str__(self):
        return self.name

    @cached_property
    def primary_image(self):
        return self.images.order_by('-is_primary', 'sort_order', 'id').first()

    @property
    def primary_image_url(self):
        image = self.primary_image
        return image.resolved_url if image else ''

    @property
    def whatsapp_message(self):
        return (
            f"Hello, I'm interested in the {self.name} "
            f"({self.category.name}). Price: {self.price_text}. "
            f"Capacity: {self.capacity_text}. Please share availability."
        )

class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="Use this for Google Drive or external links")
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-is_primary', 'sort_order', 'id']

    def __str__(self):
        return f"Image for {self.vehicle.name}"

    def save(self, *args, **kwargs):
        if self.is_primary and self.vehicle_id:
            VehicleImage.objects.filter(
                vehicle=self.vehicle, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    @staticmethod
    def _drive_image_url(url):
        if not url or "drive.google.com" not in url:
            return url

        match = re.search(r"/file/d/([a-zA-Z0-9_-]+)", url)
        if not match:
            match = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url)

        if not match:
            return url

        file_id = match.group(1)
        # Thumbnail links render reliably in <img> tags for public files.
        return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1600"

    @property
    def resolved_url(self):
        if self.image_url:
            return self._drive_image_url(self.image_url)
        if self.image:
            return self.image.url
        return ''
