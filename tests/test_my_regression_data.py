"""Testes adicionais: regressão sobre os arquivos de data/.

Valores esperados conferidos por três cálculos independentes 
(CLI, gabarito em Decimal e frações exatas).
"""

from my_helpers import DATA_DIR, run_cli_on_file


def test_my_regression_validation_sample_matches_readme(tmp_path):
    """data/exemplo-validacao.csv bate com a tabela "Amostra de validação" do README."""
    report = run_cli_on_file(tmp_path, DATA_DIR / "exemplo-validacao.csv")
    assert report["summary"] == {
        "total_reservations": 12,
        "confirmed_reservations": 9,
        "cancelled_reservations": 2,
        "no_show_reservations": 1,
        "total_room_nights": 28,
        "total_amount_brl": "7566.00",
        "average_nightly_rate_brl": "270.21",
    }
    assert report["by_month"] == [
        {"month": "2025-01", "reservations": 8, "room_nights": 25, "total_brl": "6684.00"},
        {"month": "2025-02", "reservations": 1, "room_nights": 3, "total_brl": "882.00"},
    ]
    assert report["top_hotels"] == [
        {"hotel_id": "H01", "hotel_name": "Hotel Aurora Paulista", "room_nights": 3, "total_brl": "1200.00"},
        {"hotel_id": "H02", "hotel_name": "Hotel Mirante", "room_nights": 2, "total_brl": "1084.00"},
        {"hotel_id": "H12", "hotel_name": "Hotel Miami Beach", "room_nights": 1, "total_brl": "1000.00"},
        {"hotel_id": "H10", "hotel_name": "Hotel Madrid, Gran Vía", "room_nights": 4, "total_brl": "900.00"},
        {"hotel_id": "H09", "hotel_name": "Hotel Lisboa, Centro", "room_nights": 3, "total_brl": "882.00"},
    ]


def test_my_regression_full_dataset(tmp_path):
    """data/reservas_hoteis.csv (300 reservas): relatório completo."""
    report = run_cli_on_file(tmp_path, DATA_DIR / "reservas_hoteis.csv")
    assert report["report_version"] == "1.0"
    assert report["summary"] == {
        "total_reservations": 300,
        "confirmed_reservations": 235,
        "cancelled_reservations": 31,
        "no_show_reservations": 34,
        "total_room_nights": 1347,
        "total_amount_brl": "396170.00",  # soma exata 396169.9994 (arredondar antes daria 396169.99)
        "average_nightly_rate_brl": "294.11",
    }
    assert report["by_month"] == [
        {"month": "2024-12", "reservations": 35, "room_nights": 174, "total_brl": "61335.80"},
        {"month": "2025-01", "reservations": 37, "room_nights": 235, "total_brl": "64662.89"},
        {"month": "2025-02", "reservations": 26, "room_nights": 138, "total_brl": "45991.09"},
        {"month": "2025-03", "reservations": 39, "room_nights": 215, "total_brl": "65984.99"},
        {"month": "2025-04", "reservations": 21, "room_nights": 146, "total_brl": "31335.97"},
        {"month": "2025-05", "reservations": 39, "room_nights": 196, "total_brl": "63507.98"},
        {"month": "2025-06", "reservations": 38, "room_nights": 243, "total_brl": "63351.29"},
    ]
    assert report["top_hotels"] == [
        {"hotel_id": "H06", "hotel_name": "Hotel Salvador Centro", "room_nights": 160, "total_brl": "45165.46"},
        {"hotel_id": "H10", "hotel_name": "Hotel Madrid, Gran Vía", "room_nights": 120, "total_brl": "45041.69"},
        {"hotel_id": "H12", "hotel_name": "Hotel Miami Beach", "room_nights": 106, "total_brl": "41647.69"},
        {"hotel_id": "H07", "hotel_name": "Hotel Brasília Tower", "room_nights": 148, "total_brl": "39920.52"},
        {"hotel_id": "H11", "hotel_name": "Hotel Buenos Aires", "room_nights": 102, "total_brl": "37455.69"},
    ]


def test_my_regression_full_dataset_internal_consistency(tmp_path):
    """Somas de by_month batem com o summary; contagens por status somam o total."""
    report = run_cli_on_file(tmp_path, DATA_DIR / "reservas_hoteis.csv", top=50)
    summary = report["summary"]
    assert sum(month["reservations"] for month in report["by_month"]) == summary["confirmed_reservations"]
    assert sum(month["room_nights"] for month in report["by_month"]) == summary["total_room_nights"]
    assert sum(hotel["room_nights"] for hotel in report["top_hotels"]) == summary["total_room_nights"]
    assert (
        summary["confirmed_reservations"] + summary["cancelled_reservations"] + summary["no_show_reservations"]
        == summary["total_reservations"]
    )
    assert len(report["top_hotels"]) == 12
