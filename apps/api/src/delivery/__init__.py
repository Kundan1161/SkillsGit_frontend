"""Delivery — license-gated, watermarked skills.md downloads.

See ``prompts/marketplace/04-licensing-and-delivery.md``.
"""

from src.delivery.service import (
    DeliveryService,
    entitled_version,
    get_delivery_service,
)

__all__ = ["DeliveryService", "entitled_version", "get_delivery_service"]
