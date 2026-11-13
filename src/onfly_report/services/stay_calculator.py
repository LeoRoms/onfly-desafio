"""Cálculo de noites ocupadas."""

from __future__ import annotations

from datetime import date


def calculate_room_nights(checkin: date, checkout: date, rooms: int) -> int:
    """Calcula noites de quarto: diferença de dias (não inclusiva) vezes quartos."""
    # return (checkout.day - checkin.day) * rooms # antigo retorno 
    # problema: podemos ter algo como 30/1 -> 2/2 : 2 - 30 = -28 -> erro!!!
    return (checkout - checkin).days * rooms 
    # esse novo retorno calcula a diferença de datas e depois extrai os dias -> correto! 
