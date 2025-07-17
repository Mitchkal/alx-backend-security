#!/usr/bin/env python3
"""
Basic ip logging middleware
"""
from ipware import get_client_ip
from datetime import datetime
import logging
from .models import RequestLog, BlockedIP
from django.http import HttpResponseForbidden
from ipgeolocation import IPGeolocation
from django.core.cache import cache


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


geo_locator = IPGeolocation()


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
        country_name = request.geolocation.country_name
        city_name = request.geolocation.city_name
        latitude = request.gelolocation.latitude
        longitude = request.geolocation.longitude

        geo_data = {
            "country": country_name,
            "city": city_name,
            "latitude": latitude,
            "longitude": longitude,
        }

        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden()

        geo_cache_key = f"geo: {ip}"
        geo_data = cache.get(geo_cache_key)

        if not geo_data:
            try:
                geo_data = geo_locator.get_location(ip)
                cache.set(geo_cache_key, geo_data, timeout=86400)
            except Exception as e:
                logger.warning(f"Geo lookup failed ffor ip {ip}: {e}")
                geo_data = {}
        # prepare request info
        country = geo_data.get("country_name")
        city = geo_data.get("city_name")
        latitude = geo_data.get("latitude")
        longitude = geo_data.get("longitude")

        request_info = {
            "client_ip": ip,
            "request_timestamp": timestamp.isoformat(),
            "request_path": path,
            "city": city,
            "country": country,
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
            country=country,
            city=city,
        )

        return self.get_response(request)
