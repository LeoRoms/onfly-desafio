"""Política de status das reservas."""

from __future__ import annotations


def is_billable(status: str) -> bool:
    """Indica se a reserva entra nos totais financeiros e de noites."""
    # Problema: consideramos "NO_SHOW" 
    # Devemos considerar, apenas, "CONFIRMED"
    # return status != "CANCELLED"
    return status == "CONFIRMED"
