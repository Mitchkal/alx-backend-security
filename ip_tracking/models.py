from django.db import models


class RequestLog(models.Model):
    """
    Requestlog model
    """
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField()
    path = models.CharField(max_length=2048)
    country = models.ForeignKey('cities_light.Country', on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey('cities_light.City', on_delete=models.SET_NULL, null=True, blank=True)


class BlockedIP(models.Model):
    """
    Model for blocked ips
    """
    ip_address = models.GenericIPAddressField()
