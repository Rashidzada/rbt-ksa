from django.db import models

class SiteSetting(models.Model):
    support_whatsapp_number = models.CharField(max_length=20, help_text="Global support number")
    
    def __str__(self):
        return "Site Settings"

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"
