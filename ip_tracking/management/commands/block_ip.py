#!/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_ipv46_address
from django.core.exceptions import ValidationError
from ip_tracking.models import BlockedIP


class Command(BaseCommand):
    """
    Adds an ip to the BlockedIP model
    """

    help = "adds ip to Blocked Ip model"

    def add_arguments(self, parser):
        parser.add_argument("ip_address", type=str, help="IP address to block")

    def handle(self, *args, **options):
        ip = options["ip_address"]
        try:
            validate_ipv46_address(ip)
        except ValidationError:
            raise CommandError(f"'{ip}' is not a valid ip address")

        try:
            blocked, created = BlockedIP.objects.get_or_create(ip_address=ip)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully blocked ip address{ip}")
                )
            else:
                self.stdout.write(self.style.WARNING(f"Ip already blocked: {ip}"))

        except Exception as e:
            raise CommandError(f"Error blocking ip {ip}: {str(e)}")
