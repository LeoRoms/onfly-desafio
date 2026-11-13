"""Testes adicionais: câmbio para BRL."""

import pytest
from helpers import run_cli


@pytest.mark.parametrize(
    ("currency", "amount", "expected"),
    [
        ("BRL", "100.00", "100.00"),
        ("USD", "100.00", "542.00"),
        ("EUR", "150.00", "882.00"),
        ("EUR", "50.50", "296.94"),
    ],
)
def test_my_currency_multiplies_amount_by_rate(tmp_path, currency, amount, expected):
    """amount x rate_to_brl, nunca divisão."""
    report = run_cli(tmp_path, [{"currency": currency, "amount": amount}])
    assert report["summary"]["total_amount_brl"] == expected


def test_my_currency_keeps_four_decimal_places_until_serialization(tmp_path):
    """333.33 EUR x 5.88 = 1959.9804 -> 1959.98."""
    report = run_cli(tmp_path, [{"currency": "EUR", "amount": "333.33"}])
    assert report["summary"]["total_amount_brl"] == "1959.98"


def test_my_currency_mixed_currencies_in_same_hotel(tmp_path):
    """Moedas diferentes somam no mesmo hotel depois de convertidas."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "currency": "BRL", "amount": "1000.00"},
            {"reservation_id": "R-2", "currency": "USD", "amount": "10.00"},
            {"reservation_id": "R-3", "currency": "EUR", "amount": "10.00"},
        ],
    )
    assert report["top_hotels"][0]["total_brl"] == "1113.00"
