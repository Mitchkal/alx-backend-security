from django.db import models


class RequestLog(models.Model):
    """
    Requestlog model
    """
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField()
    path = models.CharField(max_length=2048)
