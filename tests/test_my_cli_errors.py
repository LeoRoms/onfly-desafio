"""Testes adicionais: argumentos e entradas inválidas que o CLI já trata.

Contrato: 0 sucesso, 2 entrada/argumento inválido, 1 erro inesperado.
"""

import pytest
from helpers import COLUMNS
from my_helpers import DATA_DIR, assert_invalid_input, run_cli_process, run_cli_raw, write_rows

RATES_HEADER = "currency,rate_to_brl\n"


@pytest.mark.parametrize("top", ["0", "-1", "abc", "1.5"])
def test_my_cli_invalid_top(tmp_path, top):
    """--top precisa ser inteiro >= 1."""
    output = tmp_path / "report.json"
    process = run_cli_process(tmp_path, [{}], args=["--output", str(output), "--top", top])
    assert_invalid_input(process, output)


def test_my_cli_unknown_argument(tmp_path):
    """Argumento desconhecido é argumento inválido."""
    process = run_cli_process(tmp_path, [{}], args=["--output", str(tmp_path / "r.json"), "--verbose"])
    assert_invalid_input(process)


@pytest.mark.parametrize(
    "args",
    [
        ["--rates", str(DATA_DIR / "taxas_cambio.csv")],
        ["--input", str(DATA_DIR / "exemplo-validacao.csv")],
        [],
    ],
    ids=["sem_input", "sem_rates", "sem_argumentos"],
)
def test_my_cli_missing_required_argument(args):
    """--input e --rates são obrigatórios."""
    assert_invalid_input(run_cli_raw(args))


def test_my_cli_input_not_found(tmp_path):
    """Arquivo de reservas inexistente."""
    output = tmp_path / "report.json"
    process = run_cli_process(tmp_path, input_path=tmp_path / "nao_existe.csv", output_path=output)
    assert_invalid_input(process, output)


def test_my_cli_rates_not_found(tmp_path):
    """Tabela de câmbio inexistente."""
    output = tmp_path / "report.json"
    process = run_cli_process(tmp_path, [{}], rates_path=tmp_path / "nao_existe.csv", output_path=output)
    assert_invalid_input(process, output)


@pytest.mark.parametrize(
    "content",
    [
        b"",
        (";".join(COLUMNS) + "\n").encode(),
        (",".join(COLUMNS).upper() + "\n").encode(),
        (",".join(COLUMNS[:-1]) + "\n").encode(),
    ],
    ids=["arquivo_vazio", "delimitador_ponto_e_virgula", "cabecalho_maiusculo", "coluna_faltando"],
)
def test_my_cli_invalid_header(tmp_path, content):
    """Cabeçalho ausente ou diferente do esperado."""
    output = tmp_path / "report.json"
    process = run_cli_process(tmp_path, input_bytes=content, output_path=output)
    assert_invalid_input(process, output)


def test_my_cli_row_with_missing_columns(tmp_path):
    """Linha com menos colunas que o cabeçalho."""
    output = tmp_path / "report.json"
    content = (",".join(COLUMNS) + "\nR-9,Pessoa,EMP-001,H01\n").encode()
    process = run_cli_process(tmp_path, input_bytes=content, output_path=output)
    assert_invalid_input(process, output)


@pytest.mark.parametrize(
    "row",
    [
        {"checkin_date": "10/01/2025"},
        {"checkout_date": "2025-02-30"},
        {"checkin_date": "2025-01-10T12:00:00"},
        {"checkin_date": ""},
        {"amount": "cem reais"},
        {"amount": "1.234,56"},
        {"amount": "1,234.56"},
        {"amount": "R$ 100,00"},
        {"amount": ""},
        {"rooms": "dois"},
        {"rooms": "1.0"},
        {"rooms": ""},
    ],
    ids=lambda row: "-".join(f"{key}={value!r}" for key, value in row.items()),
)
def test_my_cli_invalid_field_value(tmp_path, row):
    """Datas fora de YYYY-MM-DD, valores e quartos inválidos."""
    output = tmp_path / "report.json"
    process = run_cli_process(tmp_path, [row], output_path=output)
    assert_invalid_input(process, output)


def test_my_cli_invalid_row_even_if_cancelled(tmp_path):
    """Linha inválida derruba o arquivo mesmo sendo CANCELLED (falha de formato não é descartada)."""
    output = tmp_path / "report.json"
    process = run_cli_process(
        tmp_path,
        [{"reservation_id": "R-1"}, {"reservation_id": "R-2", "status": "CANCELLED", "amount": ""}],
        output_path=output,
    )
    assert_invalid_input(process, output)


@pytest.mark.parametrize(
    "rates_text",
    [
        RATES_HEADER,
        RATES_HEADER + "BRL,-1\n",
        RATES_HEADER + "BRL,0\n",
        RATES_HEADER + "BRL,-Infinity\n",
        RATES_HEADER + "BRL,abc\n",
        RATES_HEADER + 'BRL,"1,0"\n',
        RATES_HEADER + "BRL,\n",
        RATES_HEADER + ",1.0\n",
        "moeda,taxa\nBRL,1\n",
    ],
    ids=[
        "vazia",
        "negativa",
        "zero",
        "menos_infinito",
        "texto",
        "virgula_decimal",
        "taxa_vazia",
        "moeda_vazia",
        "sem_colunas",
    ],
)
def test_my_cli_invalid_rates_table(tmp_path, rates_text):
    """Tabela de câmbio vazia, com taxa não positiva, inválida ou sem as colunas."""
    output = tmp_path / "report.json"
    process = run_cli_process(tmp_path, [{}], rates_text=rates_text, output_path=output)
    assert_invalid_input(process, output)


def test_my_cli_output_is_directory(tmp_path):
    """Falha ao gravar o relatório: exit 1 (erro inesperado) e nada no stdout."""
    output = tmp_path / "pasta"
    output.mkdir()
    process = run_cli_process(tmp_path, [{}], output_path=output)
    assert process.returncode == 1, process.stderr
    assert process.stdout == ""


def test_my_cli_blank_lines_and_crlf_are_ignored(tmp_path):
    """Linhas em branco e fim de linha Windows (CRLF) não viram reservas."""
    path = write_rows(tmp_path / "base.csv", [{"reservation_id": "R-1"}, {"reservation_id": "R-2"}])
    content = path.read_text(encoding="utf-8").replace("\n", "\r\n\r\n")
    process = run_cli_process(tmp_path, input_bytes=content.encode(), output_path=tmp_path / "report.json")
    assert process.returncode == 0, process.stderr
    assert process.stdout.startswith("Reservas: 2 |")
