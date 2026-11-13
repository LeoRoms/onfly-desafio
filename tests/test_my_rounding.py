"""Testes adicionais: arredondamento half-up só na serialização.

Os valores esperados foram calculados com Decimal. Os comentários mostram o que dariam as
variantes erradas (half-even, float, arredondamento antecipado).
"""

import pytest
from helpers import run_cli


def test_my_rounding_half_up_single_value(tmp_path):
    """0.75 USD x 5.42 = 4.065 -> 4.07 (half-even e float dariam 4.06)."""
    report = run_cli(tmp_path, [{"currency": "USD", "amount": "0.75"}])
    assert report["summary"]["total_amount_brl"] == "4.07"
    assert report["by_month"][0]["total_brl"] == "4.07"
    assert report["top_hotels"][0]["total_brl"] == "4.07"


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        ("1.75", "9.49"),  # 9.485  (half-even: 9.48)
        ("2.75", "14.91"),  # 14.905 (half-even: 14.90)
        ("0.25", "1.36"),  # 1.355
        ("0.01", "0.05"),  # 0.0542
    ],
)
def test_my_rounding_half_up_usd_values(tmp_path, amount, expected):
    """Casos em que a terceira casa decide o arredondamento."""
    report = run_cli(tmp_path, [{"currency": "USD", "amount": amount}])
    assert report["summary"]["total_amount_brl"] == expected


def test_my_rounding_only_after_summing(tmp_path):
    """3 x 4.065 = 12.195 -> 12.20 (arredondar cada linha antes daria 12.21)."""
    rows = [{"reservation_id": f"R-{index}", "currency": "USD", "amount": "0.75"} for index in range(3)]
    report = run_cli(tmp_path, rows)
    assert report["summary"]["total_amount_brl"] == "12.20"
    assert report["by_month"][0]["total_brl"] == "12.20"
    assert report["top_hotels"][0]["total_brl"] == "12.20"


def test_my_rounding_average_uses_exact_total(tmp_path):
    """0.3252 / 2 noites = 0.1626 -> 0.16 (com o total já arredondado: 0.33 / 2 = 0.165 -> 0.17)."""
    report = run_cli(
        tmp_path,
        [{"currency": "USD", "amount": "0.06", "checkin_date": "2025-01-10", "checkout_date": "2025-01-12"}],
    )
    assert report["summary"]["total_amount_brl"] == "0.33"
    assert report["summary"]["average_nightly_rate_brl"] == "0.16"


def test_my_rounding_average_half_up(tmp_path):
    """10.01 / 2 noites = 5.005 -> 5.01 (half-even e float dariam 5.00)."""
    report = run_cli(tmp_path, [{"amount": "10.01", "checkin_date": "2025-01-10", "checkout_date": "2025-01-12"}])
    assert report["summary"]["average_nightly_rate_brl"] == "5.01"


@pytest.mark.parametrize(
    ("amount", "expected"),
    [("100", "100.00"), ("0.10", "0.10"), ("0.00", "0.00"), ("1234567.80", "1234567.80")],
)
def test_my_rounding_money_always_two_decimals_without_separator(tmp_path, amount, expected):
    """Dinheiro como string com exatamente 2 casas e sem separador de milhar."""
    report = run_cli(tmp_path, [{"amount": amount}])
    assert report["summary"]["total_amount_brl"] == expected


def test_my_rounding_complete_sample(tmp_path):
    """Base de arredondamento completa: soma exata 25.745 -> 25.75 (antecipado daria 25.77)."""
    rows = [
        {
            "reservation_id": "A01",
            "hotel_id": "H01",
            "currency": "USD",
            "amount": "0.75",
            "checkin_date": "2025-02-10",
            "checkout_date": "2025-02-11",
        },
        {"reservation_id": "A02", "hotel_id": "H02", "currency": "USD", "amount": "0.75"},
        {"reservation_id": "A03", "hotel_id": "H02", "currency": "USD", "amount": "0.75"},
        {"reservation_id": "A04", "hotel_id": "H02", "currency": "USD", "amount": "0.75"},
        {"reservation_id": "A05", "hotel_id": "H03", "currency": "USD", "amount": "1.75"},
        {"reservation_id": "A06", "hotel_id": "H04", "currency": "USD", "amount": "0.75", "status": "CANCELLED"},
    ]
    report = run_cli(tmp_path, rows)
    assert report["summary"]["total_amount_brl"] == "25.75"
    assert report["summary"]["average_nightly_rate_brl"] == "5.15"
    assert [(month["month"], month["total_brl"]) for month in report["by_month"]] == [
        ("2025-01", "21.68"),
        ("2025-02", "4.07"),
    ]
    assert [(hotel["hotel_id"], hotel["total_brl"]) for hotel in report["top_hotels"]] == [
        ("H02", "12.20"),
        ("H03", "9.49"),
        ("H01", "4.07"),
    ]
