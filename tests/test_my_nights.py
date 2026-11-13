"""Testes adicionais: noites de quarto."""

from helpers import run_cli


def test_my_nights_across_year_boundary_with_two_rooms(tmp_path):
    """Virada de ano com 2 quartos: 30/12 -> 02/01 = 3 noites x 2 quartos."""
    report = run_cli(tmp_path, [{"checkin_date": "2024-12-30", "checkout_date": "2025-01-02", "rooms": "2"}])
    assert report["summary"]["total_room_nights"] == 6


def test_my_nights_leap_year(tmp_path):
    """Ano bissexto: 28/02/2024 -> 01/03/2024 = 2 noites."""
    report = run_cli(tmp_path, [{"checkin_date": "2024-02-28", "checkout_date": "2024-03-01"}])
    assert report["summary"]["total_room_nights"] == 2


def test_my_nights_multiply_by_rooms(tmp_path):
    """Noites de quarto = dias x quartos (4 dias x 3 quartos)."""
    report = run_cli(tmp_path, [{"checkin_date": "2025-03-01", "checkout_date": "2025-03-05", "rooms": "3"}])
    assert report["summary"]["total_room_nights"] == 12


def test_my_nights_counted_in_checkin_month(tmp_path):
    """Estadia que cruza o mês entra inteira no mês do check-in."""
    report = run_cli(tmp_path, [{"checkin_date": "2025-04-28", "checkout_date": "2025-05-03", "rooms": "2"}])
    assert report["by_month"] == [{"month": "2025-04", "reservations": 1, "room_nights": 10, "total_brl": "100.00"}]


def test_my_nights_summed_across_reservations(tmp_path):
    """Total de noites soma todas as reservas, incluindo as que cruzam o mês."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "checkin_date": "2025-01-10", "checkout_date": "2025-01-13"},
            {"reservation_id": "R-2", "checkin_date": "2025-01-30", "checkout_date": "2025-02-02", "rooms": "2"},
        ],
    )
    assert report["summary"]["total_room_nights"] == 9
