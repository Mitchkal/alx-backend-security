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

        if ip == "127.0.0.1":
            return self.get_response(request)

        timestamp = datetime.now()
        path = request.path
        country_name = request.geolocation.country_name
        city_name = request.geolocation.city_name
        latitude = request.gelolocation.latitude
        longitude = request.geolocation.longitude

        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden()

        # prepare request info
        request_info = {
            "client_ip": ip,
            "request_timestamp": timestamp.isoformat(),
            "request_path": path,
            "city": city_name,
            "country": country_name,
            "longitude": longitude,
            "latitude": latitude,
        }

        # Log to console
        logger.info(f"Request info: {request_info}")

        # Log to database
        RequestLog.objects.create(
            ip_address=ip or "0.0.0.0",
            timestamp=timestamp,
            path=path,
            country=country_name,
            city=city_name,
        )
        return self.get_response(request)
