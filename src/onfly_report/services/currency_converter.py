"""Conversão de valores para BRL."""

from __future__ import annotations

from decimal import Decimal


def convert_to_brl(amount: Decimal, currency: str, rates: dict[str, Decimal]) -> Decimal:
    """Converte um valor na moeda informada para BRL usando a taxa da tabela."""
    rate = rates[currency]
    # PROBLEMA: cálculo atual divide quantidade por taxa. Deveria ser quantidade * taxa
    # além disso, o 'float()' também causava erro
    # return Decimal(str(float(amount) / float(rate))) 
    return amount * rate

