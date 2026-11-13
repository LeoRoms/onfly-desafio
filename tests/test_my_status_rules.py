"""Testes adicionais: regras de status."""

from helpers import run_cli

ZERO_SUMMARY = {
    "total_reservations": 0,
    "confirmed_reservations": 0,
    "cancelled_reservations": 0,
    "no_show_reservations": 0,
    "total_room_nights": 0,
    "total_amount_brl": "0.00",
    "average_nightly_rate_brl": "0.00",
}


def test_my_status_no_show_excluded_from_month_and_hotels(tmp_path):
    """NO_SHOW e CANCELLED não entram em by_month nem em top_hotels."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "amount": "100.00"},
            {"reservation_id": "R-2", "hotel_id": "H02", "status": "NO_SHOW", "amount": "4000.00"},
            {"reservation_id": "R-3", "hotel_id": "H03", "status": "CANCELLED", "amount": "5000.00"},
        ],
    )
    assert report["by_month"] == [{"month": "2025-01", "reservations": 1, "room_nights": 1, "total_brl": "100.00"}]
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01"]


def test_my_status_only_cancelled_and_no_show(tmp_path):
    """Sem CONFIRMED: contagens preenchidas, totais zerados e média "0.00"."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "status": "CANCELLED", "amount": "500.00"},
            {"reservation_id": "R-2", "status": "NO_SHOW", "currency": "USD", "amount": "80.00"},
        ],
    )
    assert report["summary"] == {
        **ZERO_SUMMARY,
        "total_reservations": 2,
        "cancelled_reservations": 1,
        "no_show_reservations": 1,
    }
    assert report["by_month"] == []
    assert report["top_hotels"] == []


def test_my_status_empty_file(tmp_path):
    """Arquivo só com cabeçalho: tudo zerado e listas vazias."""
    report = run_cli(tmp_path, [])
    assert report["summary"] == ZERO_SUMMARY
    assert report["by_month"] == []
    assert report["top_hotels"] == []


def test_my_status_counts_add_up_to_total(tmp_path):
    """CONFIRMED + CANCELLED + NO_SHOW = total_reservations."""
    statuses = ["CONFIRMED"] * 3 + ["CANCELLED"] * 2 + ["NO_SHOW"] * 4
    rows = [{"reservation_id": f"R-{index}", "status": status} for index, status in enumerate(statuses)]
    summary = run_cli(tmp_path, rows)["summary"]
    assert (summary["confirmed_reservations"], summary["cancelled_reservations"], summary["no_show_reservations"]) == (
        3,
        2,
        4,
    )
    assert summary["total_reservations"] == 9
