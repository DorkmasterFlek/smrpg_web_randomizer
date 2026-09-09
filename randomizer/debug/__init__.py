"""Debug configuration loader and utilities."""
from django.conf import settings
from django.utils.autoreload import autoreload_started

import yaml
from pathlib import Path
from typing import Any

# Register config.yml with Django's autoreloader so changes trigger a reload
_config_path = Path(__file__).parent / "config.yml"


def _register_config_watcher():
    """Register config.yml with Django's autoreloader."""

    def _watch_config_file(sender, **kwargs):
        sender.extra_files.add(_config_path)

    autoreload_started.connect(_watch_config_file)


if settings.DEBUG:
    _register_config_watcher()


def load_debug_config() -> dict[str, Any]:
    """Load debug config from config.yml."""
    if not _config_path.exists():
        return {}
    with open(_config_path) as f:
        return yaml.safe_load(f) or {}


def get_item_class(name: str):
    """Get item class by exact name from randomizer.data.items.

    Args:
        name: Exact class name (e.g., 'CastleKey1Item')

    Returns:
        The item class, or None if not found.
    """
    from randomizer.data import items

    cls = getattr(items, name, None)
    if cls is None:
        print(f"Warning: Item class '{name}' not found")
    return cls


def get_prize_class(name: str):
    """Get prize class by exact name from randomizer.logic.progression.prizes or randomizer.types.prize.

    Args:
        name: Exact class name (e.g., 'CastleKey1Prize', 'FPFlowerPrize')

    Returns:
        The prize class, or None if not found.
    """
    from randomizer.logic.progression import prizes
    from randomizer.types import prize as prize_types

    cls = getattr(prizes, name, None)
    if cls is None:
        # Also check types.prize for classes like FPFlowerPrize
        cls = getattr(prize_types, name, None)
    if cls is None:
        print(f"Warning: Prize class '{name}' not found")
    return cls


def get_location_class(name: str):
    """Get location class by exact name from randomizer.logic.progression.prizelocations.

    Args:
        name: Exact class name (e.g., 'MushroomWay1LowerChest')

    Returns:
        The location class, or None if not found.
    """
    from randomizer.logic.progression import prizelocations

    cls = getattr(prizelocations, name, None)
    if cls is None:
        print(f"Warning: Location class '{name}' not found")
    return cls
