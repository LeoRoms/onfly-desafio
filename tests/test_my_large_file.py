"""Testes adicionais: arquivos com mais de 200 reservas.

Nenhum teste fornecido tem mais de 200 linhas; o CLI original parava de ler na linha 200
"""

from helpers import run_cli


def test_my_large_file_reads_every_reservation(tmp_path):
    """250 reservas: todas contam."""
    rows = [{"reservation_id": f"R-{index}"} for index in range(250)]
    summary = run_cli(tmp_path, rows)["summary"]
    assert summary["total_reservations"] == 250
    assert summary["confirmed_reservations"] == 250
    assert summary["total_room_nights"] == 250
    assert summary["total_amount_brl"] == "25000.00"


def test_my_large_file_reservations_after_line_200_reach_ranking(tmp_path):
    """Um hotel que só aparece depois da linha 200 entra no ranking e nas contagens."""
    rows = [{"reservation_id": f"R-{index}", "hotel_id": "H01", "amount": "1.00"} for index in range(205)]
    rows += [
        {"reservation_id": "R-LATE-1", "hotel_id": "H99", "hotel_name": "Hotel Tardio", "amount": "999.00"},
        {"reservation_id": "R-LATE-2", "status": "NO_SHOW"},
        {"reservation_id": "R-LATE-3", "status": "CANCELLED"},
    ]
    report = run_cli(tmp_path, rows)
    assert report["summary"]["total_reservations"] == 208
    assert report["summary"]["no_show_reservations"] == 1
    assert report["summary"]["cancelled_reservations"] == 1
    assert report["top_hotels"][0] == {
        "hotel_id": "H99",
        "hotel_name": "Hotel Tardio",
        "room_nights": 1,
        "total_brl": "999.00",
    }
