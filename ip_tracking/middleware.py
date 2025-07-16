#!/usr/bin/env python3
"""
Basic ip logging middleware
"""
from ipware import get_client_ip
from datetime import datetime
import logging
from .models import RequestLog, BlockedIP
from django.http import HttpResponseForbidden


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class IpMiddleware:
    """
    middleware to log ip, timestamp and path
    """
    def __init__(self, get_response):
        """
        initialization
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Executed for each request
        """
        ip, _ = get_client_ip(request)

        timestamp = datetime.now()
        path = request.path

        request_info = {
            "client_ip": ip,
            "request_timestamp": timestamp.isoformat(),
            "request_path": path
        }

        # Log to console
        logger.info(f"Request info: {request_info}")

        # Log to database
        RequestLog.objects.create(
            ip_address=ip or "0.0.0.0",
            timestamp=timestamp,
            path=path
        )

        if BlockedIp.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden()

        return self.get_response(request)
