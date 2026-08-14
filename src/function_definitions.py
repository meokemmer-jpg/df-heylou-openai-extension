"""HeyLou function definitions for the OpenAI extension.

The canonical definitions are provider-neutral JSON Schema objects.  The payload
builder renders those definitions into the selected function-calling wire format,
so the OpenAI extension can explicitly request an OpenAI-shaped tool declaration
and prove that a Gemini countercase serializes differently.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal

ToolProvider = Literal["openai", "gemini"]


HEYLOU_FUNCTION_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "search_hotels",
        "description": (
            "Search HeyLou Travel-Knowledge-Graph for hotels matching location, dates, and preferences. "
            "Read-only, idempotent. Returns list of hotels with availability + base-rates."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City or region (e.g. 'Hildesheim', 'Munich', 'Cape Coral FL').",
                },
                "dates": {
                    "type": "object",
                    "properties": {
                        "check_in": {"type": "string", "description": "ISO date YYYY-MM-DD"},
                        "check_out": {"type": "string", "description": "ISO date YYYY-MM-DD"},
                    },
                    "required": ["check_in", "check_out"],
                },
                "preferences": {
                    "type": "object",
                    "description": "Optional filters (room_type, max_price_eur, amenities).",
                    "properties": {
                        "room_type": {"type": "string"},
                        "max_price_eur": {"type": "number"},
                        "amenities": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "required": ["location", "dates"],
        },
    },
    {
        "name": "get_rates",
        "description": (
            "Fetch current rates from PMS/RMS backend (MEWS/Opera/Protel) for a hotel + date-range. "
            "Read-only. Returns per-room-type rates with availability."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {"type": "string", "description": "HeyLou hotel-ID (e.g. 'hildesheim')."},
                "date_range": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "string", "description": "ISO date"},
                        "end": {"type": "string", "description": "ISO date"},
                    },
                    "required": ["start", "end"],
                },
            },
            "required": ["hotel_id", "date_range"],
        },
    },
    {
        "name": "compare_otas",
        "description": (
            "Compare OTA-prices (Booking.com / Expedia / HRS) for a hotel + dates against Direct-Booking. "
            "Read-only. Returns spread + commission-delta."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {"type": "string"},
                "dates": {
                    "type": "object",
                    "properties": {
                        "check_in": {"type": "string"},
                        "check_out": {"type": "string"},
                    },
                    "required": ["check_in", "check_out"],
                },
            },
            "required": ["hotel_id", "dates"],
        },
    },
    {
        "name": "book_direct",
        "description": (
            "Direct-Booking via HeyLou (commission-free). K_0-RELEVANT - requires PHRONESIS_TICKET in Real-Mode. "
            "Returns confirmed booking with booking_id."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {"type": "string"},
                "room_type": {"type": "string"},
                "guest": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                    },
                    "required": ["email"],
                },
                "dates": {
                    "type": "object",
                    "properties": {
                        "check_in": {"type": "string"},
                        "check_out": {"type": "string"},
                    },
                    "required": ["check_in", "check_out"],
                },
            },
            "required": ["hotel_id", "room_type", "guest", "dates"],
        },
    },
    {
        "name": "optimize_revenue",
        "description": (
            "Run Revenue-Optimizer for a hotel (Hamilton/Lagrange/KKT pricing optimization). "
            "Returns recommended rate-changes per room-type."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {"type": "string"},
            },
            "required": ["hotel_id"],
        },
    },
]


def _normalize_provider(provider: str) -> ToolProvider:
    normalized = provider.strip().lower()
    if normalized not in {"openai", "gemini"}:
        raise ValueError(f"unsupported tool provider: {provider!r}")
    return normalized  # type: ignore[return-value]


def build_tool_payload(provider: str = "gemini") -> dict[str, Any]:
    """Build a function-calling payload for the requested provider.

    OpenAI expects tools as a list of typed function declarations:
    {"tools": [{"type": "function", "function": {...}}]}.

    Gemini accepts the same canonical definitions below "function_declarations".
    The provider branch is intentionally explicit so tests can prove that an
    adversarial opposite provider produces a different wire shape.  The default
    stays on the legacy Gemini shape for compatibility with existing callers.
    """
    normalized = _normalize_provider(provider)
    definitions = deepcopy(HEYLOU_FUNCTION_DEFINITIONS)

    if normalized == "openai":
        return {
            "tools": [
                {
                    "type": "function",
                    "function": definition,
                }
                for definition in definitions
            ]
        }

    return {"function_declarations": definitions}


def get_function_names() -> list[str]:
    """Return the configured HeyLou function names in declaration order."""
    return [fd["name"] for fd in HEYLOU_FUNCTION_DEFINITIONS]


def get_function_schema(name: str) -> dict[str, Any] | None:
    """Look up a function schema by name."""
    for fd in HEYLOU_FUNCTION_DEFINITIONS:
        if fd["name"] == name:
            return deepcopy(fd)
    return None


def is_k0_relevant(name: str) -> bool:
    """K_0 filter: direct booking is the only write/action gate."""
    return name == "book_direct"
