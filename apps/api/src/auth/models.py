"""Auth-side ORM models.

The User and ApiToken tables live in ``users/models.py`` (the owning module
per the table-to-module mapping in the prompt). This file is intentionally
empty — kept for symmetry so feature modules can ``from src.auth.models
import …`` if we ever introduce auth-specific tables (e.g. WebAuthn
credentials in a future phase).
"""

from __future__ import annotations

# Re-export the user models for ergonomic access from the auth package.
from src.users.models import ApiToken, User, UserRole  # noqa: F401

__all__ = ["ApiToken", "User", "UserRole"]
