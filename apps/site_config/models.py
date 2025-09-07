from django.db import models

# Site Features
class SiteFeature(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    icon_class = models.CharField(max_length=100)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.title

# Social Links
class SocialLink(models.Model):
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('whatsapp', 'WhatsApp'),
    ]
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    url = models.URLField(max_length=500)
    icon_class = models.TextField(max_length=100, blank=True, null=True)  

    def __str__(self):
        return self.platform
