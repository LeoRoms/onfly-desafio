"""Testes adicionais: ranking de hotéis."""

from helpers import run_cli

THREE_HOTELS = [
    {"reservation_id": "R-1", "hotel_id": "H01", "amount": "100.00"},
    {"reservation_id": "R-2", "hotel_id": "H02", "amount": "200.00"},
    {"reservation_id": "R-3", "hotel_id": "H03", "amount": "300.00"},
]


def test_my_top_hotels_tie_broken_by_hotel_id_ascending(tmp_path):
    """Empate de valor: hotel_id ascendente, independente da ordem no arquivo.

    Um sorted(..., reverse=True) inverteria também o desempate (H09, H05, H02).
    """
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H09", "amount": "500.00"},
            {"reservation_id": "R-2", "hotel_id": "H02", "amount": "500.00"},
            {"reservation_id": "R-3", "hotel_id": "H05", "amount": "500.00"},
        ],
    )
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H02", "H05", "H09"]


def test_my_top_hotels_tie_at_cutoff(tmp_path):
    """Empate exatamente no corte do --top: entra o menor hotel_id."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "amount": "900.00"},
            {"reservation_id": "R-2", "hotel_id": "H09", "amount": "500.00"},
            {"reservation_id": "R-3", "hotel_id": "H08", "amount": "500.00"},
        ],
        top=2,
    )
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01", "H08"]


def test_my_top_hotels_top_one(tmp_path):
    """--top 1 devolve só o maior."""
    report = run_cli(tmp_path, THREE_HOTELS, top=1)
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H03"]


def test_my_top_hotels_top_larger_than_hotel_count(tmp_path):
    """--top maior que o número de hotéis devolve todos, em ordem."""
    report = run_cli(tmp_path, THREE_HOTELS, top=50)
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H03", "H02", "H01"]


def test_my_top_hotels_aggregates_reservations_of_same_hotel(tmp_path):
    """Várias reservas do mesmo hotel somam noites e valor."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "amount": "300.00", "rooms": "2"},
            {"reservation_id": "R-2", "hotel_id": "H01", "amount": "400.00"},
            {"reservation_id": "R-3", "hotel_id": "H02", "amount": "600.00"},
        ],
    )
    assert report["top_hotels"][0] == {
        "hotel_id": "H01",
        "hotel_name": "Hotel Teste",
        "room_nights": 3,
        "total_brl": "700.00",
    }


def test_my_top_hotels_name_with_comma_and_accents(tmp_path):
    """Nome com vírgula e acentos é preservado no JSON."""
    report = run_cli(tmp_path, [{"hotel_id": "H10", "hotel_name": "Hotel Madrid, Gran Vía — São João"}])
    assert report["top_hotels"][0]["hotel_name"] == "Hotel Madrid, Gran Vía — São João"
