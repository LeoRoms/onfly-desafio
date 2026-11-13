"""Testes adicionais: formato do relatório, stdout e saída."""

import json
import re
from datetime import datetime, timedelta, timezone

from helpers import run_cli
from my_helpers import DATA_DIR, run_cli_process

SUMMARY_KEYS = [
    "total_reservations",
    "confirmed_reservations",
    "cancelled_reservations",
    "no_show_reservations",
    "total_room_nights",
    "total_amount_brl",
    "average_nightly_rate_brl",
]
MONEY = re.compile(r"^\d+\.\d{2}$")
SAMPLE_ROWS = [
    {"reservation_id": "R-1", "hotel_id": "H01", "currency": "USD", "amount": "0.75"},
    {"reservation_id": "R-2", "hotel_id": "H02", "checkin_date": "2025-02-01", "checkout_date": "2025-02-03"},
    {"reservation_id": "R-3", "status": "CANCELLED"},
]


def test_my_format_exact_keys_and_order(tmp_path):
    """Chaves exatamente como no contrato, na mesma ordem e sem extras."""
    report = run_cli(tmp_path, SAMPLE_ROWS)
    assert list(report) == ["report_version", "generated_at", "summary", "by_month", "top_hotels"]
    assert list(report["summary"]) == SUMMARY_KEYS
    assert all(list(month) == ["month", "reservations", "room_nights", "total_brl"] for month in report["by_month"])
    assert all(list(hotel) == ["hotel_id", "hotel_name", "room_nights", "total_brl"] for hotel in report["top_hotels"])


def test_my_format_field_types(tmp_path):
    """Contagens e noites são int; dinheiro é string com 2 casas; mês é YYYY-MM."""
    report = run_cli(tmp_path, SAMPLE_ROWS)
    assert report["report_version"] == "1.0"
    for key in SUMMARY_KEYS:
        value = report["summary"][key]
        if key.endswith("_brl"):
            assert isinstance(value, str) and MONEY.match(value), (key, value)
        else:
            assert type(value) is int, (key, value)
    for month in report["by_month"]:
        assert re.match(r"^\d{4}-\d{2}$", month["month"])
        assert type(month["reservations"]) is int and type(month["room_nights"]) is int
        assert MONEY.match(month["total_brl"])
    for hotel in report["top_hotels"]:
        assert type(hotel["room_nights"]) is int and MONEY.match(hotel["total_brl"])


def test_my_format_generated_at_fixed_offset(tmp_path):
    """generated_at em ISO 8601, com segundos, offset fixo -03:00 e perto do horário atual."""
    value = run_cli(tmp_path, SAMPLE_ROWS)["generated_at"]
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-03:00$", value), value
    parsed = datetime.fromisoformat(value)
    assert parsed.utcoffset() == timedelta(hours=-3)
    assert abs(datetime.now(timezone.utc) - parsed) < timedelta(minutes=5)


def test_my_format_by_month_sorted_ascending(tmp_path):
    """by_month em ordem crescente de mês, mesmo com o arquivo fora de ordem."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "checkin_date": "2025-03-01", "checkout_date": "2025-03-02"},
            {"reservation_id": "R-2", "checkin_date": "2024-12-30", "checkout_date": "2025-01-02"},
            {"reservation_id": "R-3", "checkin_date": "2025-01-15", "checkout_date": "2025-01-16"},
        ],
    )
    assert [month["month"] for month in report["by_month"]] == ["2024-12", "2025-01", "2025-03"]


def test_my_format_stdout_summarizes_report(tmp_path):
    """A linha do stdout repete os valores do summary."""
    output = tmp_path / "report.json"
    process = run_cli_process(tmp_path, SAMPLE_ROWS, output_path=output)
    assert process.returncode == 0, process.stderr
    summary = json.loads(output.read_text(encoding="utf-8"))["summary"]
    assert process.stdout.strip() == (
        f"Reservas: {summary['total_reservations']} | Confirmadas: {summary['confirmed_reservations']} | "
        f"Noites: {summary['total_room_nights']} | Total BRL: {summary['total_amount_brl']}"
    )


def test_my_format_output_creates_directories(tmp_path):
    """--output em pastas inexistentes: o CLI cria o caminho."""
    output = tmp_path / "a" / "b" / "c" / "report.json"
    process = run_cli_process(tmp_path, SAMPLE_ROWS, output_path=output)
    assert process.returncode == 0, process.stderr
    assert output.is_file()


def test_my_format_default_output_and_top(tmp_path):
    """Sem --output e sem --top: grava output/report.json (relativo ao cwd) com até 5 hotéis."""
    rows = [{"reservation_id": f"R-{index}", "hotel_id": f"H{index:02d}"} for index in range(1, 8)]
    process = run_cli_process(tmp_path, rows, args=[], cwd=tmp_path)
    assert process.returncode == 0, process.stderr
    report = json.loads((tmp_path / "output" / "report.json").read_text(encoding="utf-8"))
    assert len(report["top_hotels"]) == 5


def test_my_format_works_from_other_directory(tmp_path):
    """O CLI não depende do diretório atual para ler os arquivos informados."""
    output = tmp_path / "report.json"
    process = run_cli_process(
        tmp_path,
        input_path=DATA_DIR / "exemplo-validacao.csv",
        rates_path=DATA_DIR / "taxas_cambio.csv",
        output_path=output,
        cwd=tmp_path,
    )
    assert process.returncode == 0, process.stderr
    assert json.loads(output.read_text(encoding="utf-8"))["summary"]["total_amount_brl"] == "7566.00"
