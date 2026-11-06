"""Load all template modules so they self-register.

Call ``load_all()`` once at app startup (idempotent).
"""

from __future__ import annotations

_loaded = False


def load_all() -> int:
    """Import template modules; return count of registered templates."""
    global _loaded
    if _loaded:
        from app.template_engine import list_templates
        return len(list_templates())

    from app.templates import arithmetic, geometry, ratio, word_problems  # noqa: F401

    from app.template_engine import list_templates
    _loaded = True
    return len(list_templates())
