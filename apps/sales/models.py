from django.db import models
from django.utils.text import slugify
import re

class VehicleForSale(models.Model):
    STATUS_AVAILABLE = 'available'
    STATUS_SOLD = 'sold'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_SOLD, 'Sold'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    mileage = models.PositiveIntegerField(help_text='Mileage in km')
    fuel_type = models.CharField(max_length=50)
    transmission = models.CharField(max_length=50)
    condition = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    city = models.CharField(max_length=100)
    description = models.TextField()
    whatsapp_number = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def primary_image(self):
        return self.images.order_by('created_at', 'id').first()

    @property
    def whatsapp_message(self):
        return (
            f"Hello, I'm interested in the {self.title}. "
            f"Price: {self.price} SAR. Please share more details."
        )

class SaleVehicleImage(models.Model):
    vehicle = models.ForeignKey(VehicleForSale, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='sale_vehicles/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="Use this for Google Drive or external links")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']

    def __str__(self):
        return f"Image for {self.vehicle.title}"

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
        return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1600"

    @property
    def resolved_url(self):
        if self.image_url:
            return self._drive_image_url(self.image_url)
        if self.image:
            return self.image.url
        return ''
